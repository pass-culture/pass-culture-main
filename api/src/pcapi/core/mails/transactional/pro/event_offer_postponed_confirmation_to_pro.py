from babel.dates import format_date

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Stock
from pcapi.utils.mailing import get_event_datetime


def send_event_offer_postponement_confirmation_email_to_pro(stock: Stock, booking_count: int) -> bool:
    offerer_booking_email = stock.offer.venue.bookingEmail
    if not offerer_booking_email:
        return True
    data = get_event_offer_postponed_confirmation_to_pro_email_data(stock, booking_count)
    return mails.send(recipients=[offerer_booking_email], data=data)


def get_event_offer_postponed_confirmation_to_pro_email_data(
    stock: Stock, booking_count: int
) -> models.SendinblueTransactionalEmailData:
    return models.SendinblueTransactionalEmailData(
        template=TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value,
        params={
            "OFFER_NAME": stock.offer.name,
            "VENUE_NAME": stock.offer.venue.publicName or stock.offer.venue.name,
            "EVENT_DATE": format_date(get_event_datetime(stock), format="full", locale="fr")
            if stock.offer.isEvent
            else None,
            "BOOKING_COUNT": booking_count,
        },
    )
