from babel.dates import format_date

from pcapi.core import mails
import pcapi.core.educational.models as educational_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import get_event_datetime


def send_eac_new_collective_prebooking_email_to_pro(booking: educational_models.CollectiveBooking) -> bool:
    if not booking.collectiveStock.collectiveOffer.bookingEmail:
        return True
    data = get_eac_new_collective_prebooking_email_data(booking)
    return mails.send(recipients=[booking.collectiveStock.collectiveOffer.bookingEmail], data=data)


def get_eac_new_collective_prebooking_email_data(
    booking: educational_models.CollectiveBooking,
) -> models.TransactionalEmailData:
    stock: educational_models.CollectiveStock = booking.collectiveStock  # type: ignore [assignment]
    offer: educational_models.CollectiveOffer = stock.collectiveOffer  # type: ignore [assignment]

    return models.TransactionalEmailData(
        template=TransactionalEmail.EAC_NEW_PREBOOKING_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": format_date(get_event_datetime(stock), format="full", locale="fr"),
            "EVENT_HOUR": format_booking_hours_for_email(booking),
            "QUANTITY": 1,
            "PRICE": str(stock.price) if stock.price > 0 else "Gratuit",
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": booking.educationalInstitution.postalCode,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "IS_EVENT": True,
        },
    )
