import datetime

import pytz


ACCOUNTING_TIMEZONE = pytz.timezone("Europe/Paris")


def get_cutoff_as_datetime(last_day: datetime.date) -> datetime.datetime:
    """Return a UTC datetime object for the first second of the day after
    the requested date (the latter being expressed as a date in the
    CET/CEST timezone).
    """
    next_day = last_day + datetime.timedelta(days=1)
    first_second = datetime.datetime.combine(next_day, datetime.time.min)
    return ACCOUNTING_TIMEZONE.localize(first_second).astimezone(pytz.utc)
