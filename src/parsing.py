"""
Utility functions for parsing dates, times and intervals
"""
import re
from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo

from dateparser import parse
from dateutil.relativedelta import relativedelta

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


def str_to_timedelta(string: str):
    """
    Read a relative time string into a timedelta object
    """
    base = datetime.now(tz=ZoneInfo("UTC"))
    relative = add_interval(string, base)
    return relative - base


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
    periods = []
    for period, num in match.groupdict().items():
        # Ignore all not found
        if num is None:
            continue

        # Make plural if more than one
        periods.append(f"{num} {period if float(num) != 1 else period[:-1]}")
    
    # If it starts with 0, invalid
    result = ', '.join(periods)
    if result.startswith('0 '):
        return None

    return result


RELATIVE_UNITS = ["days", "weeks", "months", "years"]
def add_interval(interval: str, dt: datetime):
    """
    Given a string describing an interval and a datetime, returns a new datetime
    that is `interval` after the original datetime
    """
    tz: tzinfo = dt.tzinfo or ZoneInfo('UTC')

    units_dict = constants.INTERVAL_REGEX.match(interval).groupdict()
    units_dict = {k: (int(v) if v else 0) for k, v in units_dict.items()}

    # Handle relative units by adding to the corresponding component
    dt += relativedelta(**{k: units_dict[k] for k in RELATIVE_UNITS})

    # Handle absolute units (seconds) by adding directly to the timestamp
    delta = units_dict.get("hours", 0) * 3600 + units_dict.get("minutes", 0) * 60 + units_dict.get("seconds", 0)
    dt = datetime.fromtimestamp(dt.timestamp() + delta, tz=tz)

    return dt
