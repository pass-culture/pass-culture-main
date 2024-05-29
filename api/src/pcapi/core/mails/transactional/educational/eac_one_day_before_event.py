from pcapi.core import mails
from pcapi.core.educational import models as educational_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_hours_for_email


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
            "VENUE_NAME": offer.venue.name,
            "EVENT_HOUR": format_booking_hours_for_email(booking),
            "QUANTITY": 1,
            "PRICE": str(stock.price) if stock.price > 0 else "Gratuit",
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
        },
    )
