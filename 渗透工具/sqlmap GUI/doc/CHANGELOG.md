# Version 1.0 (upcoming)

* Implemented support for automatic decoding of page content through detected charset.
* Implemented mechanism for proper data dumping on DBMSes not supporting `LIMIT/OFFSET` like mechanism(s) (e.g. Microsoft SQL Server, Sybase, etc.).
* Major improvements to program stabilization based on user reports.
* Added new tampering scripts avoiding popular WAF/IPS/IDS mechanisms.
* Added support for setting Tor proxy type together with port.
* Fixed major bug with DNS leaking in Tor mode.
* Added wordlist compilation made of the most popular cracking dictionaries.
* Added support for mnemonics substantially helping user with program setup.
* Implemented multi-processor hash cracking routine(s) on Linux OS.
* Implemented advanced detection techniques for inband and time-based injections by usage of standard deviation method.
* Old resume files are now deprecated and replaced by faster SQLite based session mechanism.
* Substantial code optimization and smaller memory footprint.
* Added option `-m` for scanning multiple targets enlisted in a given textual file.
* Added option `--randomize` for randomly changing value of a given parameter(s) based on it's original form.
* Added switch `--force-ssl` for forcing usage of SSL/HTTPS requests.
* Added option `--host` for manually setting HTTP Host header value.
* Added option `--eval` for evaluating provided Python code (with resulting parameter values) right before the request itself.
* Added option `--skip` for skipping tests for given parameter(s).
* Added switch `--titles` for comparing pages based only on their titles.
* Added option `--charset` for forcing character encoding used for data retrieval.
* Added switch `--check-tor` for checking if Tor is used properly.
* Added option `--crawl` for multithreaded crawling of a given website starting from the target url.
* Added option `--csv-del` for manually setting delimiting character used in CSV output.
* Added switch `--hex` for using DBMS hex conversion function(s) for data retrieval.
* Added switch `--smart` for conducting through tests only in case of positive heuristic(s).
* Added switch `--check-waf` for checking of existence of WAF/IPS/IDS protection.
* Added switch `--schema` to enumerate DBMS schema: shows all columns of all databases' tables.
* Added switch `--count` to count the number of entries for a specific table or all database(s) tables.
* Major improvements to switches --tables and --columns.
* Takeover switch --os-pwn improved: stealthier, faster and AV-proof.
* Added switch --mobile to imitate a mobile device through HTTP User-Agent header.

# Version 0.9 (2011-04-10)

* Rewritten SQL injection detection engine.
* Support to directly connect to the database without passing via a SQL injection, option `-d`.
* Added full support for both time-based blind SQL injection and error-based SQL injection techniques.
* Implemented support for SQLite 2 and 3.
* Implemented support for Firebird.
* Implemented support for Microsoft Access, Sybase and SAP MaxDB.
* Extended old `--dump -C` functionality to be able to search for specific database(s), table(s) and column(s), option `--search`.
* Added support to tamper injection data with option `--tamper`.
* Added automatic recognition of password hashes format and support to crack them with a dictionary-based attack.
* Added support to enumerate roles on Oracle, --roles switch.
* Added support for SOAP based web services requests.
* Added support to fetch unicode data.
* Added support to use persistent HTTP(s) connection for speed improvement, switch `--keep-alive`.
* Implemented several optimization switches to speed up the exploitation of SQL injections.
* Support to test and inject against HTTP Referer header.
* Implemented HTTP(s) proxy authentication support, option `--proxy-cred`.
* Implemented feature to speedup the enumeration of table names.
* Support for customizable HTTP(s) redirections.
* Support to replicate the back-end DBMS tables structure and entries in a local SQLite 3 database, switch `--replicate`.
* Support to parse and test forms on target url, switch `--forms`.
* Added switches to brute-force tables names and columns names with a dictionary attack, `--common-tables` and `--common-columns`. Useful for instance when system table `information_schema` is not available on MySQL.
* Basic support for REST-style URL parameters by using the asterisk (`*`) to mark where to test for and exploit SQL injection.
* Added safe URL feature, `--safe-url` and `--safe-freq`.
* Added switch `--text-only` to strip from the HTTP response body the HTML/JS code and compare pages based only on their textual content.
* Implemented few other features and switches.
* Over 100 bugs fixed.
* Major code refactoring.
* User's manual updated.

