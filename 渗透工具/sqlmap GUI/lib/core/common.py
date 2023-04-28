#!/usr/bin/env python

"""
Copyright (c) 2006-2012 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import codecs
import contextlib
import cookielib
import copy
import ctypes
import httplib
import inspect
import logging
import ntpath
import os
import posixpath
import random
import re
import socket
import string
import struct
import sys
import time
import urllib
import urlparse
import unicodedata

from ConfigParser import DEFAULTSECT
from ConfigParser import RawConfigParser
from StringIO import StringIO
from difflib import SequenceMatcher
from math import sqrt
from optparse import OptionValueError
from subprocess import PIPE
from subprocess import Popen as execute
from xml.dom import minidom
from xml.sax import parse

from extra.cloak.cloak import decloak
from extra.safe2bin.safe2bin import safecharencode
from lib.core.bigarray import BigArray
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import paths
from lib.core.convert import base64pickle
from lib.core.convert import base64unpickle
from lib.core.convert import htmlunescape
from lib.core.convert import stdoutencode
from lib.core.convert import unicodeencode
from lib.core.convert import utf8encode
from lib.core.decorators import cachedmethod
from lib.core.dicts import DBMS_DICT
from lib.core.dicts import DEPRECATED_HINTS
from lib.core.dicts import SQL_STATEMENTS
from lib.core.enums import ADJUST_TIME_DELAY
from lib.core.enums import CHARSET_TYPE
from lib.core.enums import DBMS
from lib.core.enums import EXPECTED
from lib.core.enums import HEURISTIC_TEST
from lib.core.enums import HTTPHEADER
from lib.core.enums import HTTPMETHOD
from lib.core.enums import OS
from lib.core.enums import PLACE
from lib.core.enums import PAYLOAD
from lib.core.enums import REFLECTIVE_COUNTER
from lib.core.enums import SORT_ORDER
from lib.core.exception import SqlmapDataException
from lib.core.exception import SqlmapFilePathException
from lib.core.exception import SqlmapGenericException
from lib.core.exception import SqlmapNoneDataException
from lib.core.exception import SqlmapMissingDependence
from lib.core.exception import SqlmapSilentQuitException
from lib.core.exception import SqlmapSyntaxException
from lib.core.exception import SqlmapUserQuitException
from lib.core.log import LOGGER_HANDLER
from lib.core.optiondict import optDict
from lib.core.settings import BOLD_PATTERNS
from lib.core.settings import CUSTOM_INJECTION_MARK_CHAR
from lib.core.settings import DBMS_DIRECTORY_DICT
from lib.core.settings import DEFAULT_COOKIE_DELIMITER
from lib.core.settings import DEFAULT_GET_POST_DELIMITER
from lib.core.settings import DEFAULT_MSSQL_SCHEMA
from lib.core.settings import DEPRECATED_OPTIONS
from lib.core.settings import DESCRIPTION
from lib.core.settings import DUMMY_SQL_INJECTION_CHARS
from lib.core.settings import DUMMY_USER_INJECTION
from lib.core.settings import DYNAMICITY_MARK_LENGTH
from lib.core.settings import ERROR_PARSING_REGEXES
from lib.core.settings import FORM_SEARCH_REGEX
from lib.core.settings import GENERIC_DOC_ROOT_DIRECTORY_NAMES
from lib.core.settings import HASHDB_MILESTONE_VALUE
from lib.core.settings import HOST_ALIASES
from lib.core.settings import INFERENCE_UNKNOWN_CHAR
from lib.core.settings import ISSUES_PAGE
from lib.core.settings import IS_WIN
from lib.core.settings import LARGE_OUTPUT_THRESHOLD
from lib.core.settings import MIN_TIME_RESPONSES
from lib.core.settings import ML
from lib.core.settings import NULL
from lib.core.settings import PARAMETER_AMP_MARKER
from lib.core.settings import PARAMETER_SEMICOLON_MARKER
from lib.core.settings import PARTIAL_VALUE_MARKER
from lib.core.settings import PAYLOAD_DELIMITER
from lib.core.settings import PLATFORM
from lib.core.settings import PRINTABLE_CHAR_REGEX
from lib.core.settings import PYVERSION
from lib.core.settings import REFERER_ALIASES
from lib.core.settings import REFLECTED_BORDER_REGEX
from lib.core.settings import REFLECTED_MAX_REGEX_PARTS
from lib.core.settings import REFLECTED_REPLACEMENT_REGEX
from lib.core.settings import REFLECTED_VALUE_MARKER
from lib.core.settings import REFLECTIVE_MISS_THRESHOLD
from lib.core.settings import REVISION
from lib.core.settings import SENSITIVE_DATA_REGEX
from lib.core.settings import SITE
from lib.core.settings import SUPPORTED_DBMS
from lib.core.settings import TEXT_TAG_REGEX
from lib.core.settings import TIME_STDEV_COEFF
from lib.core.settings import UNICODE_ENCODING
from lib.core.settings import UNKNOWN_DBMS_VERSION
from lib.core.settings import URI_QUESTION_MARKER
from lib.core.settings import URLENCODE_CHAR_LIMIT
from lib.core.settings import URLENCODE_FAILSAFE_CHARS
from lib.core.settings import USER_AGENT_ALIASES
from lib.core.settings import VERSION
from lib.core.settings import VERSION_STRING
from lib.core.threads import getCurrentThreadData
from thirdparty.clientform.clientform import ParseResponse
from thirdparty.clientform.clientform import ParseError
from thirdparty.magic import magic
from thirdparty.odict.odict import OrderedDict
from thirdparty.termcolor.termcolor import colored

class UnicodeRawConfigParser(RawConfigParser):
    """
    RawConfigParser with unicode writing support
    """

    def write(self, fp):
        """
        Write an .ini-format representation of the configuration state.
        """

        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)

            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, getUnicode(value, UNICODE_ENCODING).replace('\n', '\n\t')))

            fp.write("\n")

        for section in self._sections:
            fp.write("[%s]\n" % section)

            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    if value is None:
                        fp.write("%s\n" % (key))
                    else:
                        fp.write("%s = %s\n" % (key, getUnicode(value, UNICODE_ENCODING).replace('\n', '\n\t')))

            fp.write("\n")

class Format(object):
    @staticmethod
    def humanize(values, chain=" or "):
        return chain.join(values)

    # Get methods
    @staticmethod
    def getDbms(versions=None):
        """
        Format the back-end DBMS fingerprint value and return its
        values formatted as a human readable string.

        @return: detected back-end DBMS based upon fingerprint techniques.
        @rtype: C{str}
        """

        if versions is None and Backend.getVersionList():
            versions = Backend.getVersionList()

        return Backend.getDbms() if versions is None else "%s %s" % (Backend.getDbms(), " and ".join(v for v in versions))

    @staticmethod
    def getErrorParsedDBMSes():
        """
        Parses the knowledge base htmlFp list and return its values
        formatted as a human readable string.

        @return: list of possible back-end DBMS based upon error messages
        parsing.
        @rtype: C{str}
        """

        htmlParsed = None

        if len(kb.htmlFp) == 0 or kb.heuristicTest != HEURISTIC_TEST.POSITIVE:
            pass
        elif len(kb.htmlFp) == 1:
            htmlParsed = kb.htmlFp[0]
        elif len(kb.htmlFp) > 1:
            htmlParsed = " or ".join(kb.htmlFp)

        return htmlParsed

    @staticmethod
    def getOs(target, info):
        """
        Formats the back-end operating system fingerprint value
        and return its values formatted as a human readable string.

        Example of info (kb.headersFp) dictionary:

        {
          'distrib': set(['Ubuntu']),
          'type': set(['Linux']),
          'technology': set(['PHP 5.2.6', 'Apache 2.2.9']),
          'release': set(['8.10'])
        }

        Example of info (kb.bannerFp) dictionary:

        {
          'sp': set(['Service Pack 4']),
          'dbmsVersion': '8.00.194',
          'dbmsServicePack': '0',
          'distrib': set(['2000']),
          'dbmsRelease': '2000',
          'type': set(['Windows'])
        }

        @return: detected back-end operating system based upon fingerprint
        techniques.
        @rtype: C{str}
        """

        infoStr = ""

        if info and "type" in info:
            infoStr += "%s operating system: %s" % (target, Format.humanize(info["type"]))

            if "distrib" in info:
                infoStr += " %s" % Format.humanize(info["distrib"])

            if "release" in info:
                infoStr += " %s" % Format.humanize(info["release"])

            if "sp" in info:
                infoStr += " %s" % Format.humanize(info["sp"])

            if "codename" in info:
                infoStr += " (%s)" % Format.humanize(info["codename"])

        if "technology" in info:
            infoStr += "\nweb application technology: %s" % Format.humanize(info["technology"], ", ")

        return infoStr.lstrip()

class Backend:
    # Set methods
    @staticmethod
    def setDbms(dbms):
        dbms = aliasToDbmsEnum(dbms)

        if dbms is None:
            return None

        # Little precaution, in theory this condition should always be false
        elif kb.dbms is not None and kb.dbms != dbms:
            msg = "sqlmap previously fingerprinted back-end DBMS "
            msg += "%s. However now it has been fingerprinted " % kb.dbms
            msg += "to be %s. " % dbms
            msg += "Please, specify which DBMS is "
            msg += "correct [%s (default)/%s] " % (kb.dbms, dbms)

            while True:
                _ = readInput(msg, default=kb.dbms)

                if aliasToDbmsEnum(_) == kb.dbms:
                    break
                elif aliasToDbmsEnum(_) == dbms:
                    kb.dbms = aliasToDbmsEnum(_)
                    break
                else:
                    warnMsg = "invalid value"
                    logger.warn(warnMsg)

        elif kb.dbms is None:
            kb.dbms = aliasToDbmsEnum(dbms)

        return kb.dbms

    @staticmethod
    def setVersion(version):
        if isinstance(version, basestring):
            kb.dbmsVersion = [version]

        return kb.dbmsVersion

    @staticmethod
    def setVersionList(versionsList):
        if isinstance(versionsList, list):
            kb.dbmsVersion = versionsList
        elif isinstance(versionsList, basestring):
            Backend.setVersion(versionsList)
        else:
            logger.error("invalid format of versionsList")

    @staticmethod
    def forceDbms(dbms, sticky=False):
        if not kb.stickyDBMS:
            kb.forcedDbms = aliasToDbmsEnum(dbms)
            kb.stickyDBMS = sticky

    @staticmethod
    def flushForcedDbms(force=False):
        if not kb.stickyDBMS or force:
            kb.forcedDbms = None
            kb.stickyDBMS = False

    @staticmethod
    def setOs(os):
        if os is None:
            return None

        # Little precaution, in theory this condition should always be false
        elif kb.os is not None and isinstance(os, basestring) and kb.os.lower() != os.lower():
            msg = "sqlmap previously fingerprinted back-end DBMS "
            msg += "operating system %s. However now it has " % kb.os
            msg += "been fingerprinted to be %s. " % os
            msg += "Please, specify which OS is "
            msg += "correct [%s (default)/%s] " % (kb.os, os)

            while True:
                _ = readInput(msg, default=kb.os)

                if _ == kb.os:
                    break
                elif _ == os:
                    kb.os = _.capitalize()
                    break
                else:
                    warnMsg = "invalid value"
                    logger.warn(warnMsg)

        elif kb.os is None and isinstance(os, basestring):
            kb.os = os.capitalize()

        return kb.os

    @staticmethod
    def setOsVersion(version):
        if version is None:
            return None

        elif kb.osVersion is None and isinstance(version, basestring):
            kb.osVersion = version

    @staticmethod
    def setOsServicePack(sp):
        if sp is None:
            return None

        elif kb.osSP is None and isinstance(sp, int):
            kb.osSP = sp

    @staticmethod
    def setArch():
        msg = "what is the back-end database management system architecture?"
        msg += "\n[1] 32-bit (default)"
        msg += "\n[2] 64-bit"

        while True:
            _ = readInput(msg, default='1')

            if isinstance(_, basestring) and _.isdigit() and int(_) in (1, 2):
                kb.arch = 32 if int(_) == 1 else 64
                break
            else:
                warnMsg = "invalid value. Valid values are 1 and 2"
                logger.warn(warnMsg)

        return kb.arch

    # Get methods
    @staticmethod
    def getForcedDbms():
        return aliasToDbmsEnum(kb.get("forcedDbms"))

    @staticmethod
    def getDbms():
        return aliasToDbmsEnum(kb.get("dbms"))

    @staticmethod
    def getErrorParsedDBMSes():
        """
        Returns array with parsed DBMS names till now

        This functions is called to:

        1. Sort the tests, getSortedInjectionTests() - detection phase.
        2. Ask user whether or not skip specific DBMS tests in detection phase,
           lib/controller/checks.py - detection phase.
        3. Sort the fingerprint of the DBMS, lib/controller/handler.py -
           fingerprint phase.
        """

        return kb.htmlFp if kb.get("heuristicTest") == HEURISTIC_TEST.POSITIVE else []

    @staticmethod
    def getIdentifiedDbms():
        dbms = None

        if not kb:
            pass
        elif Backend.getForcedDbms() is not None:
            dbms = Backend.getForcedDbms()
        elif Backend.getDbms() is not None:
            dbms = kb.dbms
        elif conf.get('dbms'):
            dbms = conf.dbms
        elif Backend.getErrorParsedDBMSes():
            dbms = unArrayizeValue(Backend.getErrorParsedDBMSes())
        elif kb.injection.dbms:
            dbms = unArrayizeValue(kb.injection.dbms)

        return aliasToDbmsEnum(dbms)

    @staticmethod
    def getVersion():
        if len(kb.dbmsVersion) > 0:
            return kb.dbmsVersion[0]
        else:
            return None

    @staticmethod
    def getVersionList():
        if len(kb.dbmsVersion) > 0:
            return kb.dbmsVersion
        else:
            return None

    @staticmethod
    def getOs():
        return kb.os

    @staticmethod
    def getOsVersion():
        return kb.osVersion

    @staticmethod
    def getOsServicePack():
        return kb.osSP

    @staticmethod
    def getArch():
        if kb.arch is None:
            Backend.setArch()
        return kb.arch

    # Comparison methods
    @staticmethod
    def isDbms(dbms):
        if Backend.getDbms() is not None:
            return Backend.getDbms() == aliasToDbmsEnum(dbms)
        else:
            return Backend.getIdentifiedDbms() == aliasToDbmsEnum(dbms)

    @staticmethod
    def isDbmsWithin(aliases):
        return Backend.getDbms() is not None and Backend.getDbms().lower() in aliases

    @staticmethod
    def isVersion(version):
        return Backend.getVersion() is not None and Backend.getVersion() == version

    @staticmethod
    def isVersionWithin(versionList):
        if Backend.getVersionList() is None:
            return False

        for _ in Backend.getVersionList():
            if _ != UNKNOWN_DBMS_VERSION and _ in versionList:
                return True

        return False

    @staticmethod
    def isVersionGreaterOrEqualThan(version):
        return Backend.getVersion() is not None and str(Backend.getVersion()) >= str(version)

    @staticmethod
    def isOs(os):
        return Backend.getOs() is not None and Backend.getOs().lower() == os.lower()

def paramToDict(place, parameters=None):
    """
    Split the parameters into names and values, check if these parameters
    are within the testable parameters and return in a dictionary.
    """

    testableParameters = OrderedDict()

    if place in conf.parameters and not parameters:
        parameters = conf.parameters[place]

    parameters = parameters.replace(", ", ",")
    parameters = re.sub(r"&(\w{1,4});", r"%s\g<1>%s" % (PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER), parameters)
    splitParams = parameters.split(conf.pDel or (DEFAULT_COOKIE_DELIMITER if place == PLACE.COOKIE else DEFAULT_GET_POST_DELIMITER))

    for element in splitParams:
        element = re.sub(r"%s(.+?)%s" % (PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER), r"&\g<1>;", element)
        elem = element.split("=")

        if len(elem) >= 2:
            parameter = elem[0].replace(" ", "")

            condition = not conf.testParameter
            condition |= parameter in conf.testParameter

            if condition:
                testableParameters[parameter] = "=".join(elem[1:])
                if not conf.multipleTargets:
                    _ = urldecode(testableParameters[parameter], convall=True)
                    if _.strip(DUMMY_SQL_INJECTION_CHARS) != _\
                        or re.search(r'\A9{3,}', _) or re.search(DUMMY_USER_INJECTION, _):
                        warnMsg = "it appears that you have provided tainted parameter values "
                        warnMsg += "('%s') with most probably leftover " % element
                        warnMsg += "chars from manual SQL injection "
                        warnMsg += "tests (%s) or non-valid numerical value. " % DUMMY_SQL_INJECTION_CHARS
                        warnMsg += "Please, always use only valid parameter values "
                        warnMsg += "so sqlmap could be able to properly run "
                        logger.warn(warnMsg)

                        message = "Are you sure you want to continue? [y/N] "
                        test = readInput(message, default="N")
                        if test[0] not in ("y", "Y"):
                            raise SqlmapSilentQuitException

    if conf.testParameter and not testableParameters:
        paramStr = ", ".join(test for test in conf.testParameter)

        if len(conf.testParameter) > 1:
            warnMsg = "provided parameters '%s' " % paramStr
            warnMsg += "are not inside the %s" % place
            logger.warn(warnMsg)
        else:
            parameter = conf.testParameter[0]

            if not intersect(USER_AGENT_ALIASES + REFERER_ALIASES + HOST_ALIASES, parameter, True):
                warnMsg = "provided parameter '%s' " % paramStr
                warnMsg += "is not inside the %s" % place
                logger.warn(warnMsg)

    elif len(conf.testParameter) != len(testableParameters.keys()):
        for parameter in conf.testParameter:
            if parameter not in testableParameters:
                warnMsg =  "provided parameter '%s' " % parameter
                warnMsg += "is not inside the %s" % place
                logger.warn(warnMsg)

    return testableParameters

def getDocRoot():
    docRoot = None
    pagePath = directoryPath(conf.path)

    defaultDocRoot = ("C:/xampp/htdocs/", "C:/Inetpub/wwwroot/") if Backend.isOs(OS.WINDOWS) else ("/var/www/",)

    if kb.absFilePaths:
        for absFilePath in kb.absFilePaths:
            if docRoot:
                break

            if directoryPath(absFilePath) == '/':
                continue

            absFilePath = normalizePath(absFilePath)
            windowsDriveLetter = None

            if isWindowsDriveLetterPath(absFilePath):
                windowsDriveLetter, absFilePath = absFilePath[:2], absFilePath[2:]
                absFilePath = ntToPosixSlashes(posixToNtSlashes(absFilePath))

            if any("/%s/" % _ in absFilePath for _ in GENERIC_DOC_ROOT_DIRECTORY_NAMES):
                for _ in GENERIC_DOC_ROOT_DIRECTORY_NAMES:
                    _ = "/%s/" % _
                    if _ in absFilePath:
                        docRoot = "%s%s" % (absFilePath.split(_)[0], _)
                        break

            elif pagePath in absFilePath:
                docRoot = absFilePath.split(pagePath)[0]
                if windowsDriveLetter:
                    docRoot = "%s/%s" % (windowsDriveLetter, ntToPosixSlashes(docRoot))

    docRoot = normalizePath(docRoot)

    if docRoot:
        infoMsg = "retrieved the web server document root: '%s'" % docRoot
        logger.info(infoMsg)
    else:
        warnMsg = "unable to retrieve the web server document root"
        logger.warn(warnMsg)

        message = "please provide the web server document root "
        message += "[%s]: " % ",".join(root for root in defaultDocRoot)
        inputDocRoot = readInput(message, default=defaultDocRoot)

        if inputDocRoot:
            if isinstance(inputDocRoot, basestring):
                docRoot = inputDocRoot.split(',')
            else:
                docRoot = inputDocRoot
        else:
            docRoot = defaultDocRoot

    return docRoot

def getDirs():
    directories = set("/")

    if kb.absFilePaths:
        infoMsg = "retrieved web server full paths: "
        infoMsg += "'%s'" % ", ".join(ntToPosixSlashes(path) for path in kb.absFilePaths)
        logger.info(infoMsg)

        for absFilePath in kb.absFilePaths:
            if absFilePath:
                directory = directoryPath(absFilePath)
                directory = ntToPosixSlashes(directory)
                directories.add(directory)
    else:
        warnMsg = "unable to retrieve any web server path"
        logger.warn(warnMsg)

    webDir = extractRegexResult(r"//[^/]+?/(?P<result>.*)/.", conf.url)
    if webDir:
        directories.add(webDir)

    message = "please provide any additional web server full path to try "
    message += "to upload the agent [Enter for None]: "
    inputDirs = readInput(message)

    if inputDirs:
        inputDirs = inputDirs.replace(", ", ",")
        inputDirs = inputDirs.split(",")

        for inputDir in inputDirs:
            if inputDir:
                directories.add(inputDir)

    return list(directories)

def filePathToString(filePath):
    strRepl = filePath.replace("/", "_").replace("\\", "_")
    strRepl = strRepl.replace(" ", "_").replace(":", "_")

    return strRepl

def singleTimeWarnMessage(message):
    singleTimeLogMessage(message, logging.WARN)

def singleTimeLogMessage(message, level=logging.INFO, flag=None):
    if flag is None:
        flag = hash(message)

    if flag not in kb.singleLogFlags:
        kb.singleLogFlags.add(flag)
        logger.log(level, message)

def boldifyMessage(message):
    retVal = message

    if any(_ in message for _ in BOLD_PATTERNS):
        retVal = setColor(message, True)

    return retVal

def setColor(message, bold=False):
    retVal = message
    level = extractRegexResult(r"\[(?P<result>[A-Z ]+)\]", message) or kb.get("stickyLevel")

    if message and getattr(LOGGER_HANDLER, "is_tty", False):  # colorizing handler
        if bold:
            retVal = colored(message, color=None, on_color=None, attrs=("bold",))
        elif level:
            _ = LOGGER_HANDLER.level_map.get(logging.getLevelName(level))
            if _:
                background, foreground, bold = _
                retVal = colored(message, color=foreground, on_color="on_%s" % background if background else None, attrs=("bold",) if bold else None)

            kb.stickyLevel = level if message and message[-1] != "\n" else None

    return retVal

def dataToStdout(data, forceOutput=False, bold=False):
    """
    Writes text to the stdout (console) stream
    """

    message = ""

    if not kb.get("threadException"):
        if forceOutput or not getCurrentThreadData().disableStdOut:
            if kb.get("multiThreadMode"):
                logging._acquireLock()

            message = stdoutencode(data)
            sys.stdout.write(setColor(message, bold))

            try:
                sys.stdout.flush()
            except IOError:
                pass

            if kb.get("multiThreadMode"):
                logging._releaseLock()

            kb.prependFlag = len(data) == 1 and data not in ('\n', '\r') or len(data) > 2 and data[0] == '\r' and data[-1] != '\n'

def dataToTrafficFile(data):
    if not conf.trafficFile:
        return

    conf.trafficFP.write(data)
    conf.trafficFP.flush()

def dataToDumpFile(dumpFile, data):
    dumpFile.write(data)
    dumpFile.flush()

def dataToOutFile(data):
    if not data:
        return "No data retrieved"

    retVal = "%s%s%s" % (conf.filePath, os.sep, filePathToString(conf.rFile))

    with codecs.open(retVal, "wb") as f:
        f.write(data)

    return retVal

def strToHex(value):
    """
    Converts string value to it's hexadecimal representation
    """

    return (value if not isinstance(value, unicode) else value.encode(UNICODE_ENCODING)).encode("hex").upper()

def readInput(message, default=None, checkBatch=True):
    """
    Reads input from terminal
    """

    retVal = None
    kb.stickyLevel = None

    if "\n" in message:
        message += "%s> " % ("\n" if message.count("\n") > 1 else "")
    elif message[-1] == ']':
        message += " "

    if conf.answers:
        for item in conf.answers.split(','):
            question = item.split('=')[0].strip()
            answer = item.split('=')[1] if len(item.split('=')) > 1 else None
            if answer and question.lower() in message.lower():
                retVal = getUnicode(answer, UNICODE_ENCODING)

                infoMsg = "%s%s" % (getUnicode(message), retVal)
                logger.info(infoMsg)

                debugMsg = "used the given answer"
                logger.debug(debugMsg)

                break

    if retVal is None:
        if checkBatch and conf.batch:
            if isListLike(default):
                options = ",".join(getUnicode(opt, UNICODE_ENCODING) for opt in default)
            elif default:
                options = getUnicode(default, UNICODE_ENCODING)
            else:
                options = unicode()

            infoMsg = "%s%s" % (getUnicode(message), options)
            logger.info(infoMsg)

            debugMsg = "used the default behaviour, running in batch mode"
            logger.debug(debugMsg)

            retVal = default
        else:
            logging._acquireLock()
            dataToStdout("\r%s" % message, forceOutput=True, bold=True)
            kb.prependFlag = False
            try:
                retVal = raw_input() or default
                retVal = getUnicode(retVal, system=True) if retVal else retVal
            except:
                time.sleep(0.05)  # Reference: http://www.gossamer-threads.com/lists/python/python/781893
                kb.prependFlag = True
                raise SqlmapUserQuitException
            finally:
                logging._releaseLock()

    return retVal

def randomRange(start=0, stop=1000):
    """
    Returns random integer value in given range
    """

    return int(random.randint(start, stop))

def randomInt(length=4):
    """
    Returns random integer value with provided number of digits
    """

    return int("".join(random.choice(string.digits if i!=0 else string.digits.replace('0', '')) for i in xrange(0, length)))

def randomStr(length=4, lowercase=False, alphabet=None):
    """
    Returns random string value with provided number of characters
    """

    if alphabet:
        retVal = "".join(random.choice(alphabet) for _ in xrange(0, length))
    elif lowercase:
        retVal = "".join(random.choice(string.lowercase) for _ in xrange(0, length))
    else:
        retVal = "".join(random.choice(string.letters) for _ in xrange(0, length))

    return retVal

def sanitizeStr(value):
    """
    Sanitizes string value in respect to newline and line-feed characters
    """

    return getUnicode(value).replace("\n", " ").replace("\r", "")

def checkFile(filename):
    """
    Checks for file existence
    """

    if not os.path.isfile(filename):
        raise SqlmapFilePathException, "unable to read file '%s'" % filename

def banner():
    """
    This function prints sqlmap banner with its version
    """

    _ = """\n    %s - %s\n    %s\n\n""" % (VERSION_STRING, DESCRIPTION, SITE)
    dataToStdout(_, forceOutput=True)

def parsePasswordHash(password):
    blank = " " * 8

    if not password or password == " ":
        password = NULL

    if Backend.isDbms(DBMS.MSSQL) and password != NULL and isHexEncodedString(password):
        hexPassword = password
        password = "%s\n" % hexPassword
        password += "%sheader: %s\n" % (blank, hexPassword[:6])
        password += "%ssalt: %s\n" % (blank, hexPassword[6:14])
        password += "%smixedcase: %s\n" % (blank, hexPassword[14:54])

        if not Backend.isVersionWithin(("2005", "2008")):
            password += "%suppercase: %s" % (blank, hexPassword[54:])

    return password

def cleanQuery(query):
    retVal = query

    for sqlStatements in SQL_STATEMENTS.values():
        for sqlStatement in sqlStatements:
            sqlStatementEsc = sqlStatement.replace("(", "\\(")
            queryMatch = re.search("(%s)" % sqlStatementEsc, query, re.I)

            if queryMatch and "sys_exec" not in query:
                retVal = retVal.replace(queryMatch.group(1), sqlStatement.upper())

    return retVal

def setPaths():
    """
    Sets absolute paths for project directories and files
    """

    # sqlmap paths
    paths.SQLMAP_EXTRAS_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "extra")
    paths.SQLMAP_PROCS_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "procs")
    paths.SQLMAP_SHELL_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "shell")
    paths.SQLMAP_TAMPER_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "tamper")
    paths.SQLMAP_TXT_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "txt")
    paths.SQLMAP_UDF_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "udf")
    paths.SQLMAP_XML_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "xml")
    paths.SQLMAP_XML_BANNER_PATH = os.path.join(paths.SQLMAP_XML_PATH, "banner")
    paths.SQLMAP_OUTPUT_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "output")
    paths.SQLMAP_DUMP_PATH = os.path.join(paths.SQLMAP_OUTPUT_PATH, "%s", "dump")
    paths.SQLMAP_FILES_PATH = os.path.join(paths.SQLMAP_OUTPUT_PATH, "%s", "files")
    paths.SQLMAP_SEXEC_PATH = os.path.join(paths.SQLMAP_EXTRAS_PATH, "shellcodeexec")

    # sqlmap files
    paths.SQLMAP_HISTORY = os.path.join(paths.SQLMAP_ROOT_PATH, ".sqlmap_history")
    paths.SQLMAP_CONFIG = os.path.join(paths.SQLMAP_ROOT_PATH, "sqlmap-%s.conf" % randomStr())
    paths.COMMON_COLUMNS = os.path.join(paths.SQLMAP_TXT_PATH, "common-columns.txt")
    paths.COMMON_TABLES = os.path.join(paths.SQLMAP_TXT_PATH, "common-tables.txt")
    paths.COMMON_OUTPUTS = os.path.join(paths.SQLMAP_TXT_PATH, 'common-outputs.txt')
    paths.SQL_KEYWORDS = os.path.join(paths.SQLMAP_TXT_PATH, "keywords.txt")
    paths.SMALL_DICT = os.path.join(paths.SQLMAP_TXT_PATH, "smalldict.txt")
    paths.USER_AGENTS = os.path.join(paths.SQLMAP_TXT_PATH, "user-agents.txt")
    paths.WORDLIST = os.path.join(paths.SQLMAP_TXT_PATH, "wordlist.zip")
    paths.PHPIDS_RULES_XML = os.path.join(paths.SQLMAP_XML_PATH, "phpids_rules.xml")
    paths.ERRORS_XML = os.path.join(paths.SQLMAP_XML_PATH, "errors.xml")
    paths.PAYLOADS_XML = os.path.join(paths.SQLMAP_XML_PATH, "payloads.xml")
    paths.INJECTIONS_XML = os.path.join(paths.SQLMAP_XML_PATH, "injections.xml")
    paths.LIVE_TESTS_XML = os.path.join(paths.SQLMAP_XML_PATH, "livetests.xml")
    paths.QUERIES_XML = os.path.join(paths.SQLMAP_XML_PATH, "queries.xml")
    paths.GENERIC_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "generic.xml")
    paths.MSSQL_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "mssql.xml")
    paths.MYSQL_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "mysql.xml")
    paths.ORACLE_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "oracle.xml")
    paths.PGSQL_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "postgresql.xml")

def weAreFrozen():
    """
    Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located.
    Reference: http://www.py2exe.org/index.cgi/WhereAmI
    """

    return hasattr(sys, "frozen")

def parseTargetDirect():
    """
    Parse target dbms and set some attributes into the configuration singleton.
    """

    if not conf.direct:
        return

    details = None
    remote = False

    for dbms in SUPPORTED_DBMS:
        details = re.search("^(?P<dbms>%s)://(?P<credentials>(?P<user>.+?)\:(?P<pass>.*)\@)?(?P<remote>(?P<hostname>.+?)\:(?P<port>[\d]+)\/)?(?P<db>[\w\d\ \:\.\_\-\/\\\\]+?)$" % dbms, conf.direct, re.I)

        if details:
            conf.dbms = details.group('dbms')

            if details.group('credentials'):
                conf.dbmsUser = details.group('user')
                conf.dbmsPass = details.group('pass')
            else:
                conf.dbmsUser = unicode()
                conf.dbmsPass = unicode()

            if not conf.dbmsPass:
                conf.dbmsPass = None

            if details.group('remote'):
                remote = True
                conf.hostname = details.group('hostname')
                conf.port = int(details.group('port'))
            else:
                conf.hostname = "localhost"
                conf.port = 0

            conf.dbmsDb = details.group('db')

            conf.parameters[None] = "direct connection"

            break

    if not details:
        errMsg = "invalid target details, valid syntax is for instance "
        errMsg += "'mysql://USER:PASSWORD@DBMS_IP:DBMS_PORT/DATABASE_NAME' "
        errMsg += "or 'access://DATABASE_FILEPATH'"
        raise SqlmapSyntaxException, errMsg

    for dbmsName, data in DBMS_DICT.items():
        if conf.dbms in data[0]:
            try:
                if dbmsName in (DBMS.ACCESS, DBMS.SQLITE, DBMS.FIREBIRD):
                    if remote:
                        warnMsg = "direct connection over the network for "
                        warnMsg += "%s DBMS is not supported" % dbmsName
                        logger.warn(warnMsg)

                        conf.hostname = "localhost"
                        conf.port = 0
                elif not remote:
                        errMsg = "missing remote connection details"
                        raise SqlmapSyntaxException, errMsg

                if dbmsName in (DBMS.MSSQL, DBMS.SYBASE):
                    import _mssql
                    import pymssql

                    if not hasattr(pymssql, "__version__") or pymssql.__version__ < "1.0.2":
                        errMsg = "'%s' third-party library must be " % data[1]
                        errMsg += "version >= 1.0.2 to work properly. "
                        errMsg += "Download from '%s'" % data[2]
                        raise SqlmapMissingDependence, errMsg

                elif dbmsName == DBMS.MYSQL:
                    import pymysql
                elif dbmsName == DBMS.PGSQL:
                    import psycopg2
                elif dbmsName == DBMS.ORACLE:
                    import cx_Oracle
                elif dbmsName == DBMS.SQLITE:
                    import sqlite3
                elif dbmsName == DBMS.ACCESS:
                    import pyodbc
                elif dbmsName == DBMS.FIREBIRD:
                    import kinterbasdb
            except ImportError:
                errMsg = "sqlmap requires '%s' third-party library " % data[1]
                errMsg += "in order to directly connect to the database "
                errMsg += "%s. Download from '%s'" % (dbmsName, data[2])
                raise SqlmapMissingDependence, errMsg

def parseTargetUrl():
    """
    Parse target url and set some attributes into the configuration singleton.
    """

    if not conf.url:
        return

    originalUrl = conf.url

    if re.search("\[.+\]", conf.url) and not socket.has_ipv6:
        errMsg = "IPv6 addressing is not supported "
        errMsg += "on this platform"
        raise SqlmapGenericException, errMsg

    if not re.search("^http[s]*://", conf.url, re.I):
        if ":443/" in conf.url:
            conf.url = "https://" + conf.url
        else:
            conf.url = "http://" + conf.url

    if CUSTOM_INJECTION_MARK_CHAR in conf.url:
        conf.url = conf.url.replace('?', URI_QUESTION_MARKER)

    urlSplit = urlparse.urlsplit(conf.url)
    hostnamePort = urlSplit[1].split(":") if not re.search("\[.+\]", urlSplit[1]) else filter(None, (re.search("\[.+\]", urlSplit[1]).group(0), re.search("\](:(?P<port>\d+))?", urlSplit[1]).group("port")))

    conf.scheme = urlSplit[0].strip().lower() if not conf.forceSSL else "https"
    conf.path = urlSplit[2].strip()
    conf.hostname = hostnamePort[0].strip()

    conf.ipv6 = conf.hostname != conf.hostname.strip("[]")
    conf.hostname = conf.hostname.strip("[]")

    try:
        _ = conf.hostname.encode("idna")
    except UnicodeError:
        _ = None

    if any((_ is None, re.search(r'\s', conf.hostname), '..' in conf.hostname, conf.hostname.startswith('.'))):
        errMsg = "invalid target url"
        raise SqlmapSyntaxException, errMsg

    if len(hostnamePort) == 2:
        try:
            conf.port = int(hostnamePort[1])
        except:
            errMsg = "invalid target url"
            raise SqlmapSyntaxException, errMsg
    elif conf.scheme == "https":
        conf.port = 443
    else:
        conf.port = 80

    if urlSplit[3]:
        conf.parameters[PLACE.GET] = urldecode(urlSplit[3]) if urlSplit[3] and urlencode(DEFAULT_GET_POST_DELIMITER, None) not in urlSplit[3] else urlSplit[3]

    conf.url = getUnicode("%s://%s:%d%s" % (conf.scheme, ("[%s]" % conf.hostname) if conf.ipv6 else conf.hostname, conf.port, conf.path))
    conf.url = conf.url.replace(URI_QUESTION_MARKER, '?')

    if not conf.referer and intersect(REFERER_ALIASES, conf.testParameter, True):
        debugMsg = "setting the HTTP Referer header to the target url"
        logger.debug(debugMsg)
        conf.httpHeaders = filter(lambda (key, value): key != HTTPHEADER.REFERER, conf.httpHeaders)
        conf.httpHeaders.append((HTTPHEADER.REFERER, conf.url))

    if not conf.host and intersect(HOST_ALIASES, conf.testParameter, True):
        debugMsg = "setting the HTTP Host header to the target url"
        logger.debug(debugMsg)
        conf.httpHeaders = filter(lambda (key, value): key != HTTPHEADER.HOST, conf.httpHeaders)
        conf.httpHeaders.append((HTTPHEADER.HOST, getHostHeader(conf.url)))

    if originalUrl != conf.url:
        kb.originalUrls[conf.url] = originalUrl

def expandAsteriskForColumns(expression):
    """
    If the user provided an asterisk rather than the column(s)
    name, sqlmap will retrieve the columns itself and reprocess
    the SQL query string (expression)
    """

    asterisk = re.search("^SELECT\s+\*\s+FROM\s+([\w\.\_]+)\s*", expression, re.I)

    if asterisk:
        infoMsg = "you did not provide the fields in your query. "
        infoMsg += "sqlmap will retrieve the column names itself"
        logger.info(infoMsg)

        dbTbl = asterisk.group(1)

        if dbTbl and ".." in dbTbl:
            dbTbl = dbTbl.replace('..', '.dbo.')

        if dbTbl and "." in dbTbl:
            conf.db, conf.tbl = dbTbl.split(".", 1)
        else:
            conf.tbl = dbTbl

        columnsDict = conf.dbmsHandler.getColumns(onlyColNames=True)

        if columnsDict and conf.db in columnsDict and conf.tbl in columnsDict[conf.db]:
            columns = columnsDict[conf.db][conf.tbl].keys()
            columns.sort()
            columnsStr = ", ".join(column for column in columns)
            expression = expression.replace("*", columnsStr, 1)

            infoMsg = "the query with column names is: "
            infoMsg += "%s" % expression
            logger.info(infoMsg)

    return expression

def getLimitRange(count, dump=False, plusOne=False):
    """
    Returns range of values used in limit/offset constructs
    """

    retVal = None
    count = int(count)
    limitStart, limitStop = 1, count

    if dump:
        if isinstance(conf.limitStop, int) and conf.limitStop > 0 and conf.limitStop < limitStop:
            limitStop = conf.limitStop

        if isinstance(conf.limitStart, int) and conf.limitStart > 0 and conf.limitStart <= limitStop:
            limitStart = conf.limitStart

    retVal = xrange(limitStart, limitStop + 1) if plusOne else xrange(limitStart - 1, limitStop)

    return retVal

def parseUnionPage(page):
    """
    Returns resulting items from union query inside provided page content
    """

    if page is None:
        return None

    if page.startswith(kb.chars.start) and page.endswith(kb.chars.stop):
        if len(page) > LARGE_OUTPUT_THRESHOLD:
            warnMsg = "large output detected. This might take a while"
            logger.warn(warnMsg)

        data = BigArray()
        keys = set()

        for match in re.finditer("%s(.*?)%s" % (kb.chars.start, kb.chars.stop), page, re.DOTALL | re.IGNORECASE):
            entry = match.group(1)

            if kb.chars.start in entry:
                entry = entry.split(kb.chars.start)[-1]

            if kb.unionDuplicates:
                key = entry.lower()
                if key not in keys:
                    keys.add(key)
                else:
                    continue

            entry = entry.split(kb.chars.delimiter)

            if conf.hexConvert:
                entry = applyFunctionRecursively(entry, decodeHexValue)

            if kb.safeCharEncode:
                entry = applyFunctionRecursively(entry, safecharencode)

            data.append(entry[0] if len(entry) == 1 else entry)
    else:
        data = page

    if len(data) == 1 and isinstance(data[0], basestring):
        data = data[0]

    return data

def parseFilePaths(page):
    """
    Detects (possible) absolute system paths inside the provided page content
    """

    if page:
        for regex in (r" in <b>(?P<result>.*?)</b> on line", r"(?:>|\s)(?P<result>[A-Za-z]:[\\/][\w.\\/]*)", r"(?:>|\s)(?P<result>/\w[/\w.]+)"):
            for match in re.finditer(regex, page):
                absFilePath = match.group("result").strip()
                page = page.replace(absFilePath, "")

                if isWindowsDriveLetterPath(absFilePath):
                    absFilePath = posixToNtSlashes(absFilePath)

                if absFilePath not in kb.absFilePaths:
                    kb.absFilePaths.add(absFilePath)

def getLocalIP():
    retVal = None

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((conf.hostname, conf.port))
        retVal, _ = s.getsockname()
        s.close()
    except:
        debugMsg = "there was an error in opening socket "
        debugMsg += "connection toward '%s'" % conf.hostname
        logger.debug(debugMsg)

    return retVal

def getRemoteIP():
    return socket.gethostbyname(conf.hostname)

def getFileType(filePath):
    try:
        _ = magic.from_file(filePath)
    except:
        return "unknown"

    return "text" if "ASCII" in _ or "text" in _ else "binary"

def getCharset(charsetType=None):
    asciiTbl = []

    if charsetType is None:
        asciiTbl.extend(xrange(0, 128))

    # 0 or 1
    elif charsetType == CHARSET_TYPE.BINARY:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(47, 50))

    # Digits
    elif charsetType == CHARSET_TYPE.DIGITS:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(47, 58))

    # Hexadecimal
    elif charsetType == CHARSET_TYPE.HEXADECIMAL:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(47, 58))
        asciiTbl.extend(xrange(64, 71))
        asciiTbl.extend([87, 88])  # X
        asciiTbl.extend(xrange(96, 103))
        asciiTbl.extend([119, 120])  # x

    # Characters
    elif charsetType == CHARSET_TYPE.ALPHA:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(64, 91))
        asciiTbl.extend(xrange(96, 123))

    # Characters and digits
    elif charsetType == CHARSET_TYPE.ALPHANUM:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(47, 58))
        asciiTbl.extend(xrange(64, 91))
        asciiTbl.extend(xrange(96, 123))

    return asciiTbl

def searchEnvPath(filename):
    retVal = None
    path = os.environ.get("PATH", "")
    paths = path.split(";") if IS_WIN else path.split(":")

    for _ in paths:
        _ = _.replace(";", "")
        retVal = os.path.exists(os.path.normpath(os.path.join(_, filename)))

        if retVal:
            break

    return retVal

def directoryPath(filepath):
    """
    Returns directory path for a given filepath
    """

    retVal = filepath

    if filepath:
        retVal = ntpath.dirname(filepath) if isWindowsDriveLetterPath(filepath) else posixpath.dirname(filepath)

    return retVal

def normalizePath(filepath):
    """
    Returns normalized string representation of a given filepath
    """

    retVal = filepath

    if filepath:
        retVal = ntpath.normpath(filepath) if isWindowsDriveLetterPath(filepath) else posixpath.normpath(filepath)

    return retVal

def safeStringFormat(format_, params):
    """
    Avoids problems with inappropriate string format strings
    """

    retVal = format_.replace("%d", "%s")

    if isinstance(params, basestring):
        retVal = retVal.replace("%s", params)
    else:
        count, index = 0, 0
        while index != -1:
            index = retVal.find("%s")
            if index != -1:
                if count < len(params):
                    retVal = retVal[:index] + getUnicode(params[count]) + retVal[index + 2:]
                else:
                    raise SqlmapNoneDataException, "wrong number of parameters during string formatting"
                count += 1

    return retVal

def getFilteredPageContent(page, onlyText=True):
    """
    Returns filtered page content without script, style and/or comments
    or all HTML tags
    """

    retVal = page

    # only if the page's charset has been successfully identified
    if isinstance(page, unicode):
        retVal = re.sub(r"(?si)<script.+?</script>|<!--.+?-->|<style.+?</style>%s" % (r"|<[^>]+>|\t|\n|\r" if onlyText else ""), " ", page)
        while retVal.find("  ") != -1:
            retVal = retVal.replace("  ", " ")
        retVal = htmlunescape(retVal)

    return retVal

def getPageWordSet(page):
    """
    Returns word set used in page content
    """

    retVal = set()

    # only if the page's charset has been successfully identified
    if isinstance(page, unicode):
        _ = getFilteredPageContent(page)
        retVal = set(re.findall(r"\w+", _))

    return retVal

def showStaticWords(firstPage, secondPage):
    infoMsg = "finding static words in longest matching part of dynamic page content"
    logger.info(infoMsg)

    firstPage = getFilteredPageContent(firstPage)
    secondPage = getFilteredPageContent(secondPage)

    infoMsg = "static words: "

    if firstPage and secondPage:
        match = SequenceMatcher(None, firstPage, secondPage).find_longest_match(0, len(firstPage), 0, len(secondPage))
        commonText = firstPage[match[0]:match[0] + match[2]]
        commonWords = getPageWordSet(commonText)
    else:
        commonWords = None

    if commonWords:
        commonWords = list(commonWords)
        commonWords.sort(lambda a, b: cmp(a.lower(), b.lower()))

        for word in commonWords:
            if len(word) > 2:
                infoMsg += "'%s', " % word

        infoMsg = infoMsg.rstrip(", ")
    else:
        infoMsg += "None"

    logger.info(infoMsg)

def decloakToNamedStream(filepath, name=None):
    class _(StringIO):
        __len__ = property(lambda self: self.len)
    retVal = _(decloak(filepath))
    retVal.name = name

    return retVal

def isWindowsPath(filepath):
    """
    Returns True if given filepath is in Windows format
    """

    return re.search("\A[\w]\:\\\\", filepath) is not None

def isWindowsDriveLetterPath(filepath):
    """
    Returns True if given filepath starts with a Windows drive letter
    """

    return re.search("\A[\w]\:", filepath) is not None

def posixToNtSlashes(filepath):
    """
    Replaces all occurances of Posix slashes (/) in provided
    filepath with NT ones (/)

    >>> posixToNtSlashes('C:/Windows')
    'C:\\\\Windows'
    """

    return filepath.replace('/', '\\')

def ntToPosixSlashes(filepath):
    """
    Replaces all occurances of NT slashes (\) in provided
    filepath with Posix ones (/)

    >>> ntToPosixSlashes('C:\\Windows')
    'C:/Windows'
    """

    return filepath.replace('\\', '/')

def isBase64EncodedString(subject):
    """
    Checks if the provided string is Base64 encoded

    >>> isBase64EncodedString('dGVzdA==')
    True
    >>> isBase64EncodedString('123456')
    False
    """

    return re.match(r"\A(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?\Z", subject) is not None

def isHexEncodedString(subject):
    """
    Checks if the provided string is hex encoded

    >>> isHexEncodedString('DEADBEEF')
    True
    >>> isHexEncodedString('test')
    False
    """

    return re.match(r"\A[0-9a-fA-Fx]+\Z", subject) is not None

def getConsoleWidth(default=80):
    """
    Returns console width
    """

    width = None

    if os.getenv("COLUMNS", "").isdigit():
        width = int(os.getenv("COLUMNS"))
    else:
        output=execute('stty size', shell=True, stdout=PIPE, stderr=PIPE).stdout.read()
        items = output.split()

        if len(items) == 2 and items[1].isdigit():
            width = int(items[1])

    if width is None:
        try:
            import curses

            stdscr = curses.initscr()
            _, width = stdscr.getmaxyx()
            curses.endwin()
        except:
            pass

    return width or default

def clearConsoleLine(forceOutput=False):
    """
    Clears current console line
    """

    dataToStdout("\r%s\r" % (" " * (getConsoleWidth() - 1)), forceOutput)

    kb.prependFlag = False
    kb.stickyLevel = None

def parseXmlFile(xmlFile, handler):
    """
    Parses XML file by a given handler
    """

    with contextlib.closing(StringIO(readCachedFileContent(xmlFile))) as stream:
        parse(stream, handler)

def getSQLSnippet(dbms, sfile, **variables):
    """
    Returns content of SQL snippet located inside 'procs/' directory
    """

    if sfile.endswith('.sql') and os.path.exists(sfile):
        filename = sfile
    elif not sfile.endswith('.sql') and os.path.exists("%s.sql" % sfile):
        filename = "%s.sql" % sfile
    else:
        filename = os.path.join(paths.SQLMAP_PROCS_PATH, DBMS_DIRECTORY_DICT[dbms], sfile if sfile.endswith('.sql') else "%s.sql" % sfile)
        checkFile(filename)

    retVal = readCachedFileContent(filename)
    retVal = re.sub(r"#.+", "", retVal)
    retVal = re.sub(r"(?s);\s+", "; ", retVal).strip("\r\n")

    for _ in variables.keys():
        retVal = re.sub(r"%%%s%%" % _, variables[_], retVal)

    for _ in re.findall(r"%RANDSTR\d+%", retVal, re.I):
        retVal = retVal.replace(_, randomStr())

    for _ in re.findall(r"%RANDINT\d+%", retVal, re.I):
        retVal = retVal.replace(_, randomInt())

    variables = re.findall(r"%(\w+)%", retVal, re.I)

    if variables:
        errMsg = "unresolved variable%s '%s' in SQL file '%s'" % ("s" if len(variables) > 1 else "", ", ".join(variables), sfile)
        logger.error(errMsg)

        msg = "do you want to provide the substitution values? [y/N] "
        choice = readInput(msg, default="N")

        if choice and choice[0].lower() == "y":
            for var in variables:
                msg = "insert value for variable '%s': " % var
                val = readInput(msg)
                retVal = retVal.replace(r"%%%s%%" % var, val)

    return retVal

def readCachedFileContent(filename, mode='rb'):
    """
    Cached reading of file content (avoiding multiple same file reading)
    """

    if filename not in kb.cache.content:
        with kb.locks.cache:
            if filename not in kb.cache.content:
                checkFile(filename)
                with codecs.open(filename, mode, UNICODE_ENCODING) as f:
                    kb.cache.content[filename] = f.read()

    return kb.cache.content[filename]

def readXmlFile(xmlFile):
    """
    Reads XML file content and returns its DOM representation
    """

    checkFile(xmlFile)

    with codecs.open(xmlFile, 'r', UNICODE_ENCODING) as f:
        retVal = minidom.parse(f).documentElement

    return retVal

def stdev(values):
    """
    Computes standard deviation of a list of numbers.
    Reference: http://www.goldb.org/corestats.html
    """

    if not values or len(values) < 2:
        return None

    key = (values[0], values[-1], len(values))

    if key in kb.cache.stdev:
        retVal = kb.cache.stdev[key]
    else:
        avg = average(values)
        _ = reduce(lambda x, y: x + pow((y or 0) - avg, 2), values, 0.0)
        retVal = sqrt(_ / (len(values) - 1))
        kb.cache.stdev[key] = retVal

    return retVal

def average(values):
    """
    Computes the arithmetic mean of a list of numbers.
    """

    return (sum(values) / len(values)) if values else None

def calculateDeltaSeconds(start):
    """
    Returns elapsed time from start till now
    """

    return time.time() - start

def initCommonOutputs():
    """
    Initializes dictionary containing common output values used by "good samaritan" feature
    """

    kb.commonOutputs = {}
    key = None

    with codecs.open(paths.COMMON_OUTPUTS, 'r', UNICODE_ENCODING) as f:
        for line in f.readlines():  # xreadlines doesn't return unicode strings when codec.open() is used
            if line.find('#') != -1:
                line = line[:line.find('#')]

            line = line.strip()

            if len(line) > 1:
                if line.startswith('[') and line.endswith(']'):
                    key = line[1:-1]
                elif key:
                    if key not in kb.commonOutputs:
                        kb.commonOutputs[key] = set()

                    if line not in kb.commonOutputs[key]:
                        kb.commonOutputs[key].add(line)

def getFileItems(filename, commentPrefix='#', unicode_=True, lowercase=False, unique=False):
    """
    Returns newline delimited items contained inside file
    """

    retVal = list() if not unique else OrderedDict()

    checkFile(filename)

    with codecs.open(filename, 'r', UNICODE_ENCODING) if unicode_ else open(filename, 'r') as f:
        for line in (f.readlines() if unicode_ else f.xreadlines()):  # xreadlines doesn't return unicode strings when codec.open() is used
            if commentPrefix:
                if line.find(commentPrefix) != -1:
                    line = line[:line.find(commentPrefix)]

            line = line.strip()

            if not unicode_:
                try:
                    line = str.encode(line)
                except UnicodeDecodeError:
                    continue

            if line:
                if lowercase:
                    line = line.lower()

                if unique and line in retVal:
                    continue

                if unique:
                    retVal[line] = True
                else:
                    retVal.append(line)

    return retVal if not unique else retVal.keys()

def goGoodSamaritan(prevValue, originalCharset):
    """
    Function for retrieving parameters needed for common prediction (good
    samaritan) feature.

    prevValue: retrieved query output so far (e.g. 'i').

    Returns commonValue if there is a complete single match (in kb.partRun
    of txt/common-outputs.txt under kb.partRun) regarding parameter
    prevValue. If there is no single value match, but multiple, commonCharset is
    returned containing more probable characters (retrieved from matched
    values in txt/common-outputs.txt) together with the rest of charset as
    otherCharset.
    """

    if kb.commonOutputs is None:
        initCommonOutputs()

    predictionSet = set()
    commonValue = None
    commonPattern = None
    countCommonValue = 0

    # If the header (e.g. Databases) we are looking for has common
    # outputs defined
    if kb.partRun in kb.commonOutputs:
        commonPartOutputs = kb.commonOutputs[kb.partRun]
        commonPattern = commonFinderOnly(prevValue, commonPartOutputs)

        # If the longest common prefix is the same as previous value then
        # do not consider it
        if commonPattern and commonPattern == prevValue:
            commonPattern = None

        # For each common output
        for item in commonPartOutputs:
            # Check if the common output (item) starts with prevValue
            # where prevValue is the enumerated character(s) so far
            if item.startswith(prevValue):
                commonValue = item
                countCommonValue += 1

                if len(item) > len(prevValue):
                    char = item[len(prevValue)]
                    predictionSet.add(char)

        # Reset single value if there is more than one possible common
        # output
        if countCommonValue > 1:
            commonValue = None

        commonCharset = []
        otherCharset = []

        # Split the original charset into common chars (commonCharset)
        # and other chars (otherCharset)
        for ordChar in originalCharset:
            if chr(ordChar) not in predictionSet:
                otherCharset.append(ordChar)
            else:
                commonCharset.append(ordChar)

        commonCharset.sort()

        return commonValue, commonPattern, commonCharset, originalCharset
    else:
        return None, None, None, originalCharset

def getPartRun():
    """
    Goes through call stack and finds constructs matching conf.dbmsHandler.*.
    Returns it or its alias used in txt/common-outputs.txt
    """

    retVal = None
    commonPartsDict = optDict["Enumeration"]

    try:
        stack = [item[4][0] if isinstance(item[4], list) else '' for item in inspect.stack()]

        # Goes backwards through the stack to find the conf.dbmsHandler method
        # calling this function
        for i in xrange(0, len(stack) - 1):
            for regex in (r"self\.(get[^(]+)\(\)", r"conf\.dbmsHandler\.([^(]+)\(\)"):
                match = re.search(regex, stack[i])

                if match:
                    # This is the calling conf.dbmsHandler or self method
                    # (e.g. 'getDbms')
                    retVal = match.groups()[0]
                    break

            if retVal is not None:
                break

    # Reference: http://coding.derkeiler.com/Archive/Python/comp.lang.python/2004-06/2267.html
    except TypeError:
        pass

    # Return the INI tag to consider for common outputs (e.g. 'Databases')
    return commonPartsDict[retVal][1] if isinstance(commonPartsDict.get(retVal), tuple) else retVal

def getUnicode(value, encoding=None, system=False, noneToNull=False):
    """
    Return the unicode representation of the supplied value:

    >>> getUnicode(u'test')
    u'test'
    >>> getUnicode('test')
    u'test'
    >>> getUnicode(1)
    u'1'
    """

    if noneToNull and value is None:
        return NULL

    if isListLike(value):
        value = list(getUnicode(_, encoding, system, noneToNull) for _ in value)
        return value

    if not system:
        if isinstance(value, unicode):
            return value
        elif isinstance(value, basestring):
            return unicode(value, encoding or kb.pageEncoding or UNICODE_ENCODING, "replace")
        else:
            return unicode(value)  # encoding ignored for non-basestring instances
    else:
        try:
            return getUnicode(value, sys.getfilesystemencoding() or sys.stdin.encoding)
        except:
            return getUnicode(value, UNICODE_ENCODING)

def longestCommonPrefix(*sequences):
    """
    Returns longest common prefix occuring in given sequences
    Reference: http://boredzo.org/blog/archives/2007-01-06/longest-common-prefix-in-python-2
    """

    if len(sequences) == 1:
        return sequences[0]

    sequences = [pair[1] for pair in sorted((len(fi), fi) for fi in sequences)]

    if not sequences:
        return None

    for i, comparison_ch in enumerate(sequences[0]):
        for fi in sequences[1:]:
            ch = fi[i]

            if ch != comparison_ch:
                return fi[:i]

    return sequences[0]

def commonFinderOnly(initial, sequence):
    return longestCommonPrefix(*filter(lambda x: x.startswith(initial), sequence))

def pushValue(value):
    """
    Push value to the stack (thread dependent)
    """

    getCurrentThreadData().valueStack.append(copy.deepcopy(value))

def popValue():
    """
    Pop value from the stack (thread dependent)
    """

    return getCurrentThreadData().valueStack.pop()

def wasLastRequestDBMSError():
    """
    Returns True if the last web request resulted in a (recognized) DBMS error page
    """

    threadData = getCurrentThreadData()
    return threadData.lastErrorPage and threadData.lastErrorPage[0] == threadData.lastRequestUID

def wasLastRequestHTTPError():
    """
    Returns True if the last web request resulted in an errornous HTTP code (like 500)
    """

    threadData = getCurrentThreadData()
    return threadData.lastHTTPError and threadData.lastHTTPError[0] == threadData.lastRequestUID

def wasLastRequestDelayed():
    """
    Returns True if the last web request resulted in a time-delay
    """

    # 99.9999999997440% of all non time-based SQL injection affected
    # response times should be inside +-7*stdev([normal response times])
    # Math reference: http://www.answers.com/topic/standard-deviation

    deviation = stdev(kb.responseTimes)
    threadData = getCurrentThreadData()

    if deviation and not conf.direct:
        if len(kb.responseTimes) < MIN_TIME_RESPONSES:
            warnMsg = "time-based standard deviation method used on a model "
            warnMsg += "with less than %d response times" % MIN_TIME_RESPONSES
            logger.warn(warnMsg)

        lowerStdLimit = average(kb.responseTimes) + TIME_STDEV_COEFF * deviation
        retVal = (threadData.lastQueryDuration >= lowerStdLimit)

        if not kb.testMode and retVal:
            if kb.adjustTimeDelay is None:
                msg = "do you want sqlmap to try to optimize value(s) "
                msg += "for DBMS delay responses (option '--time-sec')? [Y/n] "
                choice = readInput(msg, default='Y')
                kb.adjustTimeDelay = ADJUST_TIME_DELAY.DISABLE if choice.upper() == 'N' else ADJUST_TIME_DELAY.YES
            if kb.adjustTimeDelay is ADJUST_TIME_DELAY.YES:
                adjustTimeDelay(threadData.lastQueryDuration, lowerStdLimit)

        return retVal
    else:
        return (threadData.lastQueryDuration - conf.timeSec) >= 0

def adjustTimeDelay(lastQueryDuration, lowerStdLimit):
    """
    Provides tip for adjusting time delay in time-based data retrieval
    """

    candidate = 1 + int(round(lowerStdLimit))

    if candidate:
        kb.delayCandidates = [candidate] + kb.delayCandidates[:-1]

        if all((x == candidate for x in kb.delayCandidates)) and candidate < conf.timeSec:
            conf.timeSec = candidate

            infoMsg = "adjusting time delay to "
            infoMsg += "%d second%s due to good response times" % (conf.timeSec, 's' if conf.timeSec > 1 else '')
            logger.info(infoMsg)

def getLastRequestHTTPError():
    """
    Returns last HTTP error code
    """

    threadData = getCurrentThreadData()
    return threadData.lastHTTPError[1] if threadData.lastHTTPError else None

def extractErrorMessage(page):
    """
    Returns reported error message from page if it founds one
    """

    retVal = None

    if isinstance(page, basestring):
        for regex in ERROR_PARSING_REGEXES:
            match = re.search(regex, page, re.DOTALL | re.IGNORECASE)

            if match:
                retVal = htmlunescape(match.group("result")).replace("<br>", "\n").strip()
                break

    return retVal

def findMultipartPostBoundary(post):
    """
    Finds value for a boundary parameter in given multipart POST body
    """

    retVal = None

    done = set()
    candidates = []

    for match in re.finditer(r"(?m)^--(.+?)(--)?$", post or ""):
        _ = match.group(1)
        if _ in done:
            continue
        else:
            candidates.append((post.count(_), _))
            done.add(_)

    if candidates:
        candidates.sort(key=lambda _: _[0], reverse=True)
        retVal = candidates[0][1]

    return retVal

def urldecode(value, encoding=None, unsafe="%%&=;+%s" % CUSTOM_INJECTION_MARK_CHAR, convall=False):
    result = value

    if value:
        try:
            # for cases like T%C3%BCrk%C3%A7e
            value = str(value)
        except ValueError:
            pass
        finally:
            if convall:
                result = urllib.unquote_plus(value)
            else:
                def _(match):
                    charset = reduce(lambda x, y: x.replace(y, ""), unsafe, string.printable)
                    char = chr(ord(match.group(1).decode("hex")))
                    return char if char in charset else match.group(0)
                result = re.sub("%([0-9a-fA-F]{2})", _, value)
                result = result.replace("+", " ")  # plus sign has a special meaning in url encoded data (hence the usage of urllib.unquote_plus in convall case)

    if isinstance(result, str):
        result = unicode(result, encoding or UNICODE_ENCODING, "replace")

    return result

def urlencode(value, safe="%&=", convall=False, limit=False):
    if conf.direct:
        return value

    count = 0
    result = None if value is None else ""

    if value:
        if convall or safe is None:
            safe = ""

        # corner case when character % really needs to be
        # encoded (when not representing url encoded char)
        # except in cases when tampering scripts are used
        if all(map(lambda x: '%' in x, [safe, value])) and not kb.tamperFunctions:
            value = re.sub("%(?![0-9a-fA-F]{2})", "%25", value)

        while True:
            result = urllib.quote(utf8encode(value), safe)

            if limit and len(result) > URLENCODE_CHAR_LIMIT:
                if count >= len(URLENCODE_FAILSAFE_CHARS):
                    break

                while count < len(URLENCODE_FAILSAFE_CHARS):
                    safe += URLENCODE_FAILSAFE_CHARS[count]
                    count += 1
                    if safe[-1] in value:
                        break
            else:
                break

    return result

def runningAsAdmin():
    """
    Returns True if the current process is run under admin privileges
    """

    isAdmin = None

    if PLATFORM in ("posix", "mac"):
        _ = os.geteuid()

        isAdmin = isinstance(_, (int, float, long)) and _ == 0
    elif IS_WIN:
        _ = ctypes.windll.shell32.IsUserAnAdmin()

        isAdmin = isinstance(_, (int, float, long)) and _ == 1
    else:
        errMsg = "sqlmap is not able to check if you are running it "
        errMsg += "as an administrator account on this platform. "
        errMsg += "sqlmap will assume that you are an administrator "
        errMsg += "which is mandatory for the requested takeover attack "
        errMsg += "to work properly"
        logger.error(errMsg)

        isAdmin = True

    return isAdmin

def logHTTPTraffic(requestLogMsg, responseLogMsg):
    """
    Logs HTTP traffic to the output file
    """

    if not conf.trafficFile:
        return

    with kb.locks.log:
        dataToTrafficFile("%s%s" % (requestLogMsg, os.linesep))
        dataToTrafficFile("%s%s" % (responseLogMsg, os.linesep))
        dataToTrafficFile("%s%s%s%s" % (os.linesep, 76 * '#', os.linesep, os.linesep))

def getPageTemplate(payload, place):  # Cross-linked function
    pass

def getPublicTypeMembers(type_, onlyValues=False):
    """
    Useful for getting members from types (e.g. in enums)
    """

    for name, value in inspect.getmembers(type_):
        if not name.startswith('__'):
            if not onlyValues:
                yield (name, value)
            else:
                yield value

def enumValueToNameLookup(type_, value_):
    """
    Returns name of a enum member with a given value
    """

    retVal = None

    for name, value in getPublicTypeMembers(type_):
        if value == value_:
            retVal = name
            break

    return retVal

def extractRegexResult(regex, content, flags=0):
    """
    Returns 'result' group value from a possible match with regex on a given
    content
    """

    retVal = None

    if regex and content and '?P<result>' in regex:
        match = re.search(regex, content, flags)

        if match:
            retVal = match.group("result")

    return retVal

def extractTextTagContent(page):
    """
    Returns list containing content from "textual" tags
    """

    page = re.sub(r"(?si)[^\s>]*%s[^<]*" % REFLECTED_VALUE_MARKER, "", page or "")
    return filter(None, (_.group('result').strip() for _ in re.finditer(TEXT_TAG_REGEX, page)))

def trimAlphaNum(value):
    """
    Trims alpha numeric characters from start and ending of a given value
    """

    while value and value[-1].isalnum():
        value = value[:-1]

    while value and value[0].isalnum():
        value = value[1:]

    return value

def isNumPosStrValue(value):
    """
    Returns True if value is a string (or integer) with a positive integer representation
    """

    return (value and isinstance(value, basestring) and value.isdigit() and value != "0") or (isinstance(value, int) and value != 0)

@cachedmethod
def aliasToDbmsEnum(dbms):
    """
    Returns major DBMS name from a given alias
    """

    retVal = None

    if dbms:
        for key, item in DBMS_DICT.items():
            if dbms.lower() in item[0] or dbms.lower() == key.lower():
                retVal = key
                break

    return retVal

def findDynamicContent(firstPage, secondPage):
    """
    This function checks if the provided pages have dynamic content. If they
    are dynamic, proper markings will be made
    """

    infoMsg = "searching for dynamic content"
    logger.info(infoMsg)

    blocks = SequenceMatcher(None, firstPage, secondPage).get_matching_blocks()
    kb.dynamicMarkings = []

    # Removing too small matching blocks
    for block in blocks[:]:
        (_, _, length) = block

        if length <= DYNAMICITY_MARK_LENGTH:
            blocks.remove(block)

    # Making of dynamic markings based on prefix/suffix principle
    if len(blocks) > 0:
        blocks.insert(0, None)
        blocks.append(None)

        for i in xrange(len(blocks) - 1):
            prefix = firstPage[blocks[i][0]:blocks[i][0] + blocks[i][2]] if blocks[i] else None
            suffix = firstPage[blocks[i + 1][0]:blocks[i + 1][0] + blocks[i + 1][2]] if blocks[i + 1] else None

            if prefix is None and blocks[i + 1][0] == 0:
                continue

            if suffix is None and (blocks[i][0] + blocks[i][2] >= len(firstPage)):
                continue

            prefix = trimAlphaNum(prefix)
            suffix = trimAlphaNum(suffix)

            kb.dynamicMarkings.append((re.escape(prefix[-DYNAMICITY_MARK_LENGTH / 2:]) if prefix else None, re.escape(suffix[:DYNAMICITY_MARK_LENGTH / 2]) if suffix else None))

    if len(kb.dynamicMarkings) > 0:
        infoMsg = "dynamic content marked for removal (%d region%s)" % (len(kb.dynamicMarkings), 's' if len(kb.dynamicMarkings) > 1 else '')
        logger.info(infoMsg)

def removeDynamicContent(page):
    """
    Removing dynamic content from supplied page basing removal on
    precalculated dynamic markings
    """

    if page:
        for item in kb.dynamicMarkings:
            prefix, suffix = item

            if prefix is None and suffix is None:
                continue
            elif prefix is None:
                page = re.sub(r'(?s)^.+%s' % suffix, suffix, page)
            elif suffix is None:
                page = re.sub(r'(?s)%s.+$' % prefix, prefix, page)
            else:
                page = re.sub(r'(?s)%s.+%s' % (prefix, suffix), '%s%s' % (prefix, suffix), page)

    return page

def filterStringValue(value, regex, replacement=""):
    """
    Returns string value consisting only of chars satisfying supplied
    regular expression (note: it has to be in form [...])
    """

    retVal = value

    if value:
        retVal = re.sub(regex.replace("[", "[^") if "[^" not in regex else regex.replace("[^", "["), replacement, value)

    return retVal

def filterControlChars(value):
    """
    Returns string value with control chars being supstituted with ' '
    """

    return filterStringValue(value, PRINTABLE_CHAR_REGEX, ' ')

def isDBMSVersionAtLeast(version):
    """
    Checks if the recognized DBMS version is at least the version
    specified
    """

    retVal = None

    if Backend.getVersion() and Backend.getVersion() != UNKNOWN_DBMS_VERSION:
        value = Backend.getVersion().replace(" ", "").rstrip('.')

        while True:
            index = value.find('.', value.find('.') + 1)

            if index > -1:
                value = value[0:index] + value[index + 1:]
            else:
                break

        value = filterStringValue(value, '[0-9.><=]')

        if isinstance(value, basestring):
            if value.startswith(">="):
                value = float(value.replace(">=", ""))
            elif value.startswith(">"):
                value = float(value.replace(">", "")) + 0.01
            elif value.startswith("<="):
                value = float(value.replace("<=", ""))
            elif value.startswith(">"):
                value = float(value.replace("<", "")) - 0.01

        retVal = getUnicode(value) >= getUnicode(version)

    return retVal

def parseSqliteTableSchema(value):
    """
    Parses table column names and types from specified SQLite table schema
    """

    if value:
        table = {}
        columns = {}

        for match in re.finditer(r"(\w+)\s+(TEXT|NUMERIC|INTEGER|REAL|NONE)", value):
            columns[match.group(1)] = match.group(2)

        table[conf.tbl] = columns
        kb.data.cachedColumns[conf.db] = table

def getTechniqueData(technique=None):
    """
    Returns injection data for technique specified
    """

    return kb.injection.data.get(technique)

def isTechniqueAvailable(technique):
    """
    Returns True if there is injection data which sqlmap could use for
    technique specified
    """

    if conf.tech and isinstance(conf.tech, list) and technique not in conf.tech:
        return False
    else:
        return getTechniqueData(technique) is not None

def isInferenceAvailable():
    """
    Returns True whether techniques using inference technique are available
    """

    return any(isTechniqueAvailable(_) for _ in (PAYLOAD.TECHNIQUE.BOOLEAN, PAYLOAD.TECHNIQUE.STACKED, PAYLOAD.TECHNIQUE.TIME))

def setOptimize():
    """
    Sets options turned on by switch '-o'
    """

    #conf.predictOutput = True
    conf.keepAlive = True
    conf.threads = 3 if conf.threads < 3 else conf.threads
    conf.nullConnection = not any([conf.data, conf.textOnly, conf.titles, conf.string, conf.notString, conf.regexp, conf.tor])

    if not conf.nullConnection:
        debugMsg = "turning off --null-connection switch used indirectly by switch -o"
        logger.debug(debugMsg)

def initTechnique(technique=None):
    """
    Prepares data for technique specified
    """

    try:
        data = getTechniqueData(technique)
        resetCounter(technique)

        if data:
            kb.pageTemplate, kb.errorIsNone = getPageTemplate(data.templatePayload, kb.injection.place)
            kb.matchRatio = data.matchRatio
            kb.negativeLogic = (technique == PAYLOAD.TECHNIQUE.BOOLEAN) and (data.where == PAYLOAD.WHERE.NEGATIVE)

            # Restoring stored conf options
            for key, value in kb.injection.conf.items():
                if value and (not hasattr(conf, key) or (hasattr(conf, key) and not getattr(conf, key))):
                    setattr(conf, key, value)
                    debugMsg = "resuming configuration option '%s' (%s)" % (key, value)
                    logger.debug(debugMsg)

                    if value and key == "optimize":
                        setOptimize()
        else:
            warnMsg = "there is no injection data available for technique "
            warnMsg += "'%s'" % enumValueToNameLookup(PAYLOAD.TECHNIQUE, technique)
            logger.warn(warnMsg)

    except SqlmapDataException:
        errMsg = "missing data in old session file(s). "
        errMsg += "Please use '--flush-session' to deal "
        errMsg += "with this error"
        raise SqlmapNoneDataException, errMsg

def arrayizeValue(value):
    """
    Makes a list out of value if it is not already a list or tuple itself
    """

    if not isListLike(value):
        value = [value]

    return value

def unArrayizeValue(value):
    """
    Makes a value out of iterable if it is a list or tuple itself
    """

    if isListLike(value):
        value = value[0] if len(value) > 0 else None

    return value

def flattenValue(value):
    """
    Returns an iterator representing flat representation of a given value
    """

    for i in iter(value):
        if isListLike(i):
            for j in flattenValue(i):
                yield j
        else:
            yield i

def isListLike(value):
    """
    Returns True if the given value is a list-like instance
    """

    return isinstance(value, (list, tuple, set, BigArray))

def getSortedInjectionTests():
    """
    Returns prioritized test list by eventually detected DBMS from error
    messages
    """

    retVal = copy.deepcopy(conf.tests)

    def priorityFunction(test):
        retVal = SORT_ORDER.FIRST

        if test.stype == PAYLOAD.TECHNIQUE.UNION:
            retVal = SORT_ORDER.LAST

        elif 'details' in test and 'dbms' in test.details:
            if test.details.dbms in Backend.getErrorParsedDBMSes():
                retVal = SORT_ORDER.SECOND
            else:
                retVal = SORT_ORDER.THIRD

        return retVal

    if Backend.getErrorParsedDBMSes():
        retVal = sorted(retVal, key=priorityFunction)

    return retVal

def filterListValue(value, regex):
    """
    Returns list with items that have parts satisfying given regular
    expression
    """

    if isinstance(value, list) and regex:
        retVal = filter(lambda _: re.search(regex, _, re.I), value)
    else:
        retVal = value

    return retVal

def showHttpErrorCodes():
    """
    Shows all HTTP error codes raised till now
    """

    if kb.httpErrorCodes:
        warnMsg = "HTTP error codes detected during run:\n"
        warnMsg += ", ".join("%d (%s) - %d times" % (code, httplib.responses[code] \
          if code in httplib.responses else '?', count) \
          for code, count in kb.httpErrorCodes.items())
        logger.warn(warnMsg)

def getComparePageRatio(firstPage, secondPage, filtered=False):
    """
    Returns comparison ratio between two given pages
    """

    if filtered:
        (firstPage, secondPage) = map(getFilteredPageContent, (firstPage, secondPage))

    seqMatcher = getCurrentThreadData().seqMatcher
    seqMatcher.set_seq1(firstPage)
    seqMatcher.set_seq2(secondPage)

    return seqMatcher.quick_ratio()

def openFile(filename, mode='r'):
    """
    Returns file handle of a given filename
    """

    try:
        return codecs.open(filename, mode, UNICODE_ENCODING, "replace")
    except IOError:
        errMsg = "there has been a file opening error for filename '%s'. " % filename
        errMsg += "Please check %s permissions on a file " % ("write" if \
          mode and ('w' in mode or 'a' in mode or '+' in mode) else "read")
        errMsg += "and that it's not locked by another process."
        raise SqlmapFilePathException, errMsg

def decodeIntToUnicode(value):
    """
    Decodes inferenced integer value to an unicode character
    """
    retVal = value

    if isinstance(value, int):
        try:
            # http://dev.mysql.com/doc/refman/5.0/en/string-functions.html#function_ord
            if Backend.getIdentifiedDbms() in (DBMS.MYSQL,):
                retVal = getUnicode(struct.pack('B' if value < 256 else '<H', value))
            elif value > 255:
                retVal = unichr(value)
            else:
                retVal = getUnicode(chr(value))
        except:
            retVal = INFERENCE_UNKNOWN_CHAR

    return retVal

def unhandledExceptionMessage():
    """
    Returns detailed message about occured unhandled exception
    """

    errMsg = "unhandled exception in %s, retry your " % VERSION_STRING
    errMsg += "run with the latest development version from the GitHub "
    errMsg += "repository. If the exception persists, please send by e-mail "
    errMsg += "to '%s' or open a new issue at '%s' with the following text " % (ML, ISSUES_PAGE)
    errMsg += "and any information required to reproduce the bug. The "
    errMsg += "developers will try to reproduce the bug, fix it accordingly "
    errMsg += "and get back to you.\n"
    errMsg += "sqlmap version: %s%s\n" % (VERSION, "-%s" % REVISION if REVISION else "")
    errMsg += "Python version: %s\n" % PYVERSION
    errMsg += "Operating system: %s\n" % PLATFORM
    errMsg += "Command line: %s\n" % " ".join(sys.argv)
    errMsg += "Technique: %s\n" % (enumValueToNameLookup(PAYLOAD.TECHNIQUE, kb.technique) if kb.get("technique") else None)
    errMsg += "Back-end DBMS: %s" % ("%s (fingerprinted)" % Backend.getDbms() if Backend.getDbms() is not None else "%s (identified)" % Backend.getIdentifiedDbms())

    return maskSensitiveData(errMsg)

def maskSensitiveData(msg):
    """
    Masks sensitive data in the supplied message
    """

    retVal = msg

    for item in filter(None, map(lambda x: conf.get(x), ("hostname", "googleDork", "aCred", "pCred", "tbl", "db", "col", "user", "cookie", "proxy"))):
        regex = SENSITIVE_DATA_REGEX % re.sub("(\W)", r"\\\1", item)
        while extractRegexResult(regex, retVal):
            value = extractRegexResult(regex, retVal)
            retVal = retVal.replace(value, '*' * len(value))

    return retVal

def listToStrValue(value):
    """
    Flattens list to a string value

    >>> listToStrValue([1,2,3])
    '1, 2, 3'
    """

    if isinstance(value, (set, tuple)):
        value = list(value)

    if isinstance(value, list):
        retVal = value.__str__().lstrip('[').rstrip(']')
    else:
        retVal = value

    return retVal

def getExceptionFrameLocals():
    """
    Returns dictionary with local variable content from frame
    where exception has been raised
    """

    retVal = {}

    if sys.exc_info():
        trace = sys.exc_info()[2]
        while trace.tb_next:
            trace = trace.tb_next
        retVal = trace.tb_frame.f_locals

    return retVal

def intersect(valueA, valueB, lowerCase=False):
    """
    Returns intersection of the array-ized values
    """

    retVal = None

    if valueA and valueB:
        valueA = arrayizeValue(valueA)
        valueB = arrayizeValue(valueB)

        if lowerCase:
            valueA = [val.lower() if isinstance(val, basestring) else val for val in valueA]
            valueB = [val.lower() if isinstance(val, basestring) else val for val in valueB]

        retVal = [val for val in valueA if val in valueB]

    return retVal

def cpuThrottle(value):
    """
    Does a CPU throttling for lesser CPU consumption
    """

    delay = 0.00001 * (value ** 2)
    time.sleep(delay)

def removeReflectiveValues(content, payload, suppressWarning=False):
    """
    Neutralizes reflective values in a given content based on a payload
    (e.g. ..search.php?q=1 AND 1=2 --> "...searching for <b>1%20AND%201%3D2</b>..." --> "...searching for <b>__REFLECTED_VALUE__</b>...")
    """

    retVal = content

    if all([content, payload]) and isinstance(content, unicode) and kb.reflectiveMechanism:
        def _(value):
            while 2 * REFLECTED_REPLACEMENT_REGEX in value:
                value = value.replace(2 * REFLECTED_REPLACEMENT_REGEX, REFLECTED_REPLACEMENT_REGEX)
            return value

        payload = getUnicode(urldecode(payload.replace(PAYLOAD_DELIMITER, ''), convall=True))
        regex = _(filterStringValue(payload, r"[A-Za-z0-9]", REFLECTED_REPLACEMENT_REGEX.encode("string-escape")))

        if regex != payload:
            if all(part.lower() in content.lower() for part in filter(None, regex.split(REFLECTED_REPLACEMENT_REGEX))[1:]):  # fast optimization check
                parts = regex.split(REFLECTED_REPLACEMENT_REGEX)
                retVal = content.replace(payload, REFLECTED_VALUE_MARKER)  # dummy approach

                if len(parts) > REFLECTED_MAX_REGEX_PARTS:  # preventing CPU hogs
                    regex = _("%s%s%s" % (REFLECTED_REPLACEMENT_REGEX.join(parts[:REFLECTED_MAX_REGEX_PARTS / 2]), REFLECTED_REPLACEMENT_REGEX, REFLECTED_REPLACEMENT_REGEX.join(parts[-REFLECTED_MAX_REGEX_PARTS / 2:])))

                parts = filter(None, regex.split(REFLECTED_REPLACEMENT_REGEX))

                if regex.startswith(REFLECTED_REPLACEMENT_REGEX):
                    regex = r"%s%s" % (REFLECTED_BORDER_REGEX, regex[len(REFLECTED_REPLACEMENT_REGEX):])
                else:
                    regex = r"\b%s" % regex

                if regex.endswith(REFLECTED_REPLACEMENT_REGEX):
                    regex = r"%s%s" % (regex[:-len(REFLECTED_REPLACEMENT_REGEX)], REFLECTED_BORDER_REGEX)
                else:
                    regex = r"%s\b" % regex

                retVal = re.sub(r"(?i)%s" % regex, REFLECTED_VALUE_MARKER, retVal)

                if len(parts) > 2:
                    regex = REFLECTED_REPLACEMENT_REGEX.join(parts[1:])
                    retVal = re.sub(r"(?i)\b%s\b" % regex, REFLECTED_VALUE_MARKER, retVal)

            if retVal != content:
                kb.reflectiveCounters[REFLECTIVE_COUNTER.HIT] += 1
                if not suppressWarning:
                    warnMsg = "reflective value(s) found and filtering out"
                    singleTimeWarnMessage(warnMsg)

                if re.search(r"FRAME[^>]+src=[^>]*%s" % REFLECTED_VALUE_MARKER, retVal, re.I):
                    warnMsg = "frames detected containing attacked parameter values. Please be sure to "
                    warnMsg += "test those separately in case that attack on this page fails"
                    singleTimeWarnMessage(warnMsg)

            elif not kb.testMode and not kb.reflectiveCounters[REFLECTIVE_COUNTER.HIT]:
                kb.reflectiveCounters[REFLECTIVE_COUNTER.MISS] += 1
                if kb.reflectiveCounters[REFLECTIVE_COUNTER.MISS] > REFLECTIVE_MISS_THRESHOLD:
                    kb.reflectiveMechanism = False
                    if not suppressWarning:
                        debugMsg = "turning off reflection removal mechanism (for optimization purposes)"
                        logger.debug(debugMsg)

    return retVal

def normalizeUnicode(value):
    """
    Does an ASCII normalization of unicode strings
    Reference: http://www.peterbe.com/plog/unicode-to-ascii
    """

    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore') if isinstance(value, unicode) else value

def safeSQLIdentificatorNaming(name, isTable=False):
    """
    Returns a safe representation of SQL identificator name (internal data format)
    Reference: http://stackoverflow.com/questions/954884/what-special-characters-are-allowed-in-t-sql-column-retVal
    """

    retVal = name

    if isinstance(name, basestring):
        retVal = getUnicode(name)
        _ = isTable and Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE)

        if _:
            retVal = re.sub(r"(?i)\A%s\." % DEFAULT_MSSQL_SCHEMA, "", retVal)

        if not re.match(r"\A[A-Za-z0-9_@%s\$]+\Z" % ("." if _ else ""), retVal):  # MsSQL is the only DBMS where we automatically prepend schema to table name (dot is normal)
            if Backend.getIdentifiedDbms() in (DBMS.MYSQL, DBMS.ACCESS):
                retVal = "`%s`" % retVal.strip("`")
            elif Backend.getIdentifiedDbms() in (DBMS.ORACLE, DBMS.PGSQL, DBMS.DB2):
                retVal = "\"%s\"" % retVal.strip("\"")
            elif Backend.getIdentifiedDbms() in (DBMS.MSSQL,):
                retVal = "[%s]" % retVal.strip("[]")

        if _ and DEFAULT_MSSQL_SCHEMA not in retVal and '.' not in re.sub(r"\[[^]]+\]", "", retVal):
            retVal = "%s.%s" % (DEFAULT_MSSQL_SCHEMA, retVal)

    return retVal

def unsafeSQLIdentificatorNaming(name):
    """
    Extracts identificator's name from its safe SQL representation
    """

    retVal = name

    if isinstance(name, basestring):
        if Backend.getIdentifiedDbms() in (DBMS.MYSQL, DBMS.ACCESS):
            retVal = name.replace("`", "")
        elif Backend.getIdentifiedDbms() in (DBMS.ORACLE, DBMS.PGSQL, DBMS.DB2):
            retVal = name.replace("\"", "")
        elif Backend.getIdentifiedDbms() in (DBMS.MSSQL,):
            retVal = name.replace("[", "").replace("]", "")

        if Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE):
            prefix = "%s." % DEFAULT_MSSQL_SCHEMA
            if retVal.startswith(prefix):
                retVal = retVal[len(prefix):]

    return retVal

def isBinaryData(value):
    """
    Tests given value for binary content
    """

    retVal = False
    if isinstance(value, basestring):
        retVal = reduce(lambda x, y: x or not (y in string.printable or ord(y) > 255), value, False)
    return retVal

def isNoneValue(value):
    """
    Returns whether the value is unusable (None or '')
    """

    if isinstance(value, basestring):
        return value in ("None", "")
    elif isListLike(value):
        return all(isNoneValue(_) for _ in value)
    elif isinstance(value, dict):
        return not any(value)
    else:
        return value is None

def isNullValue(value):
    """
    Returns whether the value contains explicit 'NULL' value
    """

    return isinstance(value, basestring) and value.upper() == NULL

def expandMnemonics(mnemonics, parser, args):
    """
    Expands mnemonic options
    """

    class MnemonicNode(object):
        def __init__(self):
            self.next = {}
            self.current = []

    head = MnemonicNode()
    pointer = None

    for group in parser.option_groups:
        for option in group.option_list:
            for opt in option._long_opts + option._short_opts:
                pointer = head

                for char in opt:
                    if char == "-":
                        continue
                    elif char not in pointer.next:
                        pointer.next[char] = MnemonicNode()

                    pointer = pointer.next[char]
                    pointer.current.append(option)

    for mnemonic in mnemonics.split(','):
        found = None
        name = mnemonic.split('=')[0].replace("-", "").strip()
        value = mnemonic.split('=')[1] if len(mnemonic.split('=')) > 1 else None
        pointer = head

        for char in name:
            if char in pointer.next:
                pointer = pointer.next[char]
            else:
                pointer = None
                break

        if pointer in (None, head):
            errMsg = "mnemonic '%s' can't be resolved to any parameter name" % name
            raise SqlmapSyntaxException, errMsg

        elif len(pointer.current) > 1:
            options = {}

            for option in pointer.current:
                for opt in option._long_opts + option._short_opts:
                    opt = opt.strip('-')
                    if opt.startswith(name):
                        options[opt] = option

            if name in options:
                found = name
                debugMsg = "mnemonic '%s' resolved to %s). " % (name, found)
                logger.debug(debugMsg)
            else:
                found = sorted(options.keys(), key=lambda x: len(x))[0]
                warnMsg = "detected ambiguity (mnemonic '%s' can be resolved to: %s). " % (name, ", ".join("'%s'" % key for key in options.keys()))
                warnMsg += "Resolved to shortest of those ('%s')" % found
                logger.warn(warnMsg)

            found = options[found]
        else:
            found = pointer.current[0]
            debugMsg = "mnemonic '%s' resolved to %s). " % (name, found)
            logger.debug(debugMsg)

        if found:
            try:
                value = found.convert_value(found, value)
            except OptionValueError:
                value = None

            if value is not None:
                setattr(args, found.dest, value)
            elif not found.type:  # boolean
                setattr(args, found.dest, True)
            else:
                errMsg = "mnemonic '%s' requires value of type '%s'" % (name, found.type)
                raise SqlmapSyntaxException, errMsg

def safeCSValue(value):
    """
    Returns value safe for CSV dumping
    Reference: http://tools.ietf.org/html/rfc4180
    """

    retVal = value

    if retVal and isinstance(retVal, basestring):
        if not (retVal[0] == retVal[-1] == '"'):
            if any(_ in retVal for _ in (conf.csvDel, '"', '\n')):
                retVal = '"%s"' % retVal.replace('"', '""')

    return retVal

def filterPairValues(values):
    """
    Returns only list-like values with length 2
    """

    retVal = []

    if not isNoneValue(values) and hasattr(values, '__iter__'):
        retVal = filter(lambda x: isinstance(x, (tuple, list, set)) and len(x) == 2, values)

    return retVal

def randomizeParameterValue(value):
    """
    Randomize a parameter value based on occurances of alphanumeric characters
    """

    retVal = value

    for match in re.finditer('[A-Z]+', value):
        retVal = retVal.replace(match.group(), randomStr(len(match.group())).upper())

    for match in re.finditer('[a-z]+', value):
        retVal = retVal.replace(match.group(), randomStr(len(match.group())).lower())

    for match in re.finditer('[0-9]+', value):
        retVal = retVal.replace(match.group(), str(randomInt(len(match.group()))))

    return retVal

def asciifyUrl(url, forceQuote=False):
    """
    Attempts to make a unicode url usuable with ``urllib/urllib2``.

    More specifically, it attempts to convert the unicode object ``url``,
    which is meant to represent a IRI, to an unicode object that,
    containing only ASCII characters, is a valid URI. This involves:

        * IDNA/Puny-encoding the domain name.
        * UTF8-quoting the path and querystring parts.

    See also RFC 3987.

    Reference: http://blog.elsdoerfer.name/2008/12/12/opening-iris-in-python/
    """

    parts = urlparse.urlsplit(url)
    if not parts.scheme or not parts.netloc:
        # apparently not an url
        return url

    if all(char in string.printable for char in url):
        return url

    # idna-encode domain
    hostname = parts.hostname.encode("idna")

    # UTF8-quote the other parts. We check each part individually if
    # if needs to be quoted - that should catch some additional user
    # errors, say for example an umlaut in the username even though
    # the path *is* already quoted.
    def quote(s, safe):
        s = s or ''
        # Triggers on non-ascii characters - another option would be:
        #     urllib.quote(s.replace('%', '')) != s.replace('%', '')
        # which would trigger on all %-characters, e.g. "&".
        if s.encode("ascii", "replace") != s or forceQuote:
            return urllib.quote(s.encode(UNICODE_ENCODING), safe=safe)
        return s

    username = quote(parts.username, '')
    password = quote(parts.password, safe='')
    path = quote(parts.path, safe='/')
    query = quote(parts.query, safe="&=")

    # put everything back together
    netloc = hostname
    if username or password:
        netloc = '@' + netloc
        if password:
            netloc = ':' + password + netloc
        netloc = username + netloc

    if parts.port:
        netloc += ':' + str(parts.port)

    return urlparse.urlunsplit([parts.scheme, netloc, path, query, parts.fragment])

def isAdminFromPrivileges(privileges):
    """
    Inspects privileges to see if those are comming from an admin user
    """

    # In PostgreSQL the usesuper privilege means that the
    # user is DBA
    retVal = (Backend.isDbms(DBMS.PGSQL) and "super" in privileges)

    # In Oracle the DBA privilege means that the
    # user is DBA
    retVal |= (Backend.isDbms(DBMS.ORACLE) and "DBA" in privileges)

    # In MySQL >= 5.0 the SUPER privilege means
    # that the user is DBA
    retVal |= (Backend.isDbms(DBMS.MYSQL) and kb.data.has_information_schema and "SUPER" in privileges)

    # In MySQL < 5.0 the super_priv privilege means
    # that the user is DBA
    retVal |= (Backend.isDbms(DBMS.MYSQL) and not kb.data.has_information_schema and "super_priv" in privileges)

    # In Firebird there is no specific privilege that means
    # that the user is DBA
    # TODO: confirm
    retVal |= (Backend.isDbms(DBMS.FIREBIRD) and "SELECT" in privileges and "INSERT" in privileges and "UPDATE" in privileges and "DELETE" in privileges and "REFERENCES" in privileges and "EXECUTE" in privileges)

    return retVal

def findPageForms(content, url, raise_=False, addToTargets=False):
    """
    Parses given page content for possible forms
    """

    class _(StringIO):
        def __init__(self, content, url):
            StringIO.__init__(self, unicodeencode(content, kb.pageEncoding) if isinstance(content, unicode) else content)
            self._url = url
        def geturl(self):
            return self._url

    if not content:
        errMsg = "can't parse forms as the page content appears to be blank"
        if raise_:
            raise SqlmapGenericException, errMsg
        else:
            logger.debug(errMsg)

    forms = None
    retVal = set()
    response = _(content, url)

    try:
        forms = ParseResponse(response, backwards_compat=False)
    except ParseError:
        warnMsg = "badly formed HTML at the given url ('%s'). Going to filter it" % url
        logger.warning(warnMsg)
        response.seek(0)
        filtered = _("".join(re.findall(FORM_SEARCH_REGEX, response.read())), response.geturl())
        try:
            forms = ParseResponse(filtered, backwards_compat=False)
        except ParseError:
            errMsg = "no success"
            if raise_:
                raise SqlmapGenericException, errMsg
            else:
                logger.debug(errMsg)

    if forms:
        for form in forms:
            try:
                for control in form.controls:
                    if hasattr(control, "items"):
                        # if control has selectable items select first non-disabled
                        for item in control.items:
                            if not item.disabled:
                                if not item.selected:
                                    item.selected = True
                                break

                request = form.click()
            except (ValueError, TypeError), ex:
                errMsg = "there has been a problem while "
                errMsg += "processing page forms ('%s')" % ex
                if raise_:
                    raise SqlmapGenericException, errMsg
                else:
                    logger.debug(errMsg)
            else:
                url = urldecode(request.get_full_url(), kb.pageEncoding)
                method = request.get_method()
                data = request.get_data() if request.has_data() else None
                data = urldecode(data, kb.pageEncoding) if data and urlencode(DEFAULT_GET_POST_DELIMITER, None) not in data else data

                if not data and method and method.upper() == HTTPMETHOD.POST:
                    debugMsg = "invalid POST form with blank data detected"
                    logger.debug(debugMsg)
                    continue

                target = (url, method, data, conf.cookie)
                retVal.add(target)
    else:
        errMsg = "there were no forms found at the given target url"
        if raise_:
            raise SqlmapGenericException, errMsg
        else:
            logger.debug(errMsg)

    if addToTargets and retVal:
        for target in retVal:
            url = target[0]

            # flag to know if we are dealing with the same target host
            _ = reduce(lambda x, y: x == y, map(lambda x: urlparse.urlparse(x).netloc.split(':')[0], (response.geturl(), url)))

            if conf.scope:
                if not re.search(conf.scope, url, re.I):
                    continue
            elif not _:
                continue

            kb.targets.add(target)

    return retVal

def getHostHeader(url):
    """
    Returns proper Host header value for a given target URL
    """

    retVal = url

    if url:
        retVal = urlparse.urlparse(url).netloc

        if re.search("http(s)?://\[.+\]", url, re.I):
            retVal = extractRegexResult("http(s)?://\[(?P<result>.+)\]", url)
        elif any(retVal.endswith(':%d' % _) for _ in (80, 443)):
            retVal = retVal.split(':')[0]

    return retVal

def checkDeprecatedOptions(args):
    """
    Checks for deprecated options
    """

    for _ in args:
        if _ in DEPRECATED_OPTIONS:
            errMsg = "switch/option '%s' is deprecated" % _
            if _ in DEPRECATED_HINTS:
                errMsg += " (hint: %s)" % DEPRECATED_HINTS[_]
            raise SqlmapSyntaxException, errMsg

def evaluateCode(code, variables=None):
    """
    Executes given python code given in a string form
    """

    try:
        exec(code, variables)
    except KeyboardInterrupt:
        raise
    except Exception, ex:
        errMsg = "an error occured while evaluating provided code ('%s'). " % ex
        raise SqlmapGenericException, errMsg

def serializeObject(object_):
    """
    Serializes given object
    """

    return base64pickle(object_)

def unserializeObject(value):
    """
    Unserializes object from given serialized form
    """

    return base64unpickle(value) if value else None

def resetCounter(technique):
    """
    Resets query counter for a given technique
    """

    kb.counters[technique] = 0

def incrementCounter(technique):
    """
    Increments query counter for a given technique
    """

    kb.counters[technique] = getCounter(technique) + 1

def getCounter(technique):
    """
    Returns query counter for a given technique
    """

    return kb.counters.get(technique, 0)

def applyFunctionRecursively(value, function):
    """
    Applies function recursively through list-like structures
    """

    if isListLike(value):
        retVal = [applyFunctionRecursively(_, function) for _ in value]
    else:
        retVal = function(value)

    return retVal

def decodeHexValue(value):
    """
    Returns value decoded from DBMS specific hexadecimal representation
    """

    retVal = value

    def _(value):
        if value and isinstance(value, basestring) and len(value) % 2 == 0:
            if value.lower().startswith("0x"):
                value = value[2:]
            value = value.decode("hex")
            if Backend.isDbms(DBMS.MSSQL):
                try:
                    value = value.decode("utf-16-le")
                except UnicodeDecodeError:
                    pass
            if not isinstance(value, unicode):
                value = value.decode("utf8", "replace")
        return value

    try:
        retVal = applyFunctionRecursively(value, _)
    except Exception:
        singleTimeWarnMessage("there was a problem decoding value '%s' from expected hexadecimal form" % value)

    return retVal

def extractExpectedValue(value, expected):
    """
    Extracts and returns expected value by a given type
    """

    if expected:
        value = unArrayizeValue(value)

        if isNoneValue(value):
            value = None
        elif expected == EXPECTED.BOOL:
            if isinstance(value, int):
                value = bool(value)
            elif isinstance(value, basestring):
                value = value.strip().lower()
                if value in ("true", "false"):
                    value = value == "true"
                elif value in ("1", "-1"):
                    value = True
                elif value == "0":
                    value = False
                else:
                    value = None
        elif expected == EXPECTED.INT:
            if isinstance(value, basestring):
                value = int(value) if value.isdigit() else None

    return value

def hashDBWrite(key, value, serialize=False):
    """
    Helper function for writing session data to HashDB
    """

    _ = "%s%s%s" % (conf.url or "%s%s" % (conf.hostname, conf.port), key, HASHDB_MILESTONE_VALUE)
    conf.hashDB.write(_, value, serialize)

def hashDBRetrieve(key, unserialize=False, checkConf=False):
    """
    Helper function for restoring session data from HashDB
    """

    _ = "%s%s%s" % (conf.url or "%s%s" % (conf.hostname, conf.port), key, HASHDB_MILESTONE_VALUE)
    _ = conf.hashDB.retrieve(_, unserialize) if kb.resumeValues and not (checkConf and any([conf.flushSession, conf.freshQueries])) else None
    if not kb.inferenceMode and not kb.fileReadMode and _ and PARTIAL_VALUE_MARKER in _:
        _ = None
    return _

def resetCookieJar(cookieJar):
    """
    Cleans cookies from a given cookie jar
    """

    if not conf.loadCookies:
        cookieJar.clear()
    else:
        try:
            cookieJar.load(conf.loadCookies)
            cookieJar.clear_expired_cookies()
        except cookielib.LoadError, msg:
            errMsg = "there was a problem loading "
            errMsg += "cookies file ('%s')" % msg
            raise SqlmapGenericException, errMsg

def prioritySortColumns(columns):
    """
    Sorts given column names by length in ascending order while those containing
    string 'id' go first
    """
    _ = lambda x: x and "id" in x.lower()
    return sorted(sorted(columns, key=len), lambda x, y: -1 if _(x) and not _(y) else 1 if not _(x) and _(y) else 0)

def getRequestHeader(request, name):
    """
    Solving an issue with an urllib2 Request header case sensitivity

    Reference: http://bugs.python.org/issue2275
    """

    retVal = None
    if request and name:
        retVal = max(request.get_header(_) if name.upper() == _.upper() else None for _ in request.headers.keys())
    return retVal

def isNumber(value):
    """
    Returns True if the given value is a number-like object
    """

    try:
        float(value)
    except:
        return False
    else:
        return True
