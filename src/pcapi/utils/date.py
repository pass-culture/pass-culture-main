from datetime import datetime
from typing import Optional

from babel.dates import format_date
from babel.dates import format_datetime as babel_format_datetime
from dateutil import tz

from pcapi.domain.postal_code.postal_code import PostalCode


DATE_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_STORED_TIMEZONE = "UTC"
MONTHS_IN_FRENCH = [
    None,
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]
# This mapping is also defined in webapp and pro. Make sure that all
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


class DateTimes:
    def __init__(self, *datetimes):
        self.datetimes = list(datetimes)

    def __eq__(self, other):
        return self.datetimes == other.datetimes


def strftime(date) -> str:
    return date.strftime(DATE_ISO_FORMAT)


def match_format(value: str, fmt: str) -> str:
    try:
        datetime.strptime(value, fmt)
    except ValueError:
        return False
    else:
        return True


def format_datetime(date_time: datetime) -> str:
    return babel_format_datetime(date_time, format="long", locale="fr")[:-9]


def get_postal_code_timezone(postal_code: str) -> str:
    return get_department_timezone(PostalCode(postal_code).get_departement_code())


def get_department_timezone(departement_code: str) -> str:
    return CUSTOM_TIMEZONES.get(departement_code, METROPOLE_TIMEZONE)


def utc_datetime_to_department_timezone(date_time: Optional[datetime], departement_code: str) -> datetime:
    from_zone = tz.gettz(DEFAULT_STORED_TIMEZONE)
    to_zone = tz.gettz(get_department_timezone(departement_code))
    utc_datetime = date_time.replace(tzinfo=from_zone)
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
