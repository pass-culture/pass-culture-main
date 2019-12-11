from datetime import datetime, time
from math import floor

from babel.dates import format_datetime as babel_format_datetime, format_date
from dateutil import tz

from utils.string_processing import parse_timedelta

today = datetime.combine(datetime.utcnow(), time(hour=20))
DATE_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

ENGLISH_TO_FRENCH_MONTH = {
    "January": "Janvier",
    "February": "Février",
    "March": "Mars",
    "April": "Avril",
    "May": "Mai",
    "June": "Juin",
    "July": "Juillet",
    "August": "Août",
    "September": "Septembre",
    "October": "Octobre",
    "November": "Novembre",
    "December": "Décembre"
}


def english_to_french_month(year, month_number, day=1):
    english_month = datetime(year, month_number, day).strftime("%B")
    return ENGLISH_TO_FRENCH_MONTH[english_month]


class DateTimes:
    def __init__(self, *datetimes):
        self.datetimes = list(datetimes)

    def __eq__(self, other):
        return self.datetimes == other.datetimes


def read_json_date(date):
    if '.' not in date:
        date = date + '.0'
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")


def strftime(date):
    return date.strftime(DATE_ISO_FORMAT)


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
    if departementCode in ['973', '97']:
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


def format_into_ISO_8601(value):
    return value.isoformat() + "Z"


def get_date_formatted_for_email(date_time):
    return format_date(date_time, format='long', locale='fr')[:-5]


def get_time_formatted_for_email(date_time):
    return date_time.strftime('%Hh%M')
