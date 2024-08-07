from datetime import datetime
import logging

from pcapi import settings
from pcapi.core.bookings.models import Booking
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offers.models import Stock
from pcapi.models import feature
from pcapi.utils.date import utc_datetime_to_department_timezone


logger = logging.getLogger(__name__)


def build_pc_pro_reset_password_link(token_value: str) -> str:
    return f"{settings.PRO_URL}/mot-de-passe-perdu?token={token_value}"


def format_booking_date_for_email(booking: Booking | CollectiveBooking) -> str:
    if isinstance(booking, CollectiveBooking):
        stock = booking.collectiveStock
    else:
        stock = booking.stock
    if not stock.beginningDatetime:
        return ""
    date_in_tz = get_event_datetime(stock)
    return date_in_tz.strftime("%d-%b-%Y")


def format_booking_hours_for_email(booking: Booking | CollectiveBooking) -> str:
    if isinstance(booking, CollectiveBooking):
        stock = booking.collectiveStock
    else:
        stock = booking.stock
    if not stock.beginningDatetime:
        return ""
    date_in_tz = get_event_datetime(stock)
    hour, minute = date_in_tz.hour, date_in_tz.minute
    return f"{hour}h{minute}" if minute else f"{hour}h"


def get_event_datetime(stock: CollectiveStock | Stock) -> datetime:
    if not stock.beginningDatetime:
        raise ValueError("Event stock is missing a beginningDatetime")
    if isinstance(stock, Stock):
        if feature.FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
            if stock.offer.offererAddress:
                departement_code = stock.offer.offererAddress.address.departmentCode
            else:
                departement_code = stock.offer.venue.offererAddress.address.departmentCode
        else:
            departement_code = stock.offer.venue.departementCode
    else:
        departement_code = stock.collectiveOffer.venue.departementCode
    if not departement_code:
        return stock.beginningDatetime
    return utc_datetime_to_department_timezone(stock.beginningDatetime, departement_code)
