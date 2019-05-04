"""Filename matching with shell patterns.

fnmatch(FILENAME, PATTERN) matches according to the local convention.
fnmatchcase(FILENAME, PATTERN) always takes case in account.

The functions operate by translating the pattern into a regular
expression.  They cache the compiled regular expressions for speed.

The function translate(PATTERN) returns a regular expression
corresponding to PATTERN.  (It does not compile it.)

Based on code from fnmatch.py file distributed with Python 2.6.

Licensed under PSF License (see LICENSE.PSF file).

Changes to original fnmatch module:
- translate function supports ``*`` and ``**`` similarly to fnmatch C library
"""

import os
import re


__all__ = ["fnmatch", "fnmatchcase", "translate"]

_cache = {}


# Different varaints to handle number ranges.
#
# - AS_IS and ZEROS also matching numbers with leading '+'
# - AS_IS and ZEROS also match the zero as '-0', '+0' and plain '0'
# - ZEROS allow any number of leading zeros, so '1' also matches '00001'
# - JUSTIFIED handles leading zeros like bash. So {01..10} matches '01' but not
#   '1'. Leading '+' is not allowed.

# handle as is
AS_IS     = 0
# allow any number of leading zeros
ZEROS     = 1
# handle leading zeros like like bash
JUSTIFIED = 2

NUMBER_MODE = JUSTIFIED

# Characters that must be escaped in square brackets.
# Note: The '-' might be used for a range ('a-z') and '^' for negation,
# so be careful!
CHARACTER_CLASS_SPECIAL = "^-]\\"

# regex to check if a number is at least 2-digits with leading zero.
LEADING_ZERO = re.compile(
    r"""
    ^               # match at start of string
    [-+] ?          # optional sign ('+' or '-')
    0               # a leading zero
    \d              # followed by another digit
    """, re.VERBOSE
)

NUMERIC_RANGE = re.compile(
    r"""
    (               # Capture a number
        [+-] ?      # Zero or one "+" or "-" characters
        \d +        # One or more digits
    )

    \.\.            # ".."

    (               # Capture a number
        [+-] ?      # Zero or one "+" or "-" characters
        \d +        # One or more digits
    )
    """, re.VERBOSE
)


def fnmatch(name, pat):
    """Test whether FILENAME matches PATTERN.

    Patterns are Unix shell style:

    - ``*``             matches everything except path separator
    - ``**``            matches everything
    - ``?``             matches any single character
    - ``[seq]``         matches any character in seq
    - ``[!seq]``        matches any char not in seq
    - ``{s1,s2,s3}``    matches any of the strings given (separated by commas)
    - ``{no1..n2}``     matches any number from no1 and n2

    An initial period in FILENAME is not special.
    Both FILENAME and PATTERN are first case-normalized
    if the operating system requires it.
    If you don't want this, use fnmatchcase(FILENAME, PATTERN).
    """

    name = os.path.normpath(name).replace(os.sep, "/")
    return fnmatchcase(name, pat)


def fnmatchcase(name, pat):
    """Test whether FILENAME matches PATTERN, including case.

    This is a version of fnmatch() which doesn't case-normalize
    its arguments.
    """
    if not pat in _cache:
        res = translate(pat)
        regex = re.compile(res, re.DOTALL)
        _cache[pat] = regex
    else:
        regex = _cache[pat]

    return regex.match(name)


def translate(pat):
    regex = doTranslate(pat, DEFAULT)
    #print("%s -> %s" % (pat, regex))
    return r'^%s$' % regex


# translating glob as a top-level re
DEFAULT = 0
# translating glob as the part inside a choice ('{}')
IN_BRACES = 1

