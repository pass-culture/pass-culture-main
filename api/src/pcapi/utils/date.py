from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from datetime import timezone as tz
from zoneinfo import ZoneInfo

from babel.dates import format_date
from babel.dates import format_datetime as babel_format_datetime
from dateutil.parser import parserinfo
from psycopg2.extras import NumericRange
import pytz

import pcapi.utils.postal_code as postal_code_utils


DATE_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_FIELD_FORMAT = "%Y-%m-%dT%H:%M"
DEFAULT_STORED_TIMEZONE = "UTC"
MONTHS_IN_FRENCH = [
    None,
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]
# This mapping is also defined in pro. Make sure that all
# are synchronized.
CUSTOM_TIMEZONES = {
    "971": "America/Guadeloupe",
    "972": "America/Martinique",
    "973": "America/Cayenne",
    "974": "Indian/Reunion",
    "975": "America/Miquelon",
    "976": "Indian/Mayotte",
    "977": "America/St_Barthelemy",
    "978": "America/Guadeloupe",  # Saint-Martin
    "986": "Pacific/Wallis",
    # Polynésie (987) actually spans multiple timezones. Use Papeete's timezone.
    "987": "Pacific/Tahiti",
    "988": "Pacific/Noumea",
    "989": "Pacific/Pitcairn",  # Clipperton
    # 984 (Terres australes et antarctiques françaises) is not
    # included because it has several timezones. Hopefully, we'll have
    # very few events, there...
}
METROPOLE_TIMEZONE = "Europe/Paris"
FRENCH_DATE_FORMAT = "%d/%m/%Y"


class FrenchParserInfo(parserinfo):
    WEEKDAYS = [
        ("lun.", "Lundi"),
        ("mar.", "Mardi"),
        ("mer.", "Mercredi"),
        ("jeu.", "Jeudi"),
        ("ven.", "Vendredi"),
        ("sam.", "Samedi"),
        ("dim.", "Dimanche"),
    ]
    MONTHS = [
        ("janv.", "Janvier"),
        ("fevr.", "Février"),
        ("mars", "Mars"),
        ("avr.", "Avril"),
        ("mai", "Mai"),
        ("juin", "Juin"),
        ("juill.", "Juillet"),
        ("août", "Août"),
        ("sept.", "Septembre"),
        ("oct.", "Octobre"),
        ("nov.", "Novembre"),
        ("déc.", "Décembre"),
    ]


def format_datetime(date_time: datetime) -> str:
    return babel_format_datetime(date_time, format="long", locale="fr")[:-9]


def get_postal_code_timezone(postal_code: str) -> str:
    return get_department_timezone(postal_code_utils.PostalCode(postal_code).get_departement_code())


def get_department_timezone(departement_code: str | None) -> str:
    return (
        METROPOLE_TIMEZONE if departement_code is None else CUSTOM_TIMEZONES.get(departement_code, METROPOLE_TIMEZONE)
    )


def utc_datetime_to_department_timezone(date_time: datetime, departement_code: str | None) -> datetime:
    from_zone = ZoneInfo(DEFAULT_STORED_TIMEZONE)
    to_zone = ZoneInfo(get_department_timezone(departement_code))
    utc_datetime = date_time.replace(tzinfo=from_zone)
    return utc_datetime.astimezone(to_zone)


def format_into_utc_date(date_to_format: datetime) -> str:
    return date_to_format.isoformat() + "Z"


def isoformat(date_to_format: datetime | date) -> str:
    return date_to_format.isoformat()


def get_date_formatted_for_email(date_time: datetime) -> str:
    return format_date(date_time, format="d MMMM YYYY", locale="fr")


def get_time_formatted_for_email(date_time: datetime) -> str:
    return date_time.strftime("%Hh%M")


def get_time_in_seconds_from_datetime(date_time: datetime) -> int:
    hour_in_seconds = datetime.time(date_time).hour * 60 * 60
    minute_in_seconds = datetime.time(date_time).minute * 60
    seconds = datetime.time(date_time).second
    return hour_in_seconds + minute_in_seconds + seconds


