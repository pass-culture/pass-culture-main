from pcapi.core import mails
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_education_booking_cancellation_by_institution_email_data(
    educational_booking: EducationalBooking,
) -> SendinblueTransactionalEmailData:
    stock = educational_booking.booking.stock
    institution = educational_booking.educationalInstitution
    redactor = educational_booking.educationalRedactor
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION_BY_INSTITUTION.value,
        params={
            "OFFER_NAME": stock.offer.name,
            "EDUCATIONAL_INSTITUTION_NAME": institution.name,
            "VENUE_NAME": stock.offer.venue.name,
            "EVENT_DATE": stock.beginningDatetime.strftime("%d/%m/%Y"),
            "EVENT_HOUR": stock.beginningDatetime.strftime("%H:%M"),
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": institution.postalCode,
        },
    )


def send_education_booking_cancellation_by_institution_email(educational_booking: EducationalBooking) -> bool:
    booking_email = educational_booking.booking.stock.offer.bookingEmail
    if booking_email:
        data = get_education_booking_cancellation_by_institution_email_data(educational_booking)
        return mails.send(recipients=[booking_email], data=data)
    return True  # nothing to send is ok