# Version 0.8 (2010-03-14)

* Support to enumerate and dump all databases' tables containing user provided column(s) by specifying for instance `--dump -C user,pass`. Useful to identify for instance tables containing custom application credentials.
* Support to parse `-C` (column name(s)) when fetching columns of a table with `--columns`: it will enumerate only columns like the provided one(s) within the specified table.
* Support for takeover features on PostgreSQL 8.4.
* Enhanced `--priv-esc` to rely on new Metasploit Meterpreter's 'getsystem' command to elevate privileges of the user running the back-end DBMS instance to SYSTEM on Windows.
* Automatic support in `--os-pwn` to use the web uploader/backdoor to upload and execute the Metasploit payload stager when stacked queries SQL injection is not supported, for instance on MySQL/PHP and MySQL/ASP, but there is a writable folder within the web server document root.
* Fixed web backdoor functionality for `--os-cmd`, `--os-shell` and `--os-pwn` useful when web application does not support stacked queries.
* Added support to properly read (`--read-file`) also binary files via PostgreSQL by injecting sqlmap new `sys_fileread()` user-defined function.
* Updated active fingerprint and comment injection fingerprint for MySQL 5.1, MySQL 5.4 and MySQL 5.5.
* Updated active fingerprint for PostgreSQL 8.4.
* Support for NTLM authentication via python-ntlm third party library, http://code.google.com/p/python-ntlm/, `--auth-type NTLM`.
* Support to automatically decode `deflate`, `gzip` and `x-gzip` HTTP responses.
* Support for Certificate authentication, `--auth-cert` option added.
* Added support for regular expression based scope when parsing Burp or Web Scarab proxy log file (`-l`), `--scope`.
* Added option `-r` to load a single HTTP request from a text file.
* Added switch `--ignore-proxy` to ignore the system default HTTP proxy.
* Added support to ignore Set-Cookie in HTTP responses, `--drop-set-cookie`.
* Added support to specify which Google dork result page to parse, `--gpage` to be used together with `-g`.
* Major bug fix and enhancements to the multi-threading (`--threads`) functionality.
* Fixed URL encoding/decoding of GET/POST parameters and Cookie header.
* Refactored `--update` to use `python-svn` third party library if available or `svn` command to update sqlmap to the latest development version from subversion repository.
* Major bugs fixed.
* Cleanup of UDF source code repository, https://svn.sqlmap.org/sqlmap/trunk/sqlmap/extra/udfhack.
* Major code cleanup.
* Added simple file encryption/compression utility, extra/cloak/cloak.py, used by sqlmap to decrypt on the fly Churrasco, UPX executable and web shells consequently reducing drastically the number of anti-virus softwares that mistakenly mark sqlmap as a malware.
* Updated user's manual.
* Created several demo videos, hosted on YouTube (http://www.youtube.com/user/inquisb) and linked from http://www.sqlmap.org/demo.html.

# Version 0.8 release candidate (2009-09-21)

* Major enhancement to the Microsoft SQL Server stored procedure heap-based buffer overflow exploit (--os-bof) to automatically bypass DEP memory protection.
* Added support for MySQL and PostgreSQL to execute Metasploit shellcode via UDF 'sys_bineval' (in-memory, anti-forensics technique) as an option instead of uploading the standalone payload stager executable.
* Added options for MySQL, PostgreSQL and Microsoft SQL Server to read/add/delete Windows registry keys.
* Added options for MySQL and PostgreSQL to inject custom user-defined functions.
* Added support for --first and --last so the user now has even more granularity in what to enumerate in the query output.
* Minor enhancement to save the session by default in 'output/hostname/session' file if -s option is not specified.
* Minor improvement to automatically remove sqlmap created temporary files from the DBMS underlying file system.
* Minor bugs fixed.
* Major code refactoring.

# Version 0.7 (2009-07-25)

* Adapted Metasploit wrapping functions to work with latest 3.3 development version too.
* Adjusted code to make sqlmap 0.7 to work again on Mac OSX too.
* Reset takeover OOB features (if any of --os-pwn, --os-smbrelay or --os-bof is selected) when running under Windows because msfconsole and msfcli are not supported on the native Windows Ruby interpreter. This make sqlmap 0.7 to work again on Windows too.
* Minor improvement so that sqlmap tests also all parameters with no value (eg. par=).
* HTTPS requests over HTTP proxy now work on either Python 2.4, 2.5 and 2.6+.
* Major bug fix to sql-query/sql-shell features.
* Major bug fix in --read-file option.
* Major silent bug fix to multi-threading functionality.
* Fixed the web backdoor functionality (for MySQL) when (usually) stacked queries are not supported and --os-shell is provided.
* Fixed MySQL 'comment injection' version fingerprint.
* Fixed basic Microsoft SQL Server 2000 fingerprint.
* Many minor bug fixes and code refactoring.

# Version 0.7 release candidate (2009-04-22)

* Added support to execute arbitrary commands on the database server underlying operating system either returning the standard output or not via UDF injection on MySQL and PostgreSQL and via xp_cmdshell() stored procedure on Microsoft SQL Server;
* Added support for out-of-band connection between the attacker box and the database server underlying operating system via stand-alone payload stager created by Metasploit and supporting Meterpreter, shell and VNC payloads for both Windows and Linux;
* Added support for out-of-band connection via Microsoft SQL Server 2000 and 2005 'sp_replwritetovarbin' stored procedure heap-based buffer overflow (MS09-004) exploitation with multi-stage Metasploit payload support;
* Added support for out-of-band connection via SMB reflection attack with UNC path request from the database server to the attacker box by using the Metasploit smb_relay exploit;
* Added support to read and write (upload) both text and binary files on the database server underlying file system for MySQL, PostgreSQL and Microsoft SQL Server;
* Added database process' user privilege escalation via Windows Access Tokens kidnapping on MySQL and Microsoft SQL Server via either Meterpreter's incognito extension or Churrasco stand-alone executable;
* Speed up the inference algorithm by providing the minimum required charset for the query output;
* Major bug fix in the comparison algorithm to correctly handle also the case that the url is stable and the False response changes the page content very little;
* Many minor bug fixes, minor enhancements and layout adjustments.

# Version 0.6.4 (2009-02-03)

* Major enhancement to make the comparison algorithm work properly also on url not stables automatically by using the difflib Sequence Matcher object;
* Major enhancement to support SQL data definition statements, SQL data manipulation statements, etc from user in SQL query and SQL shell if stacked queries are supported by the web application technology;
* Major speed increase in DBMS basic fingerprint;
* Minor enhancement to support an option (--is-dba) to show if the current user is a database management system administrator;
* Minor enhancement to support an option (--union-tech) to specify the technique to use to detect the number of columns used in the web application SELECT statement: NULL bruteforcing (default) or ORDER BY clause bruteforcing;
* Added internal support to forge CASE statements, used only by --is-dba query at the moment;
* Minor layout adjustment to the --update output;
* Increased default timeout to 30 seconds;
* Major bug fix to correctly handle custom SQL "limited" queries on Microsoft SQL Server and Oracle;
* Major bug fix to avoid tracebacks when multiple targets are specified and one of them is not reachable;
* Minor bug fix to make the Partial UNION query SQL injection technique work properly also on Oracle and Microsoft SQL Server;
* Minor bug fix to make the --postfix work even if --prefix is not provided;
* Updated documentation.

# Version 0.6.3 (2008-12-18)

* Major enhancement to get list of targets to test from Burp proxy (http://portswigger.net/suite/) requests log file path or WebScarab proxy (http://www.owasp.org/index.php/Category:OWASP_WebScarab_Project) 'conversations/' folder path by providing option -l <filepath>;
* Major enhancement to support Partial UNION query SQL injection technique too;
* Major enhancement to test if the web application technology supports stacked queries (multiple statements) by providing option --stacked-test which will be then used someday also by takeover functionality;
* Major enhancement to test if the injectable parameter is affected by a time based blind SQL injection technique by providing option --time-test;
* Minor enhancement to fingerprint the web server operating system and the web application technology by parsing some HTTP response headers;
* Minor enhancement to fingerprint the back-end DBMS operating system by parsing the DBMS banner value when -b option is provided;
* Minor enhancement to be able to specify the number of seconds before timeout the connection by providing option --timeout #, default is set to 10 seconds and must be 3 or higher;
* Minor enhancement to be able to specify the number of seconds to wait between each HTTP request by providing option --delay #;
* Minor enhancement to be able to get the injection payload --prefix and --postfix from user;
* Minor enhancement to be able to enumerate table columns and dump table entries, also when the database name is not provided, by using the current database on MySQL and Microsoft SQL Server, the 'public' scheme on PostgreSQL and the 'USERS' TABLESPACE_NAME on Oracle;
* Minor enhancemet to support also --regexp, --excl-str and --excl-reg options rather than only --string when comparing HTTP responses page content;
* Minor enhancement to be able to specify extra HTTP headers by providing option --headers. By default Accept, Accept-Language and Accept-Charset headers are set;
* Minor improvement to be able to provide CU (as current user) as user value (-U) when enumerating users privileges or users passwords;
* Minor improvements to sqlmap Debian package files;
* Minor improvement to use Python psyco (http://psyco.sourceforge.net/) library if available to speed up the sqlmap algorithmic operations;
* Minor improvement to retry the HTTP request up to three times in case an exception is raised during the connection to the target url;
* Major bug fix to correctly enumerate columns on Microsoft SQL Server;
* Major bug fix so that when the user provide a SELECT statement to be processed with an asterisk as columns, now it also work if in the FROM there is no database name specified;
* Minor bug fix to correctly dump table entries when the column is provided;
* Minor bug fix to correctly handle session.error, session.timeout and httplib.BadStatusLine exceptions in HTTP requests;
* Minor bug fix to correctly catch connection exceptions and notify to the user also if they occur within a thread;
* Increased default output level from 0 to 1;
* Updated documentation.

# Version 0.6.2 (2008-11-02)

* Major bug fix to correctly dump tables entries when --stop is not specified;
* Major bug fix so that the users' privileges enumeration now works properly also on both MySQL < 5.0 and MySQL >= 5.0;
* Major bug fix when the request is POST to also send the GET parameters if any have been provided;
* Major bug fix to correctly update sqlmap to the latest stable release with command line --update;
* Major bug fix so that when the expected value of a query (count variable) is an integer and, for some reasons, its resumed value from the session file is a string or a binary file, the query is executed again and its new output saved to the session file;
* Minor bug fix in MySQL comment injection fingerprint technique;
* Minor improvement to correctly enumerate tables, columns and dump tables entries on Oracle and on PostgreSQL when the database name is not 'public' schema or a system database;
* Minor improvement to be able to dump entries on MySQL < 5.0 when database name, table name and column(s) are provided;
* Updated the database management system fingerprint checks to correctly identify MySQL 5.1.x, MySQL 6.0.x and PostgreSQL 8.3;
* More user-friendly warning messages.

# Version 0.6.1 (2008-08-20)

* Major bug fix to blind SQL injection bisection algorithm to handle an exception;
* Added a Metasploit Framework 3 auxiliary module to run sqlmap;
* Implemented possibility to test for and inject also on LIKE statements;
* Implemented --start and --stop options to set the first and the last table entry to dump;
* Added non-interactive/batch-mode (--batch) option to make it easy to wrap sqlmap in Metasploit and any other tool;
* Minor enhancement to save also the length of query output in the session file when retrieving the query output length for ETA or for resume purposes;
* Changed the order sqlmap dump table entries from column by column to row by row. Now it also dumps entries as they are stored in the tables, not forcing the entries' order alphabetically anymore;
* Minor bug fix to correctly handle parameters' value with % character.

# Version 0.6 (2008-09-01)

* Complete code refactor and many bugs fixed;
* Added multithreading support to set the maximum number of concurrent HTTP requests;
* Implemented SQL shell (--sql-shell) functionality and fixed SQL query (--sql-query, before called -e) to be able to run whatever SELECT statement and get its output in both inband and blind SQL injection attack;
* Added an option (--privileges) to retrieve DBMS users privileges, it also notifies if the user is a DBMS administrator;
* Added support (-c) to read options from configuration file, an example of valid INI file is sqlmap.conf and support (--save) to save command line options on a configuration file;
* Created a function that updates the whole sqlmap to the latest stable version available by running sqlmap with --update option;
* Created sqlmap .deb (Debian, Ubuntu, etc.) and .rpm (Fedora, etc.) installation binary packages;
* Created sqlmap .exe (Windows) portable executable;
* Save a lot of more information to the session file, useful when resuming injection on the same target to not loose time on identifying injection, UNION fields and back-end DBMS twice or more times;
* Improved automatic check for parenthesis when testing and forging SQL query vector;
* Now it checks for SQL injection on all GET/POST/Cookie parameters then it lets the user select which parameter to perform the injection on in case that more than one is injectable;
* Implemented support for HTTPS requests over HTTP(S) proxy;
* Added a check to handle NULL or not available queries output;
* More entropy (randomStr() and randomInt() functions in lib/core/common.py) in inband SQL injection concatenated query and in AND condition checks;
* Improved XML files structure;
* Implemented the possibility to change the HTTP Referer header;
* Added support to resume from session file also when running with inband SQL injection attack;
* Added an option (--os-shell) to execute operating system commands if the back-end DBMS is MySQL, the web server has the PHP engine active and permits write access on a directory within the document root;
* Added a check to assure that the provided string to match (--string) is within the page content;
* Fixed various queries in XML file;
* Added LIMIT, ORDER BY and COUNT queries to the XML file and adapted the library to parse it;
* Fixed password fetching function, mainly for Microsoft SQL Server and reviewed the password hashes parsing function;
* Major bug fixed to avoid tracebacks when the testable parameter(s) is dynamic, but not injectable;
* Enhanced logging system: added three more levels of verbosity to show also HTTP sent and received traffic;
* Enhancement to handle Set-Cookie from target url and automatically re-establish the Session when it expires;
* Added support to inject also on Set-Cookie parameters;
* Implemented TAB completion and command history on both --sql-shell and --os-shell;
* Renamed some command line options;
* Added a conversion library;
* Added code schema and reminders for future developments;
* Added Copyright comment and $Id$;
* Updated the command line layout and help messages;
* Updated some docstrings;
* Updated documentation files.

# Version 0.5 (2007-11-04)

* Added support for Oracle database management system
* Extended inband SQL injection functionality (--union-use) to all other possible queries since it only worked with -e and --file on all DMBS plugins;
* Added support to extract database users password hash on Microsoft SQL Server;
* Added a fuzzer function with the aim to parse HTML page looking for standard database error messages consequently improving database fingerprinting;
* Added support for SQL injection on HTTP Cookie and User-Agent headers;
* Reviewed HTTP request library (lib/request.py) to support the extended inband SQL injection functionality. Splitted getValue() into getInband() and getBlind();
* Major enhancements in common library and added checkForBrackets() method to check if the bracket(s) are needed to perform a UNION query SQL injection attack;
* Implemented --dump-all functionality to dump entire DBMS data from all databases tables;
* Added support to exclude DBMS system databases' when enumeration tables and dumping their entries (--exclude-sysdbs);
* Implemented in Dump.dbTableValues() method the CSV file dumped data automatic saving in csv/ folder by default;
* Added DB2, Informix and Sybase DBMS error messages and minor improvements in xml/errors.xml;
* Major improvement in all three DBMS plugins so now sqlmap does not get entire databases' tables structure when all of database/table/ column are specified to be dumped;
* Important fixes in lib/option.py to make sqlmap properly work also with python 2.5 and handle the CSV dump files creation work also under Windows operating system, function __setCSVDir() and fixed also in lib/dump.py;
* Minor enhancement in lib/injection.py to randomize the number requested to test the presence of a SQL injection affected parameter and implemented the possibilities to break (q) the for cycle when using the google dork option (-g);
* Minor fix in lib/request.py to properly encode the url to request in case the "fixed" part of the url has blank spaces;
* More minor layout enhancements in some libraries;
* Renamed DMBS plugins;
* Complete code refactoring, a lot of minor and some major fixes in libraries, many minor improvements;
* Updated all documentation files.

# Version 0.4 (2007-06-15)

* Added DBMS fingerprint based also upon HTML error messages parsing defined in lib/parser.py which reads an XML file defining default error messages for each supported DBMS;
* Added Microsoft SQL Server extensive DBMS fingerprint checks based upon accurate '@@version' parsing matching on an XML file to get also the exact patching level of the DBMS;
* Added support for query ETA (Estimated Time of Arrival) real time calculation (--eta);
* Added support to extract database management system users password hash on MySQL and PostgreSQL (--passwords);
* Added docstrings to all functions, classes and methods, consequently released the sqlmap development documentation <http://www.sqlmap.org/dev/>;
* Implemented Google dorking feature (-g) to take advantage of Google results affected by SQL injection to perform other command line argument on their DBMS;
* Improved logging functionality: passed from banal 'print' to Python native logging library;
* Added support for more than one parameter in '-p' command line option;
* Added support for HTTP Basic and Digest authentication methods (--basic-auth and --digest-auth);
* Added the command line option '--remote-dbms' to manually specify the remote DBMS;
* Major improvements in union.UnionCheck() and union.UnionUse() functions to make it possible to exploit inband SQL injection also with database comment characters ('--' and '#') in UNION query statements;
* Added the possibility to save the output into a file while performing the queries (-o OUTPUTFILE) so it is possible to stop and resume the same query output retrieving in a second time (--resume);
* Added support to specify the database table column to enumerate (-C COL);
* Added inband SQL injection (UNION query) support (--union-use);
* Complete code refactoring, a lot of minor and some major fixes in libraries, many minor improvements;
* Reviewed the directory tree structure;
* Splitted lib/common.py: inband injection functionalities now are moved to lib/union.py;
* Updated documentation files.

# Version 0.3 (2007-01-20)

* Added module for MS SQL Server;
* Strongly improved MySQL dbms active fingerprint and added MySQL comment injection check;
* Added PostgreSQL dbms active fingerprint;
* Added support for string match (--string);
* Added support for UNION check (--union-check);
* Removed duplicated code, delegated most of features to the engine in common.py and option.py;
* Added support for --data command line argument to pass the string for POST requests;
* Added encodeParams() method to encode url parameters before making http request;
* Many bug fixes;
* Rewritten documentation files;
* Complete code restyling.

# Version 0.2 (2006-12-13)

* complete refactor of entire program;
* added TODO and THANKS files;
* added some papers references in README file;
* moved headers to user-agents.txt, now -f parameter specifies a file (user-agents.txt) and randomize the selection of User-Agent header;
* strongly improved program plugins (mysqlmap.py and postgres.py), major enhancements: * improved active mysql fingerprint check_dbms(); * improved enumeration functions for both databases; * minor changes in the unescape() functions;
* replaced old inference algorithm with a new bisection algorithm.
* reviewed command line parameters, now with -p it's possible to specify the parameter you know it's vulnerable to sql injection, this way the script won't perform the sql injection checks itself; removed the TOKEN parameter;
* improved Common class, adding support for http proxy and http post method in hash_page;
* added OptionCheck class in option.py which performs all needed checks on command line parameters and values;
* added InjectionCheck class in injection.py which performs check on url stability, dynamics of parameters and injection on dynamic url parameters;
* improved output methods in dump.py;
* layout enhancement on main program file (sqlmap.py), adapted to call new option/injection classes and improvements on catching of exceptions.
