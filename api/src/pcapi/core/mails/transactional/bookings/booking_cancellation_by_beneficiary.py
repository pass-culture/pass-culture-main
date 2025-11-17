from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.offers.utils import offer_app_link
from pcapi.utils import date as date_utils
from pcapi.utils.date import default_timezone_to_local_datetime
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email


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
        and beneficiary.deposit.expirationDate > date_utils.get_naive_utc_now()
    ):
        can_book_again = True

    if offer.isEvent:
        if stock.beginningDatetime is None:
            raise ValueError("Can't convert None to local timezone")
        beginning_date_time_in_tz = default_timezone_to_local_datetime(
            stock.beginningDatetime, offer.venue.offererAddress.address.timezone
        )
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
            "FORMATTED_PRICE": format_price(booking.total_amount, beneficiary),
            "USER_FIRST_NAME": beneficiary.firstName,
            "CAN_BOOK_AGAIN": can_book_again,
            "OFFER_LINK": offer_app_link(offer),
        },
    )


def send_booking_cancellation_by_beneficiary_email(booking: Booking) -> None:
    data = get_booking_cancellation_by_beneficiary_email_data(booking)
    mails.send(recipients=[booking.user.email], data=data)
