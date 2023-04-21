from datetime import datetime
import typing

from dateutil import tz

import pcapi.utils.date as date_utils
import pcapi.utils.postal_code as postal_code_utils


if typing.TYPE_CHECKING:
    from pcapi.core.bookings.models import Booking
    from pcapi.core.educational.models import CollectiveBooking


def convert_real_booking_dates_utc_to_venue_timezone(
    date_without_timezone: datetime | None, booking: "CollectiveBooking"
) -> datetime | None:
    if booking.venue.departementCode:
        return _apply_departement_timezone(
            naive_datetime=date_without_timezone, departement_code=booking.venue.departementCode
        )
    offerer_department_code = postal_code_utils.PostalCode(booking.offerer.postalCode).get_departement_code()
    return _apply_departement_timezone(naive_datetime=date_without_timezone, departement_code=offerer_department_code)


def _apply_departement_timezone(naive_datetime: datetime | None, departement_code: str) -> datetime | None:
    departement_tz = tz.gettz(date_utils.get_department_timezone(departement_code))
    return naive_datetime.astimezone(departement_tz) if naive_datetime is not None else None


def convert_booking_dates_utc_to_venue_timezone(
    date_without_timezone: datetime, booking: "CollectiveBooking | Booking"
) -> datetime | None:
    if booking.venueDepartmentCode:
        return _apply_departement_timezone(
            naive_datetime=date_without_timezone, departement_code=booking.venueDepartmentCode
        )
    offerer_department_code = postal_code_utils.PostalCode(booking.offererPostalCode).get_departement_code()
    return _apply_departement_timezone(naive_datetime=date_without_timezone, departement_code=offerer_department_code)
