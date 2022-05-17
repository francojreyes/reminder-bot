'''
Utility functions for parsing dates, times and intervals
'''
from datetime import datetime, timedelta, timezone
from dateparser import parse
from dateutil import tz

from src import constants


# We want to store all as timestamps

# For on date
# We want to take a date/time
# Parse it to a specific time (tz aware)
# Compare it to time now (utc)
# Represent this time in specific format, local time
# Later, parse into a timestamp

def date_to_str(string, tz):
    # Read a date, from tz to UTC (aware)
    # Convert to string
    pass

def date_to_timestamp(string, tz):
    # Read a date, from tz to UTC (naive)
    pass

# For in time
# We want to take an interval
# Normalise it into a set format
# Later, parse into a timestamp representing time from now
# Might as well make it aware

# For repeat time
# We wanat to take an interval
# Normalise it into a set format
# Later, parse it into a timestamp from now

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
    for period, n in match.groupdict().items():
        # Ignore all not found
        if n is None:
            continue

        # Make plural if more than one
        result.append(f"{n} {period}{'s' if float(n) > 1 else ''}")
    
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

    # print(repr(res))

    if res:
        return int(res.timestamp())
    else:
        raise ValueError('Unable to convert')

# s = '1.5 hours'
# s = normalise_relative(s)
# print(s)
# relative_to_timestamp(s, datetime.now().timestamp())
