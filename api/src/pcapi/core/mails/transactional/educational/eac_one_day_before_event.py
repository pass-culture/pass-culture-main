from pcapi.core import mails
from pcapi.core.educational import models as educational_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_hours_for_email


def send_eac_alert_one_day_before_event(booking: educational_models.CollectiveBooking) -> bool:
    if not booking.stock.offer.bookingEmails:  # type: ignore [attr-defined]
        return True
    data = get_eac_one_day_before_event_data(booking)
    return mails.send(
        recipients=[booking.stock.offer.bookingEmails[0]],  # type: ignore [attr-defined]
        bcc_recipients=booking.stock.offer.bookingEmails[1:],  # type: ignore [attr-defined]
        data=data,
    )


def get_eac_one_day_before_event_data(
    booking: educational_models.CollectiveBooking,
) -> models.TransactionalEmailData:
    stock: educational_models.CollectiveStock = booking.stock  # type: ignore [assignment]
    offer: educational_models.CollectiveOffer = stock.offer  # type: ignore [assignment]

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
