from pcapi.core import mails
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.utils import get_collective_offer_full_address
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime


def send_eac_new_collective_prebooking_email_to_pro(booking: educational_models.CollectiveBooking) -> None:
    recipients = booking.collectiveStock.collectiveOffer.bookingEmails
    if not recipients:
        return

    data = get_eac_new_collective_prebooking_email_data(booking)
    mails.send(recipients=recipients, data=data)


def get_eac_new_collective_prebooking_email_data(
    booking: educational_models.CollectiveBooking,
) -> models.TransactionalEmailData:
    stock = booking.collectiveStock
    offer = stock.collectiveOffer

    return models.TransactionalEmailData(
        template=TransactionalEmail.EAC_NEW_PREBOOKING_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.common_name,
            "EVENT_DATE": get_date_formatted_for_email(get_event_datetime(stock)),
            "EVENT_HOUR": get_time_formatted_for_email(get_event_datetime(stock)),
            "QUANTITY": 1,
            "PRICE": str(stock.price) if stock.price > 0 else "Gratuit",
            "FORMATTED_PRICE": format_price(stock.price, offer.venue),
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": booking.educationalInstitution.postalCode,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "IS_EVENT": True,
            "BOOKING_ID": booking.id,
            "COLLECTIVE_OFFER_ADDRESS": get_collective_offer_full_address(offer),
        },
    )
