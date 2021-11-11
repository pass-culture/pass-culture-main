import datetime

import pytz


ACCOUNTING_TIMEZONE = pytz.timezone("Europe/Paris")


def get_cutoff_as_datetime(last_day: str) -> datetime.datetime:
    """Return a UTC datetime object for the first second of the day after
    the requested date (the latter being expressed as an ISO-formatted
    date in the CET/CEST timezone).
    """
    next_day = datetime.date.fromisoformat(last_day) + datetime.timedelta(days=1)
    first_second = datetime.datetime.combine(next_day, datetime.time.min)
    return ACCOUNTING_TIMEZONE.localize(first_second).astimezone(pytz.utc)
