#!/usr/bin/env python

"""
Copyright (c) 2006-2012 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOWEST

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Appends encoded NULL byte character at the end of payload

    Example:
        * Input: AND 1=1
        * Output: AND 1=1%00

    Requirement:
        * Microsoft Access

    Notes:
        * Useful to bypass weak web application firewalls when the back-end
          database management system is Microsoft Access - further uses are
          also possible

    Reference: http://projects.webappsec.org/w/page/13246949/Null-Byte-Injection
    """

    return "%s%%00" % payload if payload else payload
