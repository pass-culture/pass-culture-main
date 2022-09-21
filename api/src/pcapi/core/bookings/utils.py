from datetime import datetime

from dateutil import tz

import pcapi.utils.date as date_utils
import pcapi.utils.postal_code as postal_code_utils


def _apply_departement_timezone(naive_datetime: datetime, departement_code: str) -> datetime:
    departement_tz = tz.gettz(date_utils.get_department_timezone(departement_code))
    return naive_datetime.astimezone(departement_tz) if naive_datetime is not None else None


def convert_booking_dates_utc_to_venue_timezone(date_without_timezone: datetime, booking: object) -> datetime:
    if booking.venueDepartmentCode:  # type: ignore [attr-defined]
        return _apply_departement_timezone(
            naive_datetime=date_without_timezone, departement_code=booking.venueDepartmentCode  # type: ignore [attr-defined]
        )
    offerer_department_code = postal_code_utils.PostalCode(booking.offererPostalCode).get_departement_code()  # type: ignore [attr-defined]
    return _apply_departement_timezone(naive_datetime=date_without_timezone, departement_code=offerer_department_code)
