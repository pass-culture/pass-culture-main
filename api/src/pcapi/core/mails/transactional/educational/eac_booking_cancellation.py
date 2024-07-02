from pcapi.core import mails
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_education_booking_cancellation_email_data(booking: CollectiveBooking) -> models.TransactionalEmailData:
    stock = booking.collectiveStock
    offer = stock.collectiveOffer
    institution = booking.educationalInstitution
    redactor = booking.educationalRedactor
    return models.TransactionalEmailData(
        template=TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION.value,
        params={
            "OFFER_NAME": offer.name,
            "EDUCATIONAL_INSTITUTION_NAME": institution.name,
            "VENUE_NAME": offer.venue.common_name,
            "EVENT_DATE": stock.beginningDatetime.strftime("%d/%m/%Y"),
            "EVENT_HOUR": stock.beginningDatetime.strftime("%H:%M"),
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": institution.postalCode,
            "COLLECTIVE_CANCELLATION_REASON": booking.cancellationReason.value if booking.cancellationReason else "",
            "BOOKING_ID": booking.id,
        },
    )


def send_eac_booking_cancellation_email(booking: CollectiveBooking) -> None:
    booking_emails = booking.collectiveStock.collectiveOffer.bookingEmails
    if not booking_emails:
        return
    data = get_education_booking_cancellation_email_data(booking)
    main_recipient, bcc_recipients = [booking_emails[0]], booking_emails[1:]
    mails.send(recipients=main_recipient, bcc_recipients=bcc_recipients, data=data)
