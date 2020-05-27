from datetime import datetime, time

import pytz
from babel.dates import format_date
from babel.dates import format_datetime as babel_format_datetime
from dateutil import tz

TODAY = datetime.combine(datetime.utcnow(), time(hour=20))
DATE_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_STORED_TIMEZONE = 'UTC'
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


def english_to_french_month(year: int, month_number: int, day: int = 1) -> str:
    english_month = datetime(year, month_number, day).strftime("%B")
    return ENGLISH_TO_FRENCH_MONTH[english_month]


class DateTimes:
    def __init__(self, *datetimes):
        self.datetimes = list(datetimes)

    def __eq__(self, other):
        return self.datetimes == other.datetimes


def strftime(date) -> str:
    return date.strftime(DATE_ISO_FORMAT)


def match_format(value: str, format: str) -> str:
    try:
        datetime.strptime(value, format)
    except ValueError:
        return False
    else:
        return True


def format_datetime(date_time: datetime) -> str:
    return babel_format_datetime(date_time,
                                 format='long',
                                 locale='fr')[:-9]


def get_department_timezone(departement_code: str) -> str:
    assert isinstance(departement_code, str)

    if departement_code == '973':
        return 'America/Cayenne'
    if departement_code == '974':
        return 'Indian/Reunion'

    return 'Europe/Paris'


def utc_datetime_to_department_timezone(date_time: datetime, departement_code: str) -> datetime:
    from_zone = tz.gettz(DEFAULT_STORED_TIMEZONE)
    to_zone = tz.gettz(get_department_timezone(departement_code))
    utc_datetime = date_time.replace(tzinfo=from_zone)
    return utc_datetime.astimezone(to_zone)


def format_into_ISO_8601(value: str) -> str:
    return value.isoformat() + "Z"


def get_date_formatted_for_email(date_time: datetime) -> str:
    return format_date(date_time, format='d MMMM', locale='fr')


def get_time_formatted_for_email(date_time: datetime) -> str:
    return date_time.strftime('%Hh%M')


def get_time_in_seconds_from_datetime(date_time: datetime) -> int:
    hour_in_seconds = datetime.time(date_time).hour * 60 * 60
    minute_in_seconds = datetime.time(date_time).minute * 60
    seconds = datetime.time(date_time).second
    return hour_in_seconds + minute_in_seconds + seconds
