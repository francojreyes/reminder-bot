"""
Constants used by the application
"""
import itertools
import re
import json

# REGEX taken from
# https://github.com/wroberts/pytimeparse/blob/master/pytimeparse/timeparse.py

YEARS       = r'(?P<years>\d+)\s*(?:ys?|yrs?.?|years?)'
MONTHS      = r'(?P<months>\d+)\s*(?:mos?.?|mths?.?|months?)'
WEEKS       = r'(?P<weeks>[\d.]+)\s*(?:w|wks?|weeks?)'
DAYS        = r'(?P<days>[\d.]+)\s*(?:d|dys?|days?)'
HOURS       = r'(?P<hours>[\d.]+)\s*(?:h|hrs?|hours?)'
MINS        = r'(?P<minutes>[\d.]+)\s*(?:m|(mins?)|(minutes?))'
SECS        = r'(?P<seconds>[\d.]+)\s*(?:s|secs?|seconds?)'
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

BLURPLE = 0x5865f2
GREEN = 0x57f287
RED = 0xed4245

with open('tzdata/tz_countries.json', 'r') as f:
    TZ_COUNTRIES = json.load(f)
    TZ_ALL = list(itertools.chain(*[tz_list for tz_list in TZ_COUNTRIES.values()]))
