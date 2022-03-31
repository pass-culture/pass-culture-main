from datetime import datetime

from dateutil import tz
from sqlalchemy.util._collections import AbstractKeyedTuple

from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.utils.date import get_department_timezone


def _apply_departement_timezone(naive_datetime: datetime, departement_code: str) -> datetime:
    return (
        naive_datetime.astimezone(tz.gettz(get_department_timezone(departement_code)))
        if naive_datetime is not None
        else None
    )


def convert_booking_dates_utc_to_venue_timezone(
    date_without_timezone: datetime, booking: AbstractKeyedTuple
) -> datetime:
    if booking.venueDepartmentCode:
        return _apply_departement_timezone(
            naive_datetime=date_without_timezone, departement_code=booking.venueDepartmentCode
        )
    offerer_department_code = PostalCode(booking.offererPostalCode).get_departement_code()
    return _apply_departement_timezone(naive_datetime=date_without_timezone, departement_code=offerer_department_code)
