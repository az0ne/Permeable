#!/usr/bin/env python

"""
Copyright (c) 2006-2012 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import cookielib
import inspect
import logging
import os
import re
import socket
import string
import sys
import threading
import urllib2
import urlparse

import lib.core.common
import lib.core.threads
import lib.core.convert

from lib.controller.checks import checkConnection
from lib.core.common import Backend
from lib.core.common import boldifyMessage
from lib.core.common import dataToStdout
from lib.core.common import getPublicTypeMembers
from lib.core.common import extractRegexResult
from lib.core.common import filterStringValue
from lib.core.common import findPageForms
from lib.core.common import getConsoleWidth
from lib.core.common import getFileItems
from lib.core.common import getFileType
from lib.core.common import getUnicode
from lib.core.common import isListLike
from lib.core.common import normalizePath
from lib.core.common import ntToPosixSlashes
from lib.core.common import openFile
from lib.core.common import parseTargetDirect
from lib.core.common import parseTargetUrl
from lib.core.common import paths
from lib.core.common import randomRange
from lib.core.common import randomStr
from lib.core.common import readInput
from lib.core.common import resetCookieJar
from lib.core.common import runningAsAdmin
from lib.core.common import sanitizeStr
from lib.core.common import setOptimize
from lib.core.common import singleTimeWarnMessage
from lib.core.common import UnicodeRawConfigParser
from lib.core.common import urldecode
from lib.core.common import urlencode
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import queries
from lib.core.datatype import AttribDict
from lib.core.datatype import InjectionDict
from lib.core.defaults import defaults
from lib.core.dicts import DBMS_DICT
from lib.core.dicts import DUMP_REPLACEMENTS
from lib.core.enums import ADJUST_TIME_DELAY
from lib.core.enums import CUSTOM_LOGGING
from lib.core.enums import DUMP_FORMAT
from lib.core.enums import HTTPHEADER
from lib.core.enums import HTTPMETHOD
from lib.core.enums import MOBILES
from lib.core.enums import PAYLOAD
from lib.core.enums import PRIORITY
from lib.core.enums import PROXY_TYPE
from lib.core.enums import REFLECTIVE_COUNTER
from lib.core.enums import WIZARD
from lib.core.exception import SqlmapConnectionException
from lib.core.exception import SqlmapFilePathException
from lib.core.exception import SqlmapGenericException
from lib.core.exception import SqlmapMissingDependence
from lib.core.exception import SqlmapMissingMandatoryOptionException
from lib.core.exception import SqlmapMissingPrivileges
from lib.core.exception import SqlmapSilentQuitException
from lib.core.exception import SqlmapSyntaxException
from lib.core.exception import SqlmapUnsupportedDBMSException
from lib.core.exception import SqlmapUserQuitException
from lib.core.log import FORMATTER
from lib.core.log import LOGGER_HANDLER
from lib.core.optiondict import optDict
from lib.core.purge import purge
from lib.core.settings import ACCESS_ALIASES
from lib.core.settings import BURP_REQUEST_REGEX
from lib.core.settings import CODECS_LIST_PAGE
from lib.core.settings import CRAWL_EXCLUDE_EXTENSIONS
from lib.core.settings import CUSTOM_INJECTION_MARK_CHAR
from lib.core.settings import DB2_ALIASES
from lib.core.settings import DEFAULT_GET_POST_DELIMITER
from lib.core.settings import DEFAULT_PAGE_ENCODING
from lib.core.settings import DEFAULT_TOR_HTTP_PORTS
from lib.core.settings import DEFAULT_TOR_SOCKS_PORT
from lib.core.settings import FIREBIRD_ALIASES
from lib.core.settings import INJECT_HERE_MARK
from lib.core.settings import IS_WIN
from lib.core.settings import LOCALHOST
from lib.core.settings import MAXDB_ALIASES
from lib.core.settings import MAX_NUMBER_OF_THREADS
from lib.core.settings import MSSQL_ALIASES
from lib.core.settings import MYSQL_ALIASES
from lib.core.settings import NULL
from lib.core.settings import ORACLE_ALIASES
from lib.core.settings import PARAMETER_SPLITTING_REGEX
from lib.core.settings import PGSQL_ALIASES
from lib.core.settings import PYVERSION
from lib.core.settings import SITE
from lib.core.settings import SQLITE_ALIASES
from lib.core.settings import SUPPORTED_DBMS
from lib.core.settings import SUPPORTED_OS
from lib.core.settings import SYBASE_ALIASES
from lib.core.settings import TIME_DELAY_CANDIDATES
from lib.core.settings import UNENCODED_ORIGINAL_VALUE
from lib.core.settings import UNION_CHAR_REGEX
from lib.core.settings import UNKNOWN_DBMS_VERSION
from lib.core.settings import URI_INJECTABLE_REGEX
from lib.core.settings import VERSION_STRING
from lib.core.settings import WEBSCARAB_SPLITTER
from lib.core.threads import getCurrentThreadData
from lib.core.update import update
from lib.parse.configfile import configFileParser
from lib.parse.payloads import loadPayloads
from lib.request.basic import checkCharEncoding
from lib.request.connect import Connect as Request
from lib.request.dns import DNSServer
from lib.request.proxy import ProxyHTTPSHandler
from lib.request.basicauthhandler import SmartHTTPBasicAuthHandler
from lib.request.certhandler import HTTPSCertAuthHandler
from lib.request.httpshandler import HTTPSHandler
from lib.request.rangehandler import HTTPRangeHandler
from lib.request.redirecthandler import SmartRedirectHandler
from lib.request.templates import getPageTemplate
from lib.utils.crawler import Crawler
from lib.utils.deps import checkDependencies
from lib.utils.google import Google
from thirdparty.colorama.initialise import init as coloramainit
from thirdparty.keepalive import keepalive
from thirdparty.oset.pyoset import oset
from thirdparty.socks import socks
from xml.etree.ElementTree import ElementTree

authHandler = urllib2.BaseHandler()
httpsHandler = HTTPSHandler()
keepAliveHandler = keepalive.HTTPHandler()
proxyHandler = urllib2.BaseHandler()
redirectHandler = SmartRedirectHandler()
rangeHandler = HTTPRangeHandler()

def _urllib2Opener():
    """
    This function creates the urllib2 OpenerDirector.
    """

    debugMsg = "creating HTTP requests opener object"
    logger.debug(debugMsg)

    handlers = [proxyHandler, authHandler, redirectHandler, rangeHandler, httpsHandler]

    if not conf.dropSetCookie:
        if not conf.loadCookies:
            conf.cj = cookielib.CookieJar()
        else:
            conf.cj = cookielib.MozillaCookieJar()
            resetCookieJar(conf.cj)

        handlers.append(urllib2.HTTPCookieProcessor(conf.cj))

    # Reference: http://www.w3.org/Protocols/rfc2616/rfc2616-sec8.html
    if conf.keepAlive:
        warnMsg = "persistent HTTP(s) connections, Keep-Alive, has "
        warnMsg += "been disabled because of its incompatibility "

        if conf.proxy:
            warnMsg += "with HTTP(s) proxy"
            logger.warn(warnMsg)
        elif conf.aType:
            warnMsg += "with authentication methods"
            logger.warn(warnMsg)
        else:
            handlers.append(keepAliveHandler)

    opener = urllib2.build_opener(*handlers)
    urllib2.install_opener(opener)

def _feedTargetsDict(reqFile, addedTargetUrls):
    """
    Parses web scarab and burp logs and adds results to the target url list
    """

    def _parseWebScarabLog(content):
        """
        Parses web scarab logs (POST method not supported)
        """

        reqResList = content.split(WEBSCARAB_SPLITTER)

        for request in reqResList:
            url = extractRegexResult(r"URL: (?P<result>.+?)\n", request, re.I)
            method = extractRegexResult(r"METHOD: (?P<result>.+?)\n", request, re.I)
            cookie = extractRegexResult(r"COOKIE: (?P<result>.+?)\n", request, re.I)

            if not method or not url:
                logger.debug("not a valid WebScarab log data")
                continue

            if method.upper() == HTTPMETHOD.POST:
                warnMsg = "POST requests from WebScarab logs aren't supported "
                warnMsg += "as their body content is stored in separate files. "
                warnMsg += "Nevertheless you can use -r to load them individually."
                logger.warning(warnMsg)
                continue

            if not(conf.scope and not re.search(conf.scope, url, re.I)):
                if not kb.targets or url not in addedTargetUrls:
                    kb.targets.add((url, method, None, cookie))
                    addedTargetUrls.add(url)

    def _parseBurpLog(content):
        """
        Parses burp logs
        """

        if not re.search(BURP_REQUEST_REGEX, content, re.I | re.S):
            reqResList = [content]
        else:
            reqResList = re.finditer(BURP_REQUEST_REGEX, content, re.I | re.S)

        for match in reqResList:
            request = match if isinstance(match, basestring) else match.group(0)

            schemePort = re.search(r"(http[\w]*)\:\/\/.*?\:([\d]+).+?={10,}", request, re.I | re.S)

            if schemePort:
                scheme = schemePort.group(1)
                port = schemePort.group(2)
            else:
                scheme, port = None, None

            if not re.search (r"^[\n]*(GET|POST).*?\sHTTP\/", request, re.I | re.M):
                continue

            if re.search(r"^[\n]*(GET|POST).*?\.(%s)\sHTTP\/" % "|".join(CRAWL_EXCLUDE_EXTENSIONS), request, re.I | re.M):
                continue

            getPostReq = False
            url = None
            host = None
            method = None
            data = None
            cookie = None
            params = False
            lines = request.split("\n")

            for line in lines:
                if len(line) == 0 or line == "\n":
                    if method == HTTPMETHOD.POST and data is None:
                        data = ""
                        params = True

                elif (line.startswith("GET ") or line.startswith("POST ")) and " HTTP/" in line:
                    if line.startswith("GET "):
                        index = 4
                    else:
                        index = 5

                    url = line[index:line.index(" HTTP/")]
                    method = line[:index-1]

                    if "?" in line and "=" in line:
                        params = True

                    getPostReq = True

                # POST parameters
                elif data is not None and params:
                    data += "%s%s" % ("\n" if data else "", line)

                # GET parameters
                elif "?" in line and "=" in line and ": " not in line:
                    params = True

                # Headers
                elif re.search(r"\A\S+: ", line):
                    key, value = line.split(": ", 1)

                    # Cookie and Host headers
                    if key.lower() == "cookie":
                        cookie = value
                    elif key.lower() == "host":
                        if '://' in value:
                            scheme, value = value.split('://')[:2]
                        splitValue = value.split(":")
                        host = splitValue[0]

                        if len(splitValue) > 1:
                            port = filterStringValue(splitValue[1], '[0-9]')

                    # Avoid to add a static content length header to
                    # conf.httpHeaders and consider the following lines as
                    # POSTed data
                    if key == HTTPHEADER.CONTENT_LENGTH:
                        params = True

                    # Avoid proxy and connection type related headers
                    elif key not in ( HTTPHEADER.PROXY_CONNECTION, HTTPHEADER.CONNECTION ):
                        conf.httpHeaders.append((getUnicode(key), getUnicode(value)))

            if getPostReq and (params or cookie):
                if not port and isinstance(scheme, basestring) and scheme.lower() == "https":
                    port = "443"
                elif not scheme and port == "443":
                    scheme = "https"

                if conf.forceSSL:
                    scheme = "https"
                    port = port or "443"

                if not url.startswith("http"):
                    url = "%s://%s:%s%s" % (scheme or "http", host, port or "80", url)
                    scheme = None
                    port = None

                if not(conf.scope and not re.search(conf.scope, url, re.I)):
                    if not kb.targets or url not in addedTargetUrls:
                        kb.targets.add((url, method, urldecode(data) if data and urlencode(DEFAULT_GET_POST_DELIMITER, None) not in data else data, cookie))
                        addedTargetUrls.add(url)

    fp = openFile(reqFile, "rb")

    content = fp.read()
    content = content.replace("\r", "")

    if conf.scope:
        logger.info("using regular expression '%s' for filtering targets" % conf.scope)

    _parseBurpLog(content)
    _parseWebScarabLog(content)

def _loadQueries():
    """
    Loads queries from 'xml/queries.xml' file.
    """

    def iterate(node, retVal=None):
        class DictObject(object):
            def __init__(self):
                self.__dict__ = {}
            def __contains__(self, name):
                return name in self.__dict__

        if retVal is None:
            retVal = DictObject()

        for child in node.findall("*"):
            instance = DictObject()
            retVal.__dict__[child.tag] = instance
            if child.attrib:
                instance.__dict__.update(child.attrib)
            else:
                iterate(child, instance)

        return retVal

    tree = ElementTree()
    tree.parse(paths.QUERIES_XML)

    for node in tree.findall("*"):
        queries[node.attrib['value']] = iterate(node)

def _setMultipleTargets():
    """
    Define a configuration parameter if we are running in multiple target
    mode.
    """

    initialTargetsCount = len(kb.targets)
    addedTargetUrls = set()

    if not conf.logFile:
        return

    debugMsg = "parsing targets list from '%s'" % conf.logFile
    logger.debug(debugMsg)

    if not os.path.exists(conf.logFile):
        errMsg = "the specified list of targets does not exist"
        raise SqlmapFilePathException, errMsg

    if os.path.isfile(conf.logFile):
        _feedTargetsDict(conf.logFile, addedTargetUrls)

    elif os.path.isdir(conf.logFile):
        files = os.listdir(conf.logFile)
        files.sort()

        for reqFile in files:
            if not re.search("([\d]+)\-request", reqFile):
                continue

            _feedTargetsDict(os.path.join(conf.logFile, reqFile), addedTargetUrls)

    else:
        errMsg = "the specified list of targets is not a file "
        errMsg += "nor a directory"
        raise SqlmapFilePathException, errMsg

    updatedTargetsCount = len(kb.targets)

    if updatedTargetsCount > initialTargetsCount:
        infoMsg = "sqlmap parsed %d " % (updatedTargetsCount - initialTargetsCount)
        infoMsg += "testable requests from the targets list"
        logger.info(infoMsg)

def _adjustLoggingFormatter():
    """
    Solves problem of line deletition caused by overlapping logging messages
    and retrieved data info in inference mode
    """

    if hasattr(FORMATTER, '_format'):
        return

    def format(record):
        _ = boldifyMessage(FORMATTER._format(record))
        if kb.prependFlag:
            _ = "\n%s" % _
            kb.prependFlag = False
        return _

    FORMATTER._format = FORMATTER.format
    FORMATTER.format = format

def _setRequestFromFile():
    """
    This function checks if the way to make a HTTP request is through supplied
    textual file, parses it and saves the information into the knowledge base.
    """

    if not conf.requestFile:
        return

    addedTargetUrls = set()

    conf.requestFile = os.path.expanduser(conf.requestFile)

    infoMsg = "parsing HTTP request from '%s'" % conf.requestFile
    logger.info(infoMsg)

    if not os.path.isfile(conf.requestFile):
        errMsg = "the specified HTTP request file "
        errMsg += "does not exist"
        raise SqlmapFilePathException, errMsg

    _feedTargetsDict(conf.requestFile, addedTargetUrls)

def _setCrawler():
    if not conf.crawlDepth:
        return

    crawler = Crawler()
    crawler.getTargetUrls()

def _setGoogleDorking():
    """
    This function checks if the way to request testable hosts is through
    Google dorking then requests to Google the search parameter, parses
    the results and save the testable hosts into the knowledge base.
    """

    if not conf.googleDork:
        return

    global keepAliveHandler
    global proxyHandler

    debugMsg = "initializing Google dorking requests"
    logger.debug(debugMsg)

    infoMsg = "first request to Google to get the session cookie"
    logger.info(infoMsg)

    handlers = [ proxyHandler ]

    # Reference: http://www.w3.org/Protocols/rfc2616/rfc2616-sec8.html
    if conf.keepAlive:
        if conf.proxy:
            warnMsg = "persistent HTTP(s) connections, Keep-Alive, has "
            warnMsg += "been disabled because of its incompatibility "
            warnMsg += "with HTTP(s) proxy"
            logger.warn(warnMsg)
        else:
            handlers.append(keepAliveHandler)

    googleObj = Google(handlers)
    kb.data.onlyGETs = None

    def retrieve():
        links = googleObj.search(conf.googleDork)

        if not links:
            errMsg = "unable to find results for your "
            errMsg += "Google dork expression"
            raise SqlmapGenericException, errMsg

        for link in links:
            link = urldecode(link)
            if re.search(r"(.*?)\?(.+)", link):
                kb.targets.add((link, conf.method, conf.data, conf.cookie))
            elif re.search(URI_INJECTABLE_REGEX, link, re.I):
                if kb.data.onlyGETs is None and conf.data is None:
                    message = "do you want to scan only results containing GET parameters? [Y/n] "
                    test = readInput(message, default="Y")
                    kb.data.onlyGETs = test.lower() != 'n'
                if not kb.data.onlyGETs:
                    kb.targets.add((link, conf.method, conf.data, conf.cookie))

        return links

    while True:
        links = retrieve()

        if kb.targets:
            infoMsg = "sqlmap got %d results for your " % len(links)
            infoMsg += "Google dork expression, "

            if len(links) == len(kb.targets):
                infoMsg += "all "
            else:
                infoMsg += "%d " % len(kb.targets)

            infoMsg += "of them are testable targets"
            logger.info(infoMsg)
            break

        else:
            message = "sqlmap got %d results " % len(links)
            message += "for your Google dork expression, but none of them "
            message += "have GET parameters to test for SQL injection. "
            message += "Do you want to skip to the next result page? [Y/n]"
            test = readInput(message, default="Y")

            if test[0] in ("n", "N"):
                raise SqlmapSilentQuitException
            else:
                conf.googlePage += 1

def _setBulkMultipleTargets():
    if not conf.bulkFile:
        return

    conf.bulkFile = os.path.expanduser(conf.bulkFile)

    infoMsg = "parsing multiple targets list from '%s'" % conf.bulkFile
    logger.info(infoMsg)

    if not os.path.isfile(conf.bulkFile):
        errMsg = "the specified bulk file "
        errMsg += "does not exist"
        raise SqlmapFilePathException, errMsg

    for line in getFileItems(conf.bulkFile):
        if re.search(r"[^ ]+\?(.+)", line, re.I):
            kb.targets.add((line.strip(), None, None, None))

def _findPageForms():
    if not conf.forms or conf.crawlDepth:
        return

    if not checkConnection():
        return

    infoMsg = "searching for forms"
    logger.info(infoMsg)

    page, _ = Request.queryPage(content=True)

    findPageForms(page, conf.url, True, True)

def _setDBMSAuthentication():
    """
    Check and set the DBMS authentication credentials to run statements as
    another user, not the session user
    """

    if not conf.dbmsCred:
        return

    debugMsg = "setting the DBMS authentication credentials"
    logger.debug(debugMsg)

    match = re.search("^(.+?):(.*?)$", conf.dbmsCred)

    if not match:
        errMsg = "DBMS authentication credentials value must be in format "
        errMsg += "username:password"
        raise SqlmapSyntaxException, errMsg

    conf.dbmsUsername = match.group(1)
    conf.dbmsPassword = match.group(2)

def _setMetasploit():
    if not conf.osPwn and not conf.osSmb and not conf.osBof:
        return

    debugMsg = "setting the takeover out-of-band functionality"
    logger.debug(debugMsg)

    msfEnvPathExists = False

    if IS_WIN:
        if not conf.msfPath:
            def _(key, value):
                retVal = None
                try:
                    from  _winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE
                    _ = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
                    _ = OpenKey(_, key)
                    retVal = QueryValueEx(_, value)[0]
                except Exception, ex:
                    print ex
                return retVal

            conf.msfPath = _(r"SOFTWARE\Rapid7\Metasploit", "Location")
            if conf.msfPath:
                conf.msfPath = os.path.join(conf.msfPath, "msf3")

    if conf.osSmb:
        isAdmin = runningAsAdmin()

        if not isAdmin:
            errMsg = "you need to run sqlmap as an administrator "
            errMsg += "if you want to perform a SMB relay attack because "
            errMsg += "it will need to listen on a user-specified SMB "
            errMsg += "TCP port for incoming connection attempts"
            raise SqlmapMissingPrivileges, errMsg

    if conf.msfPath:
        for path in (conf.msfPath, os.path.join(conf.msfPath, "bin")):
            if all(os.path.exists(normalizePath(os.path.join(path, _))) for _ in ("", "msfcli", "msfconsole", "msfencode", "msfpayload")):
                msfEnvPathExists = True
                conf.msfPath = path
                break

        if msfEnvPathExists:
            debugMsg = "provided Metasploit Framework path "
            debugMsg += "'%s' is valid" % conf.msfPath
            logger.debug(debugMsg)
        else:
            warnMsg = "the provided Metasploit Framework path "
            warnMsg += "'%s' is not valid. The cause could " % conf.msfPath
            warnMsg += "be that the path does not exists or that one "
            warnMsg += "or more of the needed Metasploit executables "
            warnMsg += "within msfcli, msfconsole, msfencode and "
            warnMsg += "msfpayload do not exist"
            logger.warn(warnMsg)
    else:
        warnMsg = "you did not provide the local path where Metasploit "
        warnMsg += "Framework is installed"
        logger.warn(warnMsg)

    if not msfEnvPathExists:
        warnMsg = "sqlmap is going to look for Metasploit Framework "
        warnMsg += "installation into the environment paths"
        logger.warn(warnMsg)

        envPaths = os.environ.get("PATH", "").split(";" if IS_WIN else ":")

        for envPath in envPaths:
            envPath = envPath.replace(";", "")

            if all(os.path.exists(normalizePath(os.path.join(envPath, _))) for _ in ("", "msfcli", "msfconsole", "msfencode", "msfpayload")):
                infoMsg = "Metasploit Framework has been found "
                infoMsg += "installed in the '%s' path" % envPath
                logger.info(infoMsg)

                msfEnvPathExists = True
                conf.msfPath = envPath

                break

    if not msfEnvPathExists:
        errMsg = "unable to locate Metasploit Framework installation. "
        errMsg += "Get it from http://metasploit.com/framework/download/"
        raise SqlmapFilePathException, errMsg

def _setWriteFile():
    if not conf.wFile:
        return

    debugMsg = "setting the write file functionality"
    logger.debug(debugMsg)

    if not os.path.exists(conf.wFile):
        errMsg = "the provided local file '%s' does not exist" % conf.wFile
        raise SqlmapFilePathException, errMsg

    if not conf.dFile:
        errMsg = "you did not provide the back-end DBMS absolute path "
        errMsg += "where you want to write the local file '%s'" % conf.wFile
        raise SqlmapMissingMandatoryOptionException, errMsg

    conf.wFileType = getFileType(conf.wFile)

def _setOS():
    """
    Force the back-end DBMS operating system option.
    """

    if not conf.os:
        return

    if conf.os.lower() not in SUPPORTED_OS:
        errMsg = "you provided an unsupported back-end DBMS operating "
        errMsg += "system. The supported DBMS operating systems for OS "
        errMsg += "and file system access are %s. " % ', '.join([o.capitalize() for o in SUPPORTED_OS])
        errMsg += "If you do not know the back-end DBMS underlying OS, "
        errMsg += "do not provide it and sqlmap will fingerprint it for "
        errMsg += "you."
        raise SqlmapUnsupportedDBMSException, errMsg

    debugMsg = "forcing back-end DBMS operating system to user defined "
    debugMsg += "value '%s'" % conf.os
    logger.debug(debugMsg)

    Backend.setOs(conf.os)

def _setTechnique():
    validTechniques = sorted(getPublicTypeMembers(PAYLOAD.TECHNIQUE), key=lambda x: x[1])
    validLetters = map(lambda x: x[0][0].upper(), validTechniques)

    if conf.tech and isinstance(conf.tech, basestring):
        _ = []

        for letter in conf.tech.upper():
            if letter not in validLetters:
                errMsg = "value for --technique must be a string composed "
                errMsg += "by the letters %s. Refer to the " % ", ".join(validLetters)
                errMsg += "user's manual for details"
                raise SqlmapSyntaxException, errMsg

            for validTech, validInt in validTechniques:
                if letter == validTech[0]:
                    _.append(validInt)
                    break

        conf.tech = _

def _setDBMS():
    """
    Force the back-end DBMS option.
    """

    if not conf.dbms:
        return

    debugMsg = "forcing back-end DBMS to user defined value"
    logger.debug(debugMsg)

    conf.dbms = conf.dbms.lower()
    regex = re.search("%s ([\d\.]+)" % ("(%s)" % "|".join([alias for alias in SUPPORTED_DBMS])), conf.dbms, re.I)

    if regex:
        conf.dbms = regex.group(1)
        Backend.setVersion(regex.group(2))

    if conf.dbms not in SUPPORTED_DBMS:
        errMsg = "you provided an unsupported back-end database management "
        errMsg += "system. The supported DBMS are %s. " % ', '.join([d for d in DBMS_DICT])
        errMsg += "If you do not know the back-end DBMS, do not provide "
        errMsg += "it and sqlmap will fingerprint it for you."
        raise SqlmapUnsupportedDBMSException, errMsg

    for aliases in (MSSQL_ALIASES, MYSQL_ALIASES, PGSQL_ALIASES, ORACLE_ALIASES, \
                    SQLITE_ALIASES, ACCESS_ALIASES, FIREBIRD_ALIASES, \
                    MAXDB_ALIASES, SYBASE_ALIASES, DB2_ALIASES):
        if conf.dbms in aliases:
            conf.dbms = aliases[0]

            break

def _setTamperingFunctions():
    """
    Loads tampering functions from given script(s)
    """

    if conf.tamper:
        last_priority = PRIORITY.HIGHEST
        check_priority = True
        resolve_priorities = False
        priorities = []

        for tfile in re.split(PARAMETER_SPLITTING_REGEX, conf.tamper):
            found = False

            tfile = tfile.strip()

            if not tfile:
                continue

            elif os.path.exists(os.path.join(paths.SQLMAP_TAMPER_PATH, tfile if tfile.endswith('.py') else "%s.py" % tfile)):
                tfile = os.path.join(paths.SQLMAP_TAMPER_PATH, tfile if tfile.endswith('.py') else "%s.py" % tfile)

            elif not os.path.exists(tfile):
                errMsg = "tamper script '%s' does not exist" % tfile
                raise SqlmapFilePathException, errMsg

            elif not tfile.endswith('.py'):
                errMsg = "tamper script '%s' should have an extension '.py'" % tfile
                raise SqlmapSyntaxException, errMsg

            dirname, filename = os.path.split(tfile)
            dirname = os.path.abspath(dirname)

            infoMsg = "loading tamper script '%s'" % filename[:-3]
            logger.info(infoMsg)

            if not os.path.exists(os.path.join(dirname, '__init__.py')):
                errMsg = "make sure that there is an empty file '__init__.py' "
                errMsg += "inside of tamper scripts directory '%s'" % dirname
                raise SqlmapGenericException, errMsg

            if dirname not in sys.path:
                sys.path.insert(0, dirname)

            try:
                module = __import__(filename[:-3])
            except ImportError, msg:
                raise SqlmapSyntaxException, "cannot import tamper script '%s' (%s)" % (filename[:-3], msg)

            priority = PRIORITY.NORMAL if not hasattr(module, '__priority__') else module.__priority__

            for name, function in inspect.getmembers(module, inspect.isfunction):
                if name == "tamper":
                    found = True
                    kb.tamperFunctions.append(function)
                    function.func_name = module.__name__

                    if check_priority and priority > last_priority:
                        message = "it seems that you might have mixed "
                        message += "the order of tamper scripts. "
                        message += "Do you want to auto resolve this? [Y/n/q] "
                        test = readInput(message, default="Y")

                        if not test or test[0] in ("y", "Y"):
                            resolve_priorities = True
                        elif test[0] in ("n", "N"):
                            resolve_priorities = False
                        elif test[0] in ("q", "Q"):
                            raise SqlmapUserQuitException

                        check_priority = False

                    priorities.append((priority, function))
                    last_priority = priority

                    break
                elif name == "dependencies":
                    function()

            if not found:
                errMsg = "missing function 'tamper(payload, headers)' "
                errMsg += "in tamper script '%s'" % tfile
                raise SqlmapGenericException, errMsg

        if resolve_priorities and priorities:
            priorities.sort(reverse=True)
            kb.tamperFunctions = []

            for _, function in priorities:
                kb.tamperFunctions.append(function)

def _setThreads():
    if not isinstance(conf.threads, int) or conf.threads <= 0:
        conf.threads = 1

def _setDNSCache():
    """
    Makes a cached version of socket._getaddrinfo to avoid subsequent DNS requests.
    """

    def _getaddrinfo(*args, **kwargs):
        if args in kb.cache:
            return kb.cache[args]

        else:
            kb.cache[args] = socket._getaddrinfo(*args, **kwargs)
            return kb.cache[args]

    if not hasattr(socket, '_getaddrinfo'):
        socket._getaddrinfo = socket.getaddrinfo
        socket.getaddrinfo = _getaddrinfo

def _setHTTPProxy():
    """
    Check and set the HTTP proxy to pass by all HTTP requests.
    """

    global proxyHandler

    if not conf.proxy:
        if conf.hostname in ('localhost', '127.0.0.1') or conf.ignoreProxy:
            proxyHandler = urllib2.ProxyHandler({})

        return

    debugMsg = "setting the HTTP/SOCKS proxy to pass by all HTTP requests"
    logger.debug(debugMsg)

    proxySplit = urlparse.urlsplit(conf.proxy)
    hostnamePort = proxySplit[1].split(":")

    scheme = proxySplit[0].upper()
    hostname = hostnamePort[0]
    port = None
    username = None
    password = None

    if len(hostnamePort) == 2:
        try:
            port = int(hostnamePort[1])
        except:
            pass #drops into the next check block

    if not all((scheme, hasattr(PROXY_TYPE, scheme), hostname, port)):
        errMsg = "proxy value must be in format '(%s)://url:port'" % "|".join(_[0].lower() for _ in getPublicTypeMembers(PROXY_TYPE))
        raise SqlmapSyntaxException, errMsg

    if conf.pCred:
        _ = re.search("^(.*?):(.*?)$", conf.pCred)
        if not _:
            errMsg = "Proxy authentication credentials "
            errMsg += "value must be in format username:password"
            raise SqlmapSyntaxException, errMsg
        else:
            username = _.group(1)
            password = _.group(2)

    if scheme in (PROXY_TYPE.SOCKS4, PROXY_TYPE.SOCKS5):
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 if scheme == PROXY_TYPE.SOCKS5 else socks.PROXY_TYPE_SOCKS4, hostname, port, username=username, password=password)
        socks.wrapmodule(urllib2)
    else:
        if conf.pCred:
            # Reference: http://stackoverflow.com/questions/34079/how-to-specify-an-authenticated-proxy-for-a-python-http-connection
            proxyString = "%s@" % conf.pCred
        else:
            proxyString = ""

        proxyString += "%s:%d" % (hostname, port)

        # Workaround for http://bugs.python.org/issue1424152 (urllib/urllib2:
        # HTTPS over (Squid) Proxy fails) as long as HTTP over SSL requests
        # can't be tunneled over an HTTP proxy natively by Python (<= 2.5)
        # urllib2 standard library
        if PYVERSION >= "2.6":
            proxyHandler = urllib2.ProxyHandler({"http": proxyString, "https": proxyString})
        elif conf.scheme == "https":
            proxyHandler = ProxyHTTPSHandler(proxyString)
        else:
            proxyHandler = urllib2.ProxyHandler({"http": proxyString})

def _setSafeUrl():
    """
    Check and set the safe URL options.
    """
    if not conf.safUrl:
        return

    if not re.search("^http[s]*://", conf.safUrl):
        if ":443/" in conf.safUrl:
            conf.safUrl = "https://" + conf.safUrl
        else:
            conf.safUrl = "http://" + conf.safUrl

    if conf.saFreq <= 0:
        errMsg = "please provide a valid value (>0) for safe frequency (--safe-freq) while using safe url feature"
        raise SqlmapSyntaxException, errMsg

def _setPrefixSuffix():
    if conf.prefix is not None and conf.suffix is not None:
        # Create a custom boundary object for user's supplied prefix
        # and suffix
        boundary = AttribDict()

        boundary.level = 1
        boundary.clause = [ 0 ]
        boundary.where = [ 1, 2, 3 ]
        boundary.prefix = conf.prefix
        boundary.suffix = conf.suffix

        if " like" in boundary.suffix.lower():
            if "'" in boundary.suffix.lower():
                boundary.ptype = 3
            elif '"' in boundary.suffix.lower():
                boundary.ptype = 5
        elif "'" in boundary.suffix:
            boundary.ptype = 2
        elif '"' in boundary.suffix:
            boundary.ptype = 4
        else:
            boundary.ptype = 1

        # user who provides --prefix/--suffix does not want other boundaries
        # to be tested for
        conf.boundaries = [ boundary ]

def _setAuthCred():
    """
    Adds authentication credentials (if any) for current target to the password manager
    (used by connection handler)
    """

    if kb.passwordMgr:
        kb.passwordMgr.add_password(None, "%s://%s" % (conf.scheme, conf.hostname), conf.authUsername, conf.authPassword)

def _setHTTPAuthentication():
    """
    Check and set the HTTP(s) authentication method (Basic, Digest, NTLM or Certificate),
    username and password for first three methods, or key file and certification file for
    certificate authentication
    """

    global authHandler

    if not conf.aType and not conf.aCred and not conf.aCert:
        return

    elif conf.aType and not conf.aCred:
        errMsg = "you specified the HTTP authentication type, but "
        errMsg += "did not provide the credentials"
        raise SqlmapSyntaxException, errMsg

    elif not conf.aType and conf.aCred:
        errMsg = "you specified the HTTP authentication credentials, "
        errMsg += "but did not provide the type"
        raise SqlmapSyntaxException, errMsg

    if not conf.aCert:
        debugMsg = "setting the HTTP authentication type and credentials"
        logger.debug(debugMsg)

        aTypeLower = conf.aType.lower()

        if aTypeLower not in ( "basic", "digest", "ntlm" ):
            errMsg = "HTTP authentication type value must be "
            errMsg += "Basic, Digest or NTLM"
            raise SqlmapSyntaxException, errMsg
        elif aTypeLower in ( "basic", "digest" ):
            regExp = "^(.*?):(.*?)$"
            errMsg = "HTTP %s authentication credentials " % aTypeLower
            errMsg += "value must be in format username:password"
        elif aTypeLower == "ntlm":
            regExp = "^(.*\\\\.*):(.*?)$"
            errMsg = "HTTP NTLM authentication credentials value must "
            errMsg += "be in format DOMAIN\username:password"

        aCredRegExp = re.search(regExp, conf.aCred)

        if not aCredRegExp:
            raise SqlmapSyntaxException, errMsg

        conf.authUsername = aCredRegExp.group(1)
        conf.authPassword = aCredRegExp.group(2)

        kb.passwordMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

        _setAuthCred()

        if aTypeLower == "basic":
            authHandler = SmartHTTPBasicAuthHandler(kb.passwordMgr)

        elif aTypeLower == "digest":
            authHandler = urllib2.HTTPDigestAuthHandler(kb.passwordMgr)

        elif aTypeLower == "ntlm":
            try:
                from ntlm import HTTPNtlmAuthHandler
            except ImportError:
                errMsg = "sqlmap requires Python NTLM third-party library "
                errMsg += "in order to authenticate via NTLM, "
                errMsg += "http://code.google.com/p/python-ntlm/"
                raise SqlmapMissingDependence, errMsg

            authHandler = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(kb.passwordMgr)
    else:
        debugMsg = "setting the HTTP(s) authentication certificate"
        logger.debug(debugMsg)

        aCertRegExp = re.search("^(.+?),\s*(.+?)$", conf.aCert)

        if not aCertRegExp:
            errMsg = "HTTP authentication certificate option "
            errMsg += "must be in format key_file,cert_file"
            raise SqlmapSyntaxException, errMsg

        # os.path.expanduser for support of paths with ~
        key_file = os.path.expanduser(aCertRegExp.group(1))
        cert_file = os.path.expanduser(aCertRegExp.group(2))

        for ifile in (key_file, cert_file):
            if not os.path.exists(ifile):
                errMsg = "File '%s' does not exist" % ifile
                raise SqlmapSyntaxException, errMsg

        authHandler = HTTPSCertAuthHandler(key_file, cert_file)

def _setHTTPMethod():
    """
    Check and set the HTTP method to perform HTTP requests through.
    """

    conf.method = HTTPMETHOD.POST if conf.data is not None else HTTPMETHOD.GET

    debugMsg = "setting the HTTP method to %s" % conf.method
    logger.debug(debugMsg)

def _setHTTPExtraHeaders():
    if conf.headers:
        debugMsg = "setting extra HTTP headers"
        logger.debug(debugMsg)

        conf.headers = conf.headers.split("\n") if "\n" in conf.headers else conf.headers.split("\\n")

        for headerValue in conf.headers:
            if headerValue.count(':') == 1:
                header, value = (_.lstrip() for _ in headerValue.split(":"))

                if header and value:
                    conf.httpHeaders.append((header, value))
            else:
                errMsg = "invalid header value: %s. Valid header format is 'name:value'" % repr(headerValue).lstrip('u')
                raise SqlmapSyntaxException, errMsg

    elif not conf.httpHeaders or len(conf.httpHeaders) == 1:
        conf.httpHeaders.append((HTTPHEADER.ACCEPT_LANGUAGE, "en-us,en;q=0.5"))
        if not conf.charset:
            conf.httpHeaders.append((HTTPHEADER.ACCEPT_CHARSET, "ISO-8859-15,utf-8;q=0.7,*;q=0.7"))
        else:
            conf.httpHeaders.append((HTTPHEADER.ACCEPT_CHARSET, "%s;q=0.7,*;q=0.1" % conf.charset))

        # Invalidating any caching mechanism in between
        # Reference: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        conf.httpHeaders.append((HTTPHEADER.CACHE_CONTROL, "no-cache,no-store"))
        conf.httpHeaders.append((HTTPHEADER.PRAGMA, "no-cache"))

def _defaultHTTPUserAgent():
    """
    @return: default sqlmap HTTP User-Agent header
    @rtype: C{str}
    """

    return "%s (%s)" % (VERSION_STRING, SITE)

    # Firefox 3 running on Ubuntu 9.04 updated at April 2009
    #return "Mozilla/5.0 (X11; U; Linux i686; en-GB; rv:1.9.0.9) Gecko/2009042113 Ubuntu/9.04 (jaunty) Firefox/3.0.9"

    # Internet Explorer 7.0 running on Windows 2003 Service Pack 2 english
    # updated at March 2009
    #return "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.04506.648; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)"

def _setHTTPUserAgent():
    """
    Set the HTTP User-Agent header.
    Depending on the user options it can be:

        * The default sqlmap string
        * A default value read as user option
        * A random value read from a list of User-Agent headers from a
          file choosed as user option
    """

    if conf.mobile:
        message = "which smartphone do you want sqlmap to imitate "
        message += "through HTTP User-Agent header?\n"
        items = sorted(getPublicTypeMembers(MOBILES, True))

        for count in xrange(len(items)):
            item = items[count]
            message += "[%d] %s%s\n" % (count + 1, item[0], " (default)" if item == MOBILES.IPHONE else "")

        test = readInput(message.rstrip('\n'), default=items.index(MOBILES.IPHONE) + 1)

        try:
            item = items[int(test) - 1]
        except:
            item = MOBILES.IPHONE

        conf.httpHeaders.append((HTTPHEADER.USER_AGENT, item[1]))

    elif conf.agent:
        debugMsg = "setting the HTTP User-Agent header"
        logger.debug(debugMsg)

        conf.httpHeaders.append((HTTPHEADER.USER_AGENT, conf.agent))

    elif not conf.randomAgent:
        _ = True

        for header, _ in conf.httpHeaders:
            if header == HTTPHEADER.USER_AGENT:
                _ = False
                break

        if _:
            conf.httpHeaders.append((HTTPHEADER.USER_AGENT, _defaultHTTPUserAgent()))

    else:
        if not kb.userAgents:
            debugMsg = "loading random HTTP User-Agent header(s) from "
            debugMsg += "file '%s'" % paths.USER_AGENTS
            logger.debug(debugMsg)

            try:
                kb.userAgents = getFileItems(paths.USER_AGENTS)
            except IOError:
                warnMsg = "unable to read HTTP User-Agent header "
                warnMsg += "file '%s'" % paths.USER_AGENTS
                logger.warn(warnMsg)

                conf.httpHeaders.append((HTTPHEADER.USER_AGENT, _defaultHTTPUserAgent()))
                return

        count = len(kb.userAgents)

        if count == 1:
            userAgent = kb.userAgents[0]
        else:
            userAgent = kb.userAgents[randomRange(stop=count-1)]

        userAgent = sanitizeStr(userAgent)
        conf.httpHeaders.append((HTTPHEADER.USER_AGENT, userAgent))

        infoMsg = "fetched random HTTP User-Agent header from "
        infoMsg += "file '%s': %s" % (paths.USER_AGENTS, userAgent)
        logger.info(infoMsg)

def _setHTTPReferer():
    """
    Set the HTTP Referer
    """

    if conf.referer:
        debugMsg = "setting the HTTP Referer header"
        logger.debug(debugMsg)

        conf.httpHeaders.append((HTTPHEADER.REFERER, conf.referer))

def _setHTTPCookies():
    """
    Set the HTTP Cookie header
    """

    if conf.cookie:
        debugMsg = "setting the HTTP Cookie header"
        logger.debug(debugMsg)

        conf.httpHeaders.append((HTTPHEADER.COOKIE, conf.cookie))

def _setHTTPTimeout():
    """
    Set the HTTP timeout
    """

    if conf.timeout:
        debugMsg = "setting the HTTP timeout"
        logger.debug(debugMsg)

        conf.timeout = float(conf.timeout)

        if conf.timeout < 3.0:
            warnMsg = "the minimum HTTP timeout is 3 seconds, sqlmap "
            warnMsg += "will going to reset it"
            logger.warn(warnMsg)

            conf.timeout = 3.0
    else:
        conf.timeout = 30.0

    socket.setdefaulttimeout(conf.timeout)

def _checkDependencies():
    """
    Checks for missing dependencies.
    """

    if conf.dependencies:
        checkDependencies()

def _cleanupOptions():
    """
    Cleanup configuration attributes.
    """

    debugMsg = "cleaning up configuration parameters"
    logger.debug(debugMsg)

    width = getConsoleWidth()

    if conf.eta:
        conf.progressWidth = width - 26
    else:
        conf.progressWidth = width - 46

    if conf.testParameter:
        conf.testParameter = urldecode(conf.testParameter)
        conf.testParameter = conf.testParameter.replace(" ", "")
        conf.testParameter = re.split(PARAMETER_SPLITTING_REGEX, conf.testParameter)
    else:
        conf.testParameter = []

    if conf.user:
        conf.user = conf.user.replace(" ", "")

    if conf.rParam:
        conf.rParam = conf.rParam.replace(" ", "")
        conf.rParam = re.split(PARAMETER_SPLITTING_REGEX, conf.rParam)
    else:
        conf.rParam = []

    if conf.skip:
        conf.skip = conf.skip.replace(" ", "")
        conf.skip = re.split(PARAMETER_SPLITTING_REGEX, conf.skip)
    else:
        conf.skip = []

    if conf.delay:
        conf.delay = float(conf.delay)

    if conf.rFile:
        conf.rFile = ntToPosixSlashes(normalizePath(conf.rFile))

    if conf.wFile:
        conf.wFile = ntToPosixSlashes(normalizePath(conf.wFile))

    if conf.dFile:
        conf.dFile = ntToPosixSlashes(normalizePath(conf.dFile))

    if conf.msfPath:
        conf.msfPath = ntToPosixSlashes(normalizePath(conf.msfPath))

    if conf.tmpPath:
        conf.tmpPath = ntToPosixSlashes(normalizePath(conf.tmpPath))

    if conf.googleDork or conf.logFile or conf.bulkFile or conf.forms or conf.crawlDepth:
        conf.multipleTargets = True

    if conf.optimize:
        setOptimize()

    if conf.data:
        conf.data = re.sub(INJECT_HERE_MARK.replace(" ", r"[^A-Za-z]*"), CUSTOM_INJECTION_MARK_CHAR, conf.data, re.I)

        if re.search(r'%[0-9a-f]{2}', conf.data, re.I):
            original = conf.data
            class _(unicode): pass
            conf.data = _(urldecode(conf.data))
            setattr(conf.data, UNENCODED_ORIGINAL_VALUE, original)
        else:
            conf.data = urldecode(conf.data)

    if conf.url:
        conf.url = re.sub(INJECT_HERE_MARK.replace(" ", r"[^A-Za-z]*"), CUSTOM_INJECTION_MARK_CHAR, conf.url, re.I)

    if conf.os:
        conf.os = conf.os.capitalize()

    if conf.dbms:
        conf.dbms = conf.dbms.capitalize()

    if conf.testFilter:
        if not any([char in conf.testFilter for char in ('.', ')', '(', ']', '[')]):
            conf.testFilter = conf.testFilter.replace('*', '.*')

    if conf.timeSec not in kb.explicitSettings:
        if conf.tor:
            conf.timeSec = 2 * conf.timeSec
            kb.adjustTimeDelay = ADJUST_TIME_DELAY.DISABLE

            warnMsg = "increasing default value for "
            warnMsg += "option '--time-sec' to %d because " % conf.timeSec
            warnMsg += "switch '--tor' was provided"
            logger.warn(warnMsg)
    else:
        kb.adjustTimeDelay = ADJUST_TIME_DELAY.DISABLE

    if conf.code:
        conf.code = int(conf.code)

    if conf.csvDel:
        conf.csvDel = conf.csvDel.decode("string_escape") # e.g. '\\t' -> '\t'

    if conf.torPort and conf.torPort.isdigit():
        conf.torPort = int(conf.torPort)

    if conf.torType:
        conf.torType = conf.torType.upper()

    if conf.oDir:
        paths.SQLMAP_OUTPUT_PATH = conf.oDir

    if conf.string:
        try:
            conf.string = conf.string.decode("unicode_escape")
        except:
            charset = string.whitespace.replace(" ", "")
            for _ in charset:
                conf.string = conf.string.replace(_.encode("string_escape"), _)

    if conf.getAll:
        map(lambda x: conf.__setitem__(x, True), WIZARD.ALL)

    if conf.noCast:
        for _ in DUMP_REPLACEMENTS.keys():
            del DUMP_REPLACEMENTS[_]

    if conf.dumpFormat:
        conf.dumpFormat = conf.dumpFormat.upper()

    if conf.torType:
        conf.torType = conf.torType.upper()

    threadData = getCurrentThreadData()
    threadData.reset()

def _purgeOutput():
    """
    Safely removes (purges) output directory.
    """

    if conf.purgeOutput:
        purge(paths.SQLMAP_OUTPUT_PATH)

def _setConfAttributes():
    """
    This function set some needed attributes into the configuration
    singleton.
    """

    debugMsg = "initializing the configuration"
    logger.debug(debugMsg)

    conf.authUsername = None
    conf.authPassword = None
    conf.boundaries = []
    conf.cj = None
    conf.dbmsConnector = None
    conf.dbmsHandler = None
    conf.dnsServer = None
    conf.dumpPath = None
    conf.hashDB = None
    conf.hashDBFile = None
    conf.httpHeaders = []
    conf.hostname = None
    conf.ipv6 = False
    conf.multipleTargets = False
    conf.outputPath = None
    conf.paramDict = {}
    conf.parameters = {}
    conf.path = None
    conf.port = None
    conf.resultsFilename = None
    conf.resultsFP = None
    conf.scheme = None
    conf.tests = []
    conf.trafficFP = None
    conf.wFileType = None

def _setKnowledgeBaseAttributes(flushAll=True):
    """
    This function set some needed attributes into the knowledge base
    singleton.
    """

    debugMsg = "initializing the knowledge base"
    logger.debug(debugMsg)

    kb.absFilePaths = set()
    kb.adjustTimeDelay = None
    kb.alerted = False
    kb.alwaysRefresh = None
    kb.arch = None
    kb.authHeader = None
    kb.bannerFp = AttribDict()

    kb.brute = AttribDict({"tables":[], "columns":[]})
    kb.bruteMode = False

    kb.cache = AttribDict()
    kb.cache.content = {}
    kb.cache.regex = {}
    kb.cache.stdev = {}

    kb.chars = AttribDict()
    kb.chars.delimiter = randomStr(length=6, lowercase=True)
    kb.chars.start = ":%s:" % randomStr(length=3, lowercase=True)
    kb.chars.stop = ":%s:" % randomStr(length=3, lowercase=True)
    kb.chars.at, kb.chars.space, kb.chars.dollar, kb.chars.hash_ = (":%s:" % _ for _ in randomStr(length=4, lowercase=True))

    kb.commonOutputs = None
    kb.counters = {}
    kb.data = AttribDict()
    kb.dataOutputFlag = False

    # Active back-end DBMS fingerprint
    kb.dbms = None
    kb.dbmsVersion = [ UNKNOWN_DBMS_VERSION ]

    kb.delayCandidates = TIME_DELAY_CANDIDATES * [0]
    kb.dep = None
    kb.dnsMode = False
    kb.dnsTest = None
    kb.docRoot = None
    kb.dumpTable = None
    kb.dynamicMarkings = []
    kb.dynamicParameter = False
    kb.endDetection = False
    kb.explicitSettings = set()
    kb.errorIsNone = True
    kb.fileReadMode = False
    kb.forcedDbms = None
    kb.headersFp = {}
    kb.heuristicTest = None
    kb.hintValue = None
    kb.htmlFp = []
    kb.httpErrorCodes = {}
    kb.inferenceMode = False
    kb.ignoreCasted = None
    kb.ignoreNotFound = False
    kb.ignoreTimeout = False
    kb.injection = InjectionDict()
    kb.injections = []
    kb.lastParserStatus = None

    kb.locks = AttribDict()
    for _ in ("cache", "count", "index", "io", "limits", "log", "outputs", "value"):
        kb.locks[_] = threading.Lock()

    kb.matchRatio = None
    kb.maxConnectionsFlag = False
    kb.mergeCookies = None
    kb.multiThreadMode = False
    kb.negativeLogic = False
    kb.nullConnection = None
    kb.pageCompress = True
    kb.pageTemplate = None
    kb.pageTemplates = dict()
    kb.postHint = None
    kb.previousMethod = None
    kb.processUserMarks = None
    kb.orderByColumns = None
    kb.originalCode = None
    kb.originalPage = None
    kb.originalTimeDelay = None
    kb.originalUrls = dict()

    # Back-end DBMS underlying operating system fingerprint via banner (-b)
    # parsing
    kb.os = None
    kb.osVersion = None
    kb.osSP = None

    kb.pageEncoding = DEFAULT_PAGE_ENCODING
    kb.pageStable = None
    kb.partRun = None
    kb.permissionFlag = False
    kb.prependFlag = False
    kb.processResponseCounter = 0
    kb.proxyAuthHeader = None
    kb.queryCounter = 0
    kb.redirectChoice = None
    kb.redirectSetCookie = None
    kb.reflectiveMechanism = True
    kb.reflectiveCounters = {REFLECTIVE_COUNTER.MISS:0, REFLECTIVE_COUNTER.HIT:0}
    kb.responseTimes = []
    kb.resumeValues = True
    kb.safeCharEncode = False
    kb.singleLogFlags = set()
    kb.skipOthersDbms = None
    kb.stickyDBMS = False
    kb.stickyLevel = None
    kb.suppressResumeInfo = False
    kb.technique = None
    kb.testMode = False
    kb.testQueryCount = 0
    kb.threadContinue = True
    kb.threadException = False
    kb.timeValidCharsRun = 0
    kb.uChar = NULL
    kb.unionDuplicates = False
    kb.xpCmdshellAvailable = False

    if flushAll:
        kb.headerPaths = {}
        kb.keywords = set(getFileItems(paths.SQL_KEYWORDS))
        kb.passwordMgr = None
        kb.tamperFunctions = []
        kb.targets = oset()
        kb.testedParams = set()
        kb.userAgents = None
        kb.vainRun = True
        kb.vulnHosts = set()
        kb.wordlists = None

def _useWizardInterface():
    """
    Presents simple wizard interface for beginner users
    """

    if not conf.wizard:
        return

    logger.info("starting wizard interface")

    while True:
        while not conf.url:
            message = "Please enter full target URL (-u): "
            conf.url = readInput(message, default=None)

        message = "POST data (--data) [Enter for None]: "
        conf.data = readInput(message, default=None)

        if filter(lambda x: '=' in str(x), [conf.url, conf.data]) or '*' in conf.url:
            break
        else:
            warnMsg = "no GET and/or POST parameter(s) found for testing "
            warnMsg += "(e.g. GET parameter 'id' in 'www.site.com/index.php?id=1')"
            logger.critical(warnMsg)

            if conf.crawlDepth or conf.forms:
                break
            else:
                conf.url = conf.data = None

    choice = None

    while choice is None or choice not in ("", "1", "2", "3"):
        message = "Injection difficulty (--level/--risk). Please choose:\n"
        message += "[1] Normal (default)\n[2] Medium\n[3] Hard"
        choice = readInput(message, default='1')

        if choice == '2':
            conf.risk = 2
            conf.level = 3
        elif choice == '3':
            conf.risk = 3
            conf.level = 5
        else:
            conf.risk = 1
            conf.level = 1

    if not conf.getAll:
        choice = None

        while choice is None or choice not in ("", "1", "2", "3"):
            message = "Enumeration (--banner/--current-user/etc). Please choose:\n"
            message += "[1] Basic (default)\n[2] Smart\n[3] All"
            choice = readInput(message, default='1')

            if choice == '2':
                map(lambda x: conf.__setitem__(x, True), WIZARD.SMART)
            elif choice == '3':
                map(lambda x: conf.__setitem__(x, True), WIZARD.ALL)
            else:
                map(lambda x: conf.__setitem__(x, True), WIZARD.BASIC)

    logger.debug("muting sqlmap.. it will do the magic for you")
    conf.verbose = 0

    conf.batch = True
    conf.threads = 4

    dataToStdout("\nsqlmap is running, please wait..\n\n")

def _saveCmdline():
    """
    Saves the command line options on a sqlmap configuration INI file
    Format.
    """

    if not conf.saveCmdline:
        return

    debugMsg = "saving command line options on a sqlmap configuration INI file"
    logger.debug(debugMsg)

    config = UnicodeRawConfigParser()
    userOpts = {}

    for family in optDict.keys():
        userOpts[family] = []

    for option, value in conf.items():
        for family, optionData in optDict.items():
            if option in optionData:
                userOpts[family].append((option, value, optionData[option]))

    for family, optionData in userOpts.items():
        config.add_section(family)

        optionData.sort()

        for option, value, datatype in optionData:
            if datatype and isListLike(datatype):
                datatype = datatype[0]

            if value is None:
                if datatype == "boolean":
                    value = "False"
                elif datatype in ( "integer", "float" ):
                    if option in ( "threads", "verbose" ):
                        value = "1"
                    elif option == "timeout":
                        value = "10"
                    else:
                        value = "0"
                elif datatype == "string":
                    value = ""

            if isinstance(value, basestring):
                value = value.replace("\n", "\n ")

            config.set(family, option, value)

    confFP = openFile(paths.SQLMAP_CONFIG, "wb")
    config.write(confFP)

    infoMsg = "saved command line options on '%s' configuration file" % paths.SQLMAP_CONFIG
    logger.info(infoMsg)

def _setVerbosity():
    """
    This function set the verbosity of sqlmap output messages.
    """

    if conf.verbose is None:
        conf.verbose = 1

    conf.verbose = int(conf.verbose)

    if conf.verbose == 0:
        logger.setLevel(logging.ERROR)
    elif conf.verbose == 1:
        logger.setLevel(logging.INFO)
    elif conf.verbose > 2 and conf.eta:
        conf.verbose = 2
        logger.setLevel(logging.DEBUG)
    elif conf.verbose == 2:
        logger.setLevel(logging.DEBUG)
    elif conf.verbose == 3:
        logger.setLevel(CUSTOM_LOGGING.PAYLOAD)
    elif conf.verbose == 4:
        logger.setLevel(CUSTOM_LOGGING.TRAFFIC_OUT)
    elif conf.verbose >= 5:
        logger.setLevel(CUSTOM_LOGGING.TRAFFIC_IN)

def _mergeOptions(inputOptions, overrideOptions):
    """
    Merge command line options with configuration file and default options.

    @param inputOptions: optparse object with command line options.
    @type inputOptions: C{instance}
    """

    if inputOptions.configFile:
        configFileParser(inputOptions.configFile)

    if hasattr(inputOptions, "items"):
        inputOptionsItems = inputOptions.items()
    else:
        inputOptionsItems = inputOptions.__dict__.items()

    for key, value in inputOptionsItems:
        if key not in conf or value not in (None, False) or overrideOptions:
            conf[key] = value

    for key, value in conf.items():
        if value is not None:
            kb.explicitSettings.add(key)

    for key, value in defaults.items():
        if conf[key] is None:
            conf[key] = value

def _setTrafficOutputFP():
    if conf.trafficFile:
        infoMsg = "setting file for logging HTTP traffic"
        logger.info(infoMsg)

        conf.trafficFP = openFile(conf.trafficFile, "w+")

def _setDNSServer():
    if not conf.dnsName:
        return

    infoMsg = "setting up DNS server instance"
    logger.info(infoMsg)

    isAdmin = runningAsAdmin()

    if isAdmin:
        try:
            conf.dnsServer = DNSServer()
            conf.dnsServer.run()
        except socket.error, msg:
            errMsg = "there was an error while setting up "
            errMsg += "DNS server instance ('%s')" % msg
            raise SqlmapGenericException, errMsg
    else:
        errMsg = "you need to run sqlmap as an administrator "
        errMsg += "if you want to perform a DNS data exfiltration attack "
        errMsg += "as it will need to listen on privileged UDP port 53 "
        errMsg += "for incoming address resolution attempts"
        raise SqlmapMissingPrivileges, errMsg

def _setTorProxySettings():
    if not conf.tor:
        return

    if conf.torType == PROXY_TYPE.HTTP:
        _setTorHttpProxySettings()
    else:
        _setTorSocksProxySettings()

def _setTorHttpProxySettings():
    infoMsg = "setting Tor HTTP proxy settings"
    logger.info(infoMsg)

    found = None

    for port in (DEFAULT_TOR_HTTP_PORTS if not conf.torPort else (conf.torPort, )):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((LOCALHOST, port))
            found = port
            break
        except socket.error:
            pass

    s.close()

    if found:
        conf.proxy = "http://%s:%d" % (LOCALHOST, found)
    else:
        errMsg = "can't establish connection with the Tor proxy. "
        errMsg += "Please make sure that you have Vidalia, Privoxy or "
        errMsg += "Polipo bundle installed for you to be able to "
        errMsg += "successfully use switch '--tor' "

        if IS_WIN:
            errMsg += "(e.g. https://www.torproject.org/projects/vidalia.html.en)"
        else:
            errMsg += "(e.g. http://www.coresec.org/2011/04/24/sqlmap-with-tor/)"

        raise SqlmapConnectionException, errMsg

    if not conf.checkTor:
        warnMsg = "use switch '--check-tor' at "
        warnMsg += "your own convenience when using "
        warnMsg += "HTTP proxy type (option '--tor-type') "
        warnMsg += "for accessing Tor anonymizing network because of "
        warnMsg += "known issues with default settings of various 'bundles' "
        warnMsg += "(e.g. Vidalia)"
        logger.warn(warnMsg)

def _setTorSocksProxySettings():
    infoMsg = "setting Tor SOCKS proxy settings"
    logger.info(infoMsg)

    # Has to be SOCKS5 to prevent DNS leaks (http://en.wikipedia.org/wiki/Tor_%28anonymity_network%29)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 if conf.torType == PROXY_TYPE.SOCKS5 else socks.PROXY_TYPE_SOCKS4, LOCALHOST, conf.torPort or DEFAULT_TOR_SOCKS_PORT)
    socks.wrapmodule(urllib2)

def _checkTor():
    if not conf.checkTor:
        return

    infoMsg = "checking Tor connection"
    logger.info(infoMsg)

    page, _, _ = Request.getPage(url="https://check.torproject.org/", raise404=False)
    if not page or 'Congratulations' not in page:
        errMsg = "it seems that Tor is not properly set. Please try using options '--tor-type' and/or '--tor-port'"
        raise SqlmapConnectionException, errMsg
    else:
        infoMsg = "Tor is properly being used"
        logger.info(infoMsg)

def _basicOptionValidation():
    if conf.limitStart is not None and not (isinstance(conf.limitStart, int) and conf.limitStart > 0):
        errMsg = "value for option '--start' (limitStart) must be an integer value greater than zero (>0)"
        raise SqlmapSyntaxException, errMsg

    if conf.limitStop is not None and not (isinstance(conf.limitStop, int) and conf.limitStop > 0):
        errMsg = "value for option '--stop' (limitStop) must be an integer value greater than zero (>0)"
        raise SqlmapSyntaxException, errMsg

    if conf.level is not None and not (isinstance(conf.level, int) and conf.level > 0):
        errMsg = "value for option '--level' must be an integer value greater than zero (>0)"
        raise SqlmapSyntaxException, errMsg

    if conf.risk is not None and not (isinstance(conf.risk, int) and conf.risk > 0):
        errMsg = "value for option '--risk' must be an integer value greater than zero (>0)"
        raise SqlmapSyntaxException, errMsg

    if conf.limitStart is not None and isinstance(conf.limitStart, int) and conf.limitStart > 0 and \
       conf.limitStop is not None and isinstance(conf.limitStop, int) and conf.limitStop < conf.limitStart:
        errMsg = "value for option '--start' (limitStart) must be smaller or equal than value for --stop (limitStop) option"
        raise SqlmapSyntaxException, errMsg

    if conf.firstChar is not None and isinstance(conf.firstChar, int) and conf.firstChar > 0 and \
       conf.lastChar is not None and isinstance(conf.lastChar, int) and conf.lastChar < conf.firstChar:
        errMsg = "value for option '--first' (firstChar) must be smaller than or equal to value for --last (lastChar) option"
        raise SqlmapSyntaxException, errMsg

    if conf.cpuThrottle is not None and isinstance(conf.cpuThrottle, int) and (conf.cpuThrottle > 100 or conf.cpuThrottle < 0):
        errMsg = "value for option '--cpu-throttle' (cpuThrottle) must be in range [0,100]"
        raise SqlmapSyntaxException, errMsg

    if conf.textOnly and conf.nullConnection:
        errMsg = "switch '--text-only' is incompatible with switch '--null-connection'"
        raise SqlmapSyntaxException, errMsg

    if conf.titles and conf.nullConnection:
        errMsg = "switch '--titles' is incompatible with switch '--null-connection'"
        raise SqlmapSyntaxException, errMsg

    if conf.data and conf.nullConnection:
        errMsg = "option '--data' is incompatible with switch '--null-connection'"
        raise SqlmapSyntaxException, errMsg

    if conf.string and conf.nullConnection:
        errMsg = "option '--string' is incompatible with switch '--null-connection'"
        raise SqlmapSyntaxException, errMsg

    if conf.notString and conf.nullConnection:
        errMsg = "option '--not-string' is incompatible with switch '--null-connection'"
        raise SqlmapSyntaxException, errMsg

    if conf.string and conf.notString:
        errMsg = "option '--string' is incompatible with switch '--not-string'"
        raise SqlmapSyntaxException, errMsg

    if conf.regexp and conf.nullConnection:
        errMsg = "option '--regexp' is incompatible with switch '--null-connection'"
        raise SqlmapSyntaxException, errMsg

    if conf.dumpTable and conf.dumpAll:
        errMsg = "switch '--dump' is incompatible with switch '--dump-all'"
        raise SqlmapSyntaxException, errMsg

    if conf.predictOutput and (conf.threads > 1 or conf.optimize):
        errMsg = "switch '--predict-output' is incompatible with option '--threads' and switch '-o'"
        raise SqlmapSyntaxException, errMsg

    if conf.threads > MAX_NUMBER_OF_THREADS:
        errMsg = "maximum number of used threads is %d avoiding possible connection issues" % MAX_NUMBER_OF_THREADS
        raise SqlmapSyntaxException, errMsg

    if conf.forms and not conf.url:
        errMsg = "switch '--forms' requires usage of option '-u' (--url)"
        raise SqlmapSyntaxException, errMsg

    if conf.requestFile and conf.url:
        errMsg = "option '-r' is incompatible with option '-u' (--url)"
        raise SqlmapSyntaxException, errMsg

    if conf.tor and conf.ignoreProxy:
        errMsg = "switch '--tor' is incompatible with switch '--ignore-proxy'"
        raise SqlmapSyntaxException, errMsg

    if conf.tor and conf.proxy:
        errMsg = "switch '--tor' is incompatible with option '--proxy'"
        raise SqlmapSyntaxException, errMsg

    if conf.checkTor and not any((conf.tor, conf.proxy)):
        errMsg = "switch '--check-tor' requires usage of switch '--tor' (or option '--proxy' with HTTP proxy address using Tor)"
        raise SqlmapSyntaxException, errMsg

    if conf.torPort is not None and not (isinstance(conf.torPort, int) and conf.torPort > 0):
        errMsg = "value for option '--tor-port' must be a positive integer"
        raise SqlmapSyntaxException, errMsg

    if conf.torType not in getPublicTypeMembers(PROXY_TYPE, True):
        errMsg = "option '--tor-type' accepts one of following values: %s" % ", ".join(getPublicTypeMembers(PROXY_TYPE, True))
        raise SqlmapSyntaxException, errMsg

    if conf.dumpFormat not in getPublicTypeMembers(DUMP_FORMAT, True):
        errMsg = "option '--dump-format' accepts one of following values: %s" % ", ".join(getPublicTypeMembers(DUMP_FORMAT, True))
        raise SqlmapSyntaxException, errMsg

    if conf.skip and conf.testParameter:
        errMsg = "option '--skip' is incompatible with option '-p'"
        raise SqlmapSyntaxException, errMsg

    if conf.mobile and conf.agent:
        errMsg = "switch '--mobile' is incompatible with option '--user-agent'"
        raise SqlmapSyntaxException, errMsg

    if conf.proxy and conf.ignoreProxy:
        errMsg = "option '--proxy' is incompatible with switch '--ignore-proxy'"
        raise SqlmapSyntaxException, errMsg

    if conf.forms and any([conf.logFile, conf.bulkFile, conf.direct, conf.requestFile, conf.googleDork]):
        errMsg = "switch '--forms' is compatible only with option '-u' (--url)"
        raise SqlmapSyntaxException, errMsg

    if conf.timeSec < 1:
        errMsg = "value for option '--time-sec' must be a positive integer"
        raise SqlmapSyntaxException, errMsg

    if conf.uChar and not re.match(UNION_CHAR_REGEX, conf.uChar):
        errMsg = "value for option '--union-char' must be an alpha-numeric value (e.g. 1)"
        raise SqlmapSyntaxException, errMsg

    if isinstance(conf.uCols, basestring):
        if not conf.uCols.isdigit() and ("-" not in conf.uCols or len(conf.uCols.split("-")) != 2):
            errMsg = "value for option '--union-cols' must be a range with hyphon "
            errMsg += "(e.g. 1-10) or integer value (e.g. 5)"
            raise SqlmapSyntaxException, errMsg

    if conf.charset:
        _ = checkCharEncoding(conf.charset, False)
        if _ is None:
            errMsg = "unknown charset '%s'. Please visit " % conf.charset
            errMsg += "'%s' to get the full list of " % CODECS_LIST_PAGE
            errMsg += "supported charsets"
            raise SqlmapSyntaxException, errMsg
        else:
            conf.charset = _

    if conf.loadCookies:
        if not os.path.exists(conf.loadCookies):
            errMsg = "cookies file '%s' does not exist" % conf.loadCookies
            raise SqlmapFilePathException, errMsg

def _resolveCrossReferences():
    lib.core.threads.readInput = readInput
    lib.core.common.getPageTemplate = getPageTemplate
    lib.core.convert.singleTimeWarnMessage = singleTimeWarnMessage

def init(inputOptions=AttribDict(), overrideOptions=False):
    """
    Set attributes into both configuration and knowledge base singletons
    based upon command line and configuration file options.
    """

    if not inputOptions.disableColoring:
        coloramainit()
    else:
        if hasattr(LOGGER_HANDLER, "disable_coloring"):
            LOGGER_HANDLER.disable_coloring = True
    _setConfAttributes()
    _setKnowledgeBaseAttributes()
    _mergeOptions(inputOptions, overrideOptions)
    _useWizardInterface()
    _setVerbosity()
    _saveCmdline()
    _setRequestFromFile()
    _cleanupOptions()
    _purgeOutput()
    _checkDependencies()
    _basicOptionValidation()
    _setTorProxySettings()
    _setDNSServer()
    _adjustLoggingFormatter()
    _setMultipleTargets()
    _setTamperingFunctions()
    _setTrafficOutputFP()
    _resolveCrossReferences()

    parseTargetUrl()
    parseTargetDirect()

    if any((conf.url, conf.logFile, conf.bulkFile, conf.requestFile, conf.googleDork, conf.liveTest)):
        _setHTTPTimeout()
        _setHTTPExtraHeaders()
        _setHTTPCookies()
        _setHTTPReferer()
        _setHTTPUserAgent()
        _setHTTPMethod()
        _setHTTPAuthentication()
        _setHTTPProxy()
        _setDNSCache()
        _setSafeUrl()
        _setGoogleDorking()
        _setBulkMultipleTargets()
        _urllib2Opener()
        _checkTor()
        _setCrawler()
        _findPageForms()
        _setDBMS()
        _setTechnique()

    _setThreads()
    _setOS()
    _setWriteFile()
    _setMetasploit()
    _setDBMSAuthentication()
    loadPayloads()
    _setPrefixSuffix()
    update()
    _loadQueries()