def get_day_start(dt: date, timezone: pytz.BaseTzInfo) -> datetime:
    """Return a ``datetime`` object that is the first second of the given
    ``date`` in the given timezone.
    """
    return timezone.localize(datetime.combine(dt, time(0, 0)))


def format_time_in_second_to_human_readable(time_in_second: int) -> str | None:
    INTERVALS = [60 * 60 * 24 * 7, 60 * 60 * 24, 60 * 60, 60, 1]
    NAMES = [
        ("semaine", "semaines"),
        ("jour", "jours"),
        ("heure", "heures"),
        ("minute", "minutes"),
        ("seconde", "secondes"),
    ]
    for i, interval in enumerate(INTERVALS):
        if time_in_second >= interval:
            time_in_unit = time_in_second // interval
            unit = NAMES[i][0] if time_in_unit == 1 else NAMES[i][1]
            return f"{time_in_unit} {unit}"
    return None


def local_datetime_to_default_timezone(dt: datetime, local_tz: str) -> datetime:
    from_zone = ZoneInfo(local_tz)
    to_zone = ZoneInfo(DEFAULT_STORED_TIMEZONE)
    if dt.tzinfo:
        return dt.astimezone(to_zone)
    return dt.replace(tzinfo=from_zone).astimezone(to_zone)


def default_timezone_to_local_datetime(dt: datetime, local_tz: str) -> datetime:
    from_zone = ZoneInfo(DEFAULT_STORED_TIMEZONE)
    to_zone = ZoneInfo(local_tz)
    if dt.tzinfo:
        return dt.astimezone(to_zone)
    return dt.replace(tzinfo=from_zone).astimezone(to_zone)


def date_to_localized_datetime(date_: date | None, time_: time) -> datetime | None:
    # When min/max date filters are used in requests, backoffice user expect Metroplitan French time (CET),
    # since date and time in the backoffice are formatted to show CET times.
    if not date_:
        return None
    naive_utc_datetime = datetime.combine(date_, time_)
    return pytz.timezone(METROPOLE_TIMEZONE).localize(naive_utc_datetime).astimezone(pytz.utc)


def parse_french_date(date_str: str | None) -> datetime | None:
    return datetime.strptime(date_str, FRENCH_DATE_FORMAT) if date_str else None


def format_date_to_french_locale(date_: date | None) -> str | None:
    return date_.strftime(FRENCH_DATE_FORMAT) if date_ else None


def int_to_time(time_as_int: int) -> str:
    """
    Convert time defined by hours * 60 + minutes to the format "HH:MM"
    """
    hours, minutes = divmod(time_as_int, 60)
    return f"{hours:02}:{minutes:02}"


def time_to_int(time_as_str: str) -> int:
    """
    Convert time in the format "HH:MM" to int defined by hours * 60 + minutes
    """
    hours, minutes = map(int, time_as_str.split(":"))
    return hours * 60 + minutes


def timespan_str_to_numrange(timespan_list: list[tuple[str, str]]) -> list[NumericRange]:
    """
    Convert a list of tuples (start, end) in the format [("HH:MM", "HH:MM"), ("HH:MM"), "HH:MM")] to a list of NumericRange
    """
    return [NumericRange(time_to_int(start), time_to_int(end), bounds="[]") for start, end in timespan_list]


def numranges_to_timespan_str(numranges: list[NumericRange]) -> list[tuple[str, str]]:
    """
    Convert a list of NumericRange to a list of tuples (start, end) in the format [("HH:MM", "HH:MM"), ...]
    """
    return [(int_to_time(int(numrange.lower)), int_to_time(int(numrange.upper))) for numrange in numranges]


def numranges_to_readble_str(numranges: list[NumericRange] | None) -> str:
    """
    Convert a list of NumericRange to a list of tuples (start, end) in a str ("HH:MM", "HH:MM")]
    """
    if numranges is None:
        return ""
    return ", ".join(f"{int_to_time(int(numrange.lower))}-{int_to_time(int(numrange.upper))}" for numrange in numranges)


def days_ago_timestamp(days: int) -> int:
    """Get a timestamp from a date `days` ago"""
    days_ago = datetime.now(tz.utc) - timedelta(days=days)  # pylint: disable=datetime-now
    return int(days_ago.timestamp())
