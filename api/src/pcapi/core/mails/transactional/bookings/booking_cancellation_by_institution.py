from pcapi.core import mails
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_education_booking_cancellation_by_institution_email_data(
    booking: CollectiveBooking,
) -> models.TransactionalEmailData:
    stock = booking.collectiveStock
    offer = stock.collectiveOffer
    institution = booking.educationalInstitution
    redactor = booking.educationalRedactor
    return models.TransactionalEmailData(
        template=TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION_BY_INSTITUTION.value,
        params={
            "OFFER_NAME": offer.name,
            "EDUCATIONAL_INSTITUTION_NAME": institution.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": stock.beginningDatetime.strftime("%d/%m/%Y"),
            "EVENT_HOUR": stock.beginningDatetime.strftime("%H:%M"),
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": institution.postalCode,
        },
    )


def send_education_booking_cancellation_by_institution_email(booking: CollectiveBooking) -> bool:
    booking_email = booking.collectiveStock.collectiveOffer.bookingEmail
    if not booking_email:
        return True
    data = get_education_booking_cancellation_by_institution_email_data(booking)
    return mails.send(recipients=[booking_email], data=data)
