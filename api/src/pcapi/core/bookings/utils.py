import hmac
import typing
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from hashlib import sha256
from zoneinfo import ZoneInfo

import pytz
from dateutil import tz

import pcapi.utils.date as date_utils
from pcapi import settings
from pcapi.core.categories import subcategories


if typing.TYPE_CHECKING:
    from pcapi.core.bookings.models import Booking
    from pcapi.core.educational.models import CollectiveBooking

QR_CODE_PASS_CULTURE_VERSION = "v3"

SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE = [
    subcategories.SEANCE_CINE.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    subcategories.LIVRE_PAPIER.id,
]

SUGGEST_REACTION_COOLDOWN_IN_SECONDS = {
    subcategories.SEANCE_CINE.id: settings.SUGGEST_REACTION_SHORT_COOLDOWN_IN_SECONDS,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id: settings.SUGGEST_REACTION_LONG_COOLDOWN_IN_SECONDS,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id: settings.SUGGEST_REACTION_LONG_COOLDOWN_IN_SECONDS,
    subcategories.LIVRE_PAPIER.id: settings.SUGGEST_REACTION_LONG_COOLDOWN_IN_SECONDS,
}


def get_qr_code_data(booking_token: str) -> str:
    return f"PASSCULTURE:{QR_CODE_PASS_CULTURE_VERSION};TOKEN:{booking_token}"


def generate_hmac_signature(
    hmac_key: str,
    data: str,
) -> str:
    """
    Generate the signature of the notification data using the hmac_key.
    """
    return hmac.new(hmac_key.encode(), data.encode(), sha256).hexdigest()


def _apply_departement_timezone(naive_datetime: datetime | None, departement_code: str | None) -> datetime | None:
    if naive_datetime is None or departement_code is None:
        return None
    departement_tz = tz.gettz(date_utils.get_department_timezone(departement_code))
    return naive_datetime.astimezone(departement_tz)


def convert_booking_dates_utc_to_venue_timezone(date_without_timezone: datetime, booking: "Booking") -> datetime | None:
    if booking.offerDepartmentCode:
        department_code = booking.offerDepartmentCode
        return _apply_departement_timezone(naive_datetime=date_without_timezone, departement_code=department_code)
    if booking.venueDepartmentCode:
        return _apply_departement_timezone(
            naive_datetime=date_without_timezone, departement_code=booking.venueDepartmentCode
        )
    return _apply_departement_timezone(
        naive_datetime=date_without_timezone, departement_code=booking.venueDepartmentCode
    )


def convert_collective_booking_dates_utc_to_venue_timezone(
    date_without_timezone: datetime, booking: "CollectiveBooking"
) -> datetime | None:
    if booking.venueDepartmentCode:
        return _apply_departement_timezone(
            naive_datetime=date_without_timezone, departement_code=booking.venueDepartmentCode
        )
    return _apply_departement_timezone(
        naive_datetime=date_without_timezone, departement_code=booking.venueDepartmentCode
    )


def get_cooldown_datetime_by_subcategories(sub_category_id: str) -> datetime:
    return date_utils.get_naive_utc_now() - timedelta(
        seconds=(
            SUGGEST_REACTION_COOLDOWN_IN_SECONDS[sub_category_id]
            if sub_category_id in SUGGEST_REACTION_COOLDOWN_IN_SECONDS
            else 0
        )
    )


def convert_date_period_to_utc_datetime_period(
    date_period: tuple[date, date],
    timezone: str,
) -> tuple[datetime, datetime]:
    start_date, end_date = date_period

    # if dates aren't chronologically ordered
    if date_period[0] > date_period[1]:
        end_date, start_date = date_period

    start_datetime = datetime.combine(start_date, time(hour=0, minute=0, second=0), tzinfo=ZoneInfo(timezone))
    end_datetime = datetime.combine(end_date, time(hour=23, minute=59, second=59), tzinfo=ZoneInfo(timezone))

    return (start_datetime.astimezone(pytz.utc), end_datetime.astimezone(pytz.utc))


DEFAULT_PACIFIC_FRANC_TO_EURO_RATE = 0.00838


def convert_euro_to_pacific_franc(price_in_euro: Decimal) -> Decimal:
    """
    Convertit un montant en euros en francs pacifiques (CFP) avec arrondi par tranche de 5 CFP.
    """
    result = float(price_in_euro) / DEFAULT_PACIFIC_FRANC_TO_EURO_RATE
    result = round(result / 5) * 5
    return Decimal(result)
