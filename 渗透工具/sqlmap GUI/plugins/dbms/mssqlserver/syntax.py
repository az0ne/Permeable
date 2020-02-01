#!/usr/bin/env python

"""
Copyright (c) 2006-2012 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.exception import SqlmapSyntaxException
from plugins.generic.syntax import Syntax as GenericSyntax

class Syntax(GenericSyntax):
    def __init__(self):
        GenericSyntax.__init__(self)

    @staticmethod
    def unescape(expression, quote=True):
        if quote:
            while True:
                index = expression.find("'")
                if index == -1:
                    break

                firstIndex = index + 1
                index = expression[firstIndex:].find("'")

                if index == -1:
                    raise SqlmapSyntaxException("Unenclosed ' in '%s'" % expression)

                lastIndex = firstIndex + index
                old = "'%s'" % expression[firstIndex:lastIndex]

                unescaped = "+".join("%s(%d)" % ("CHAR" if ord(expression[i]) < 256 else "NCHAR", ord(expression[i])) for i in xrange(firstIndex, lastIndex))

                expression = expression.replace(old, unescaped)
        else:
            expression = "+".join("CHAR(%d)" % ord(c) for c in expression)

        return expression

    @staticmethod
    def escape(expression):
        while True:
            index = expression.find("CHAR(")
            if index == -1:
                break

            firstIndex = index
            index = expression[firstIndex:].find(")")

            if index == -1:
                raise SqlmapSyntaxException("Unenclosed ) in '%s'" % expression)

            lastIndex = firstIndex + index + 1
            old = expression[firstIndex:lastIndex]
            oldUpper = old.upper()
            oldUpper = oldUpper.replace("CHAR(", "").replace(")", "")

            escaped = "'%s'" % chr(int(oldUpper))
            expression = expression.replace(old, escaped)

        expression = expression.replace("'+'", "")
        return expression
