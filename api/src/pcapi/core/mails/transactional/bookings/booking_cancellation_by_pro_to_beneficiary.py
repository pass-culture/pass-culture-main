from typing import Union

from babel.dates import format_date

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.models.feature import FeatureToggle
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import get_event_datetime


def get_booking_cancellation_by_pro_to_beneficiary_email_data(
    booking: Booking,
) -> Union[dict, SendinblueTransactionalEmailData]:
    stock = booking.stock
    offer = stock.offer
    if offer.isEvent:
        event_date = format_date(get_event_datetime(stock), format="full", locale="fr")
        event_hour = format_booking_hours_for_email(booking)
    else:
        event_date = None
        event_hour = None

    is_free_offer = stock.price == 0
    venue_name = offer.venue.publicName if offer.venue.publicName else offer.venue.name

    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "MJ-TemplateID": 1116690,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "event_date": event_date if event_date else "",
                "event_hour": event_hour if event_hour else "",
                "is_event": int(offer.isEvent),
                "is_free_offer": int(is_free_offer),
                "is_online": int(offer.isDigital),
                "is_thing": int(not offer.isDigital and offer.isThing),
                "offer_name": offer.name,
                "offer_price": str(booking.total_amount),
                "offerer_name": offer.venue.managingOfferer.name,
                "user_first_name": booking.firstName,
                "user_last_name": booking.lastName,
                "venue_name": venue_name,
            },
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value,
        params={
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "IS_EVENT": offer.isEvent,
            "IS_FREE_OFFER": is_free_offer,
            "IS_ONLINE": offer.isDigital,
            "IS_THING": not offer.isDigital and offer.isThing,
            "OFFER_NAME": offer.name,
            "OFFER_PRICE": booking.total_amount,
            "OFFERER_NAME": offer.venue.managingOfferer.name,
            "USER_FIRST_NAME": booking.firstName,
            "USER_LAST_NAME": booking.lastName,
            "VENUE_NAME": venue_name,
        },
    )


def send_booking_cancellation_by_pro_to_beneficiary_email(booking: Booking) -> bool:
    data = get_booking_cancellation_by_pro_to_beneficiary_email_data(booking)
    return mails.send(recipients=[booking.email], data=data)
