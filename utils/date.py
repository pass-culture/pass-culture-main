from datetime import datetime
from math import floor

from babel.dates import format_datetime as babel_format_datetime
from dateutil import tz

from utils.string_processing import parse_timedelta


class DateTimes:
    def __init__(self, *datetimes):
        self.datetimes = list(datetimes)

    def __eq__(self, other):
        return self.datetimes == other.datetimes


def match_format(value: str, format: str):
    try:
        datetime.strptime(value, format)
    except ValueError:
        return False
    else:
        return True


def format_datetime(dt):
    return babel_format_datetime(dt,
                                 format='long',
                                 locale='fr')[:-9]


def format_duration(dr):
    return floor(parse_timedelta(dr).total_seconds() / 60)


def get_dept_timezone(departementCode):
    assert isinstance(departementCode, str)
    if departementCode == '97':
        tz_name = 'America/Cayenne'
    else:
        tz_name = 'Europe/Paris'
    return tz_name


def utc_datetime_to_dept_timezone(datetimeObj, departementCode):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(get_dept_timezone(departementCode))
    utc_datetime = datetimeObj.replace(tzinfo=from_zone)
    return utc_datetime.astimezone(to_zone)


def dept_timezone_datetime_to_utc(datetimeObj, departementCode):
    from_zone = tz.gettz(get_dept_timezone(departementCode))
    to_zone = tz.gettz('UTC')
    dept_datetime = datetimeObj.replace(tzinfo=from_zone)
    return dept_datetime.astimezone(to_zone)
