import datetime

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.utils import offer_app_link
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone


def get_booking_cancellation_by_beneficiary_email_data(
    booking: Booking,
) -> models.TransactionalEmailData:
    stock = booking.stock
    beneficiary = booking.user
    offer = stock.offer
    is_free_offer = stock.price == 0
    can_book_again = False
    if (
        beneficiary.deposit
        and beneficiary.deposit.expirationDate
        and beneficiary.deposit.expirationDate > datetime.datetime.utcnow()
    ):
        can_book_again = True

    if offer.isEvent:
        if stock.beginningDatetime is None:
            raise ValueError("Can't convert None to local timezone")
        beginning_date_time_in_tz = utc_datetime_to_department_timezone(stock.beginningDatetime, offer.departementCode)
        event_date = get_date_formatted_for_email(beginning_date_time_in_tz)
        event_hour = get_time_formatted_for_email(beginning_date_time_in_tz)
    else:
        event_date = None
        event_hour = None

    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY.value,
        params={
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "IS_FREE_OFFER": is_free_offer,
            "IS_EVENT": offer.isEvent,
            "IS_EXTERNAL": booking.isExternal,
            "OFFER_NAME": offer.name,
            "OFFER_PRICE": float(booking.total_amount),
            "USER_FIRST_NAME": beneficiary.firstName,
            "CAN_BOOK_AGAIN": can_book_again,
            "OFFER_LINK": offer_app_link(offer),
        },
    )


def send_booking_cancellation_by_beneficiary_email(booking: Booking) -> None:
    data = get_booking_cancellation_by_beneficiary_email_data(booking)
    mails.send(recipients=[booking.user.email], data=data)
