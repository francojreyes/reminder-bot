'''
Constants used by the application
'''
import re

# REGEX taken from
# https://github.com/wroberts/pytimeparse/blob/master/pytimeparse/timeparse.py

YEARS       = r'(?P<year>\d+)\s*(?:ys?|yrs?.?|years?)'
MONTHS      = r'(?P<month>\d+)\s*(?:mos?.?|mths?.?|months?)'
WEEKS       = r'(?P<week>[\d.]+)\s*(?:w|wks?|weeks?)'
DAYS        = r'(?P<day>[\d.]+)\s*(?:d|dys?|days?)'
HOURS       = r'(?P<hour>[\d.]+)\s*(?:h|hrs?|hours?)'
MINS        = r'(?P<minute>[\d.]+)\s*(?:m|(mins?)|(minutes?))'
SECS        = r'(?P<second>[\d.]+)\s*(?:s|secs?|seconds?)'
SEPARATORS  = r'[,/]'

OPT         = lambda x: r'(?:{x})?'.format(x=x)
OPTSEP      = lambda x: r'(?:{x}\s*(?:{SEPARATORS}\s*)?)?'.format(
                            x=x, SEPARATORS=SEPARATORS)

INTERVAL_FORMAT = r'{YEARS}\s*{MONTHS}\s*{WEEKS}\s*{DAYS}\s*{HOURS}\s*{MINS}\s*{SECS}'.format(
    YEARS=OPTSEP(YEARS),
    MONTHS=OPTSEP(MONTHS),
    WEEKS=OPTSEP(WEEKS),
    DAYS=OPTSEP(DAYS),
    HOURS=OPTSEP(HOURS),
    MINS=OPTSEP(MINS),
    SECS=OPT(SECS))

INTERVAL_REGEX = re.compile(r'\s*' + INTERVAL_FORMAT + r'\s*$', re.I)

TOMORROW    = r'(?:tmrw?|tmw|tomorrow)'
TODAY       = r'(?:today|tdy)'
DATE_FORMAT = '%-d %b %Y at %-I:%M %p'

ISO_TZD = lambda n: f"{'+' if n >= 0 else '-'}{abs(n):02}:00"

BLURPLE = 0x5865f2
GREEN = 0x57f287
RED = 0xed4245
