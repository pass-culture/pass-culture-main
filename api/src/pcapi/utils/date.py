from datetime import date
from datetime import datetime
from datetime import time
from zoneinfo import ZoneInfo

from babel.dates import format_date
from babel.dates import format_datetime as babel_format_datetime
from dateutil.parser import parserinfo
from pytz import BaseTzInfo as pytz_BaseTzInfo

from pcapi.domain.postal_code.postal_code import PostalCode


DATE_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
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


class FrenchParserInfo(parserinfo):
    WEEKDAYS = [
        ("lun.", "Lundi"),
        ("mar.", "Mardi"),  # TODO: "Tues"
        ("mer.", "Mercredi"),
        ("jeu.", "Jeudi"),  # TODO: "Thurs"
        ("ven.", "Vendredi"),
        ("sam.", "Samedi"),
        ("dim.", "Dimanche"),
    ]
    MONTHS = [
        ("janv.", "Janvier"),
        ("fevr.", "Février"),  # TODO: "Febr"
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


class DateTimes:
    def __init__(self, *datetimes):  # type: ignore [no-untyped-def]
        self.datetimes = list(datetimes)

    def __eq__(self, other):  # type: ignore [no-untyped-def]
        return self.datetimes == other.datetimes


def format_datetime(date_time: datetime) -> str:
    return babel_format_datetime(date_time, format="long", locale="fr")[:-9]


def get_postal_code_timezone(postal_code: str) -> str:
    return get_department_timezone(PostalCode(postal_code).get_departement_code())


def get_department_timezone(departement_code: str | None) -> str:
    return (
        METROPOLE_TIMEZONE if departement_code is None else CUSTOM_TIMEZONES.get(departement_code, METROPOLE_TIMEZONE)
    )


def utc_datetime_to_department_timezone(date_time: datetime | None, departement_code: str) -> datetime:
    from_zone = ZoneInfo(DEFAULT_STORED_TIMEZONE)
    to_zone = ZoneInfo(get_department_timezone(departement_code))
    utc_datetime = date_time.replace(tzinfo=from_zone)  # type: ignore [union-attr]
    return utc_datetime.astimezone(to_zone)


def format_into_utc_date(date_to_format: datetime) -> str:
    return date_to_format.isoformat() + "Z"


def format_into_timezoned_date(date_to_format: datetime) -> str:
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


def get_day_start(dt: date, timezone: pytz_BaseTzInfo) -> datetime:
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
