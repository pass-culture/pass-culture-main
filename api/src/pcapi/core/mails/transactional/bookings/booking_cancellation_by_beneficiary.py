import datetime

from pcapi.core import mails
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.utils import offer_app_link
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone


def get_booking_cancellation_by_beneficiary_email_data(
    individual_booking: IndividualBooking,
) -> models.TransactionalEmailData:
    stock = individual_booking.booking.stock
    beneficiary = individual_booking.user
    offer = stock.offer
    is_free_offer = stock.price == 0
    can_book_again = beneficiary.deposit.expirationDate > datetime.datetime.utcnow()

    if offer.isEvent:
        beginning_date_time_in_tz = utc_datetime_to_department_timezone(
            stock.beginningDatetime, offer.venue.departementCode
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
            "IS_EXTERNAL": individual_booking.booking.isExternal,
            "OFFER_NAME": offer.name,
            "OFFER_PRICE": float(individual_booking.booking.total_amount),
            "USER_FIRST_NAME": beneficiary.firstName,
            "CAN_BOOK_AGAIN": can_book_again,
            "OFFER_LINK": offer_app_link(offer),
        },
    )


def send_booking_cancellation_by_beneficiary_email(individual_booking: IndividualBooking) -> bool:
    data = get_booking_cancellation_by_beneficiary_email_data(individual_booking)
    return mails.send(recipients=[individual_booking.user.email], data=data)
