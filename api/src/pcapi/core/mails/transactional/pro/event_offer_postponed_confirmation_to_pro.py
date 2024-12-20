from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Stock
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.mailing import get_event_datetime


def send_event_offer_postponement_confirmation_email_to_pro(stock: Stock, booking_count: int) -> None:
    offerer_booking_email = stock.offer.venue.bookingEmail
    if not offerer_booking_email:
        return
    data = get_event_offer_postponed_confirmation_to_pro_email_data(stock, booking_count)
    mails.send(recipients=[offerer_booking_email], data=data)


def get_event_offer_postponed_confirmation_to_pro_email_data(
    stock: Stock, booking_count: int
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value,
        params={
            "OFFER_NAME": stock.offer.name,
            "VENUE_NAME": stock.offer.venue.common_name,
            "EVENT_DATE": get_date_formatted_for_email(get_event_datetime(stock)) if stock.offer.isEvent else None,
            "BOOKING_COUNT": booking_count,
            "OFFER_ADDRESS": stock.offer.fullAddress,
        },
    )
