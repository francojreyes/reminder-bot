from datetime import timedelta
from dateutil.relativedelta import relativedelta

DELTA = {
    'minutes': timedelta(minutes=1),
    'hours': timedelta(hours=1),
    'days': timedelta(days=1),
    'weeks': timedelta(days=7),
    'months': relativedelta(months=1)
}

BLURPLE = 0x5865f2
GREEN = 0x57f287
RED = 0xed4245
