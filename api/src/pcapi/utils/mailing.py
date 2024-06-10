from datetime import datetime
import logging

from pcapi import settings
from pcapi.core.bookings.models import Booking
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offers.models import Stock
from pcapi.utils.date import utc_datetime_to_department_timezone


logger = logging.getLogger(__name__)


def build_pc_pro_reset_password_link(token_value: str) -> str:
    return f"{settings.PRO_URL}/mot-de-passe-perdu?token={token_value}"


def format_booking_date_for_email(booking: Booking | CollectiveBooking) -> str:
    if isinstance(booking, CollectiveBooking) or booking.stock.offer.isEvent:
        stock = booking.collectiveStock if isinstance(booking, CollectiveBooking) else booking.stock
        date_in_tz = get_event_datetime(stock)  # type: ignore[arg-type]
        offer_date = date_in_tz.strftime("%d-%b-%Y")
        return offer_date
    return ""


def format_booking_hours_for_email(booking: Booking | CollectiveBooking) -> str:
    if isinstance(booking, CollectiveBooking) or booking.stock.offer.isEvent:
        stock = booking.collectiveStock if isinstance(booking, CollectiveBooking) else booking.stock
        date_in_tz = get_event_datetime(stock)  # type: ignore[arg-type]
        event_hour = date_in_tz.hour
        event_minute = date_in_tz.minute
        return f"{event_hour}h" if event_minute == 0 else f"{event_hour}h{event_minute}"
    return ""


def get_event_datetime(stock: CollectiveStock | Stock) -> datetime:
    if isinstance(stock, Stock):
        departement_code = stock.offer.departementCode
    else:
        departement_code = stock.collectiveOffer.departementCode
    if departement_code is not None:
        date_in_utc = stock.beginningDatetime
        if date_in_utc is None:
            raise ValueError("Can't convert None to local timezone")
        date_in_tz = utc_datetime_to_department_timezone(date_in_utc, departement_code)
    else:
        date_in_tz = stock.beginningDatetime  # type: ignore[assignment]

    return date_in_tz