def doTranslate(pat, state):
    """Translate editorconfig shell GLOB PATTERN to a regular expression.
    """

    index=0
    length = len(pat)
    regex = ''

    while index < length:
        current_char = pat[index]
        index += 1
        if current_char == '*':
            if index < length and pat[index] == '*':
                regex += '.*'
                index +=1
            else:
                regex += '[^/]*'
        elif current_char == '?':
            regex += '.'
        elif current_char == '[':
            pos = getClosingBracketIndex(pat, index, state)
            if pos < 0:   # either unclosed or contains slash
                regex += '\\['
            else:
                regex += '['
                regex += handleCharacterClass(pat, index, pos)
                regex += ']'
                index = pos + 1
        elif current_char == '{':
            pos, has_comma =  getClosingBracesIndex(pat, index)
            if pos < 0:   # unclosed
                regex += '\\{'
            else:
                if not has_comma:
                    num_range = NUMERIC_RANGE.match(pat[index:pos])
                    if num_range:
                        regex += globRange2Re(num_range.group(1), num_range.group(2))
                    else:
                        inner = doTranslate(pat[index:pos], DEFAULT)
                        regex += '\\{%s\\}' % inner
                    index = pos + 1
                else:
                    inner = doTranslate(pat[index:pos], IN_BRACES)
                    regex += '(?:' + inner + ')'
                    index = pos +1
        elif current_char == ',':
            if state == IN_BRACES:
                regex += '|'
            else:
                regex += '\\,'
        elif current_char == '/':
            if pat[index:(index + 3)] == '**/':
                regex += "(?:/|/.*/)"
                index += 3
            else:
                regex += '/'
        elif current_char == '\\':
            if index < length:
                current_char = pat[index]
            regex += re.escape(current_char)
            index += 1
        else:
            regex += re.escape(current_char)
        #endif
    #endwhile
    return regex


def getClosingBracketIndex(pat, start, state):
    """Find a closing bracket in pat starting from start.
    Return the index of the closing bracket.
    Returns -1 if
     - no closing bracket was found
     - a slash was found
     - a comma was found AND the given state is IN_BRACES
    """
    length = len(pat)
    index = start
    while index < length and pat[index] != ']':
        if pat[index] == '/':
            return -1
        elif pat[index] == ',' and state == IN_BRACES:
            return -1
        if pat[index] == '\\':
            index +=1
        index +=1

    return index if index < length else -1


def getClosingBracesIndex(pat, start):
    """Find a closing brace in pat starting from start.
    Returns the index of the closing brace and whether a comma was found.
    If no closing brace was found, returns the index -1. In that
    case it is irrelevant whether a comma was found or not.
    """
    length = len(pat)
    index = start
    has_comma = False
    while index < length and  pat[index] != '}':
        if pat[index] == ',':
            has_comma = True
        elif pat[index] == '{':
            pos, icomma = getClosingBracesIndex(pat, index+1)
            if pos >=0:
                index = pos
            elif icomma:
                has_comma = True
        elif pat[index] == '\\':
            index += 1
        index += 1

    if index >= length:
        index = -1

    return index, has_comma

def handleCharacterClass(pat, start, end):
    index = start
    result = ''

    if pat[index] in '!^':
        index += 1
        result += '^'

    while index < end:
        if pat[index] == '\\':
            if (index+1) < end:
                index += 1
                if pat[index] in CHARACTER_CLASS_SPECIAL:
                    result += '\\'
                result += pat[index]
            else:
                result += '\\\\'
        elif pat[index] == '-':
            result += pat[index]
        else:
            if pat[index] in CHARACTER_CLASS_SPECIAL:
                result += '\\'
            result += pat[index]
        index += 1
    return result


