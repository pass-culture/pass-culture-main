import logging
from datetime import date
from datetime import datetime

from dateutil.relativedelta import relativedelta

from pcapi.utils import date as date_utils
from pcapi.utils.date import utc_datetime_to_department_timezone


logger = logging.getLogger(__name__)


def get_age_at_date(birth_date: date, specified_datetime: datetime, department_code: str | None = None) -> int:
    timezoned_datetime = utc_datetime_to_department_timezone(specified_datetime, department_code)
    timezoned_birth_date = datetime.combine(birth_date, datetime.min.time(), tzinfo=timezoned_datetime.tzinfo)
    return max(0, relativedelta(timezoned_datetime, timezoned_birth_date).years)


def get_age_from_birth_date(birth_date: date, department_code: str | None = None) -> int:
    return get_age_at_date(birth_date, date_utils.get_naive_utc_now(), department_code)


def format_login_location(country_name: str | None, city_name: str | None) -> str | None:
    if city_name:
        return f"{city_name}, {country_name}" if country_name else city_name

    return country_name
