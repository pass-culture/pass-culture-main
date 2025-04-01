from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime


def get_booking_cancellation_by_pro_to_beneficiary_email_data(
    booking: Booking,
    rejected_by_fraud_action: bool,
) -> models.TransactionalEmailData:
    stock = booking.stock
    offer = stock.offer
    if offer.isEvent:
        event_date = get_date_formatted_for_email(get_event_datetime(stock))
        event_hour = get_time_formatted_for_email(get_event_datetime(stock))
    else:
        event_date = None
        event_hour = None

    is_free_offer = stock.price == 0

    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value,
        params={
            "BOOKING_CONTACT": offer.bookingContact,
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "IS_EVENT": offer.isEvent,
            "IS_FREE_OFFER": is_free_offer,
            "IS_ONLINE": offer.isDigital,
            "IS_THING": not offer.isDigital and offer.isThing,
            "IS_EXTERNAL": booking.isExternal,
            "OFFER_NAME": offer.name,
            "OFFER_PRICE": booking.total_amount,
            "OFFERER_NAME": offer.venue.managingOfferer.name,
            "REASON": booking.cancellationReason.value if booking.cancellationReason else None,
            "REJECTED": rejected_by_fraud_action,
            "USER_FIRST_NAME": booking.firstName,
            "USER_LAST_NAME": booking.lastName,
            "VENUE_NAME": offer.venue.common_name,
        },
    )


def send_booking_cancellation_by_pro_to_beneficiary_email(
    booking: Booking, rejected_by_fraud_action: bool = False
) -> None:
    data = get_booking_cancellation_by_pro_to_beneficiary_email_data(booking, rejected_by_fraud_action)
    mails.send(recipients=[booking.email], data=data)