def globRange2Re(lower, upper):
    """Creates a regular expression for a range of numbers.

    The translation depends on JUSTIFY_NUMBERS.

    JUSTIFY_NUMBERS == False:
    - {3..120}   -> (?:\+?(?:[3-9]|[1-9][0-9]|1[0-1][0-9]|120))
    - {03..120}  -> (?:\+?(?:[3-9]|[1-9][0-9]|1[0-1][0-9]|120))
    - {-03..120} -> (?:-(?:[1-3])|\+?(?:[0-9]|[1-9][0-9]|1[0-1][0-9]|120))

    JUSTIFY_NUMBERS == True:
    - {3..120}   -> (?:[3-9]|[1-9][0-9]|1[0-1][0-9]|120)
    - {03..120}  -> (?:00[3-9]|0[1-9][0-9]|1[0-1][0-9]|120)
    - {-03..120} -> (?:-(?:0[1-3])|00[0-9]|0[1-9][0-9]|1[0-1][0-9]|120)
    """

    width = -1
    if NUMBER_MODE == JUSTIFIED:
        if LEADING_ZERO.match(lower) or LEADING_ZERO.match(upper):
            width = max(len(lower.replace('+', '')), len(upper.replace('+', '')))

    low_num = int(lower)
    up_num = int(upper)
    start = min(low_num, up_num)
    end = max(low_num, up_num)
    neg_part = ''
    if start < 0:
        if NUMBER_MODE != JUSTIFIED:
            neg_start = -end if end < 0 else 0
        else:
            neg_start = -end if end < 0 else 1
        neg_end = -start
        neg_width = width
        if end >= 0:
            neg_width -= 1
        neg_part = num_re(neg_width, neg_start, neg_end, '')
        if NUMBER_MODE == ZEROS:
            neg_part = "\\-0*(?:%s)" % new_part
        else:
            neg_part = "\\-(?:%s)" % neg_part
        if end < 0:
            return "(?:%s)" % neg_part
        else:
            neg_part += '|'
        start = 0

    pos_part = num_re(width, start, end, '')

    if NUMBER_MODE == JUSTIFIED:
        return '(?:%s%s)' % (neg_part, pos_part)
    elif NUMBER_MODE == ZEROS:
        return '(?:%s\\+?0*(?:%s))' % (neg_part, pos_part)
    else:
        return '(?:%s\\+?(?:%s))' % (neg_part, pos_part)


# how many decimal digit has the given number?
def digits(num):
    num = num if num >= 0 else -num
    if num < 10:
        return 1
    elif num < 10:
        return 1
    elif num < 100:
        return 2
    elif num < 1000:
        return 3
    else:
        num = num//1000
        d=3
        while num > 0:
            num //=10
            d +=1
        return d

def num_re(a_width, min, max, suffix):
    width = a_width if a_width > 0 else 0
    width10s = (a_width - 1) if a_width > 0 else 0

    if min == max:
        return "%0*d%s" % (width, min, suffix)
    if min//10 == max//10:
        if min >= 10 or width10s > 0:
            return "%0*d[%d-%d]%s" % (width10s, min//10, min%10, max%10, suffix)
        else:
            return "[%d-%d]%s" % (min%10, max%10, suffix)

    re = ""

    # if min is not divisible by 10, create re to match the gap to the next
    # number divisable by 10
    if min == 0 or min%10 != 0:
        new_min = (min//10+1)*10
        re += num_re(width, min, new_min-1, suffix)
    else:
        new_min = min

    # move new_min forward to have the same number of digits like max
    # create the needed re
    new_suffix=suffix + "[0-9]"
    div = 1
    while(digits(new_min) < digits(max)):
        div *= 10
        next_min = pow(10, digits(new_min))
        if re != "":
            re += "|"
        re += num_re(width-digits(new_min)+1, new_min//div, (next_min-1)//div, new_suffix)
        new_min = next_min
        new_suffix += "[0-9]"

    # new_min now has the same number of digits like max
    div = pow(10, digits(new_min)-1)
    while div > 1:
        new_max = (max // div)*div
        if (new_max + div-1) == max:
            # special handling for numbers ending with '9'
            # We can handle it in this loop.
            new_max = max
        if new_min != new_max:
            x=div
            new_suffix=""
            while x > 1:
                new_suffix += "[0-9]"
                x //= 10
            if re != "":
                re += "|"
            re += num_re(width-digits(new_min)+1, new_min//div, (new_max-1)//div, new_suffix)

        new_min = new_max
        div //=10

    if new_min < max:
        if re != "":
            re += "|"
        re += num_re(width10s, new_min//10, (max)//10, "[0-%d]" % (max%10))
    elif new_min%10 != 9:
        if re != "":
            re += "|"
        re += "%d" % max
    # else: The number ended with '9'/'99'/'999'... and was handled in the loop above

    return re

