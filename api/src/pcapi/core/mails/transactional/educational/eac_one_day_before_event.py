from pcapi.core import mails
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.utils import get_collective_offer_full_address
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime


def send_eac_alert_one_day_before_event(booking: educational_models.CollectiveBooking) -> None:
    if not booking.collectiveStock.collectiveOffer.bookingEmails:
        return
    data = get_eac_one_day_before_event_data(booking)
    mails.send(
        recipients=[booking.collectiveStock.collectiveOffer.bookingEmails[0]],
        bcc_recipients=booking.collectiveStock.collectiveOffer.bookingEmails[1:],
        data=data,
    )


def get_eac_one_day_before_event_data(
    booking: educational_models.CollectiveBooking,
) -> models.TransactionalEmailData:
    stock = booking.collectiveStock
    offer = stock.collectiveOffer

    return models.TransactionalEmailData(
        template=TransactionalEmail.EAC_ONE_DAY_BEFORE_EVENT.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.common_name,
            "EVENT_HOUR": get_time_formatted_for_email(get_event_datetime(stock)),
            "QUANTITY": 1,
            "PRICE": str(stock.price) if stock.price > 0 else "Gratuit",
            "FORMATTED_PRICE": format_price(stock.price, offer.venue),
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "COLLECTIVE_OFFER_ADDRESS": get_collective_offer_full_address(offer),
        },
    )
