'''
Utility functions for parsing dates, times and intervals
'''
from datetime import datetime
import re
from dateparser import parse

from src import constants


def str_to_datetime(string: str, timezone: str):
    """Process a string and timezone to an aware datetime"""
    string = re.sub(constants.TODAY, 'today', string)
    string = re.sub(constants.TOMORROW, 'tomorrow', string)
    settings = {
        'DATE_ORDER': 'DMY',
        'TIMEZONE': timezone,
        'RETURN_AS_TIMEZONE_AWARE': True,
        'PREFER_DAY_OF_MONTH': 'first',
        'PREFER_DATES_FROM': 'future',
        'PARSERS': ['relative-time', 'absolute-time']
    }
    return parse(string, languages=['en'], settings=settings)


def normalise_relative(string: str):
    """
    Read an arbitrary relative time string and convert it to
        n years, n months, n days, n hours, n minutes, n seconds
    omitting all for which n is 0

    Raises ValueError is fails
    """
    # If no number (e.g. year, day) add the number 1
    if string.isalpha():
        string = '1 ' + string

    # Regex match
    match = constants.INTERVAL_REGEX.match(string)
    if not match or not match.group(0).strip():
        return None

    # Convert to string
    result = []
    for period, num in match.groupdict().items():
        # Ignore all not found
        if num is None:
            continue

        # Make plural if more than one
        result.append(f"{num} {period}{'s' if float(num) > 1 else ''}")

    return ', '.join(result)


def relative_to_timestamp(string: str, base: int):
    """
    Given an relative time string and a UNIX timestamp, returns the timestamp
    representing the interval added to the timestamp
    """
    settings = {
        'TIMEZONE': 'UTC',
        'TO_TIMEZONE': 'UTC',
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.fromtimestamp(base),
        'PARSERS': ['relative-time']
    }
    res = parse(string, locales=['en-AU'], settings=settings)

    if not res:
        raise ValueError('Unable to convert')

    return int(res.timestamp())
