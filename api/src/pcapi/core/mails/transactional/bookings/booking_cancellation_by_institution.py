from pcapi.core import mails
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_education_booking_cancellation_by_institution_email_data(
    educational_booking: EducationalBooking,
) -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION_BY_INSTITUTION.value,
        params={
            "OFFER_NAME": educational_booking.booking.stock.offer.name,
            "EVENT_BEGINNING_DATETIME": educational_booking.booking.stock.beginningDatetime.strftime(
                "%d/%m/%Y à %H:%M"
            ),
            "EDUCATIONAL_REDACTOR_EMAIL": educational_booking.educationalRedactor.email,
        },
    )


def send_education_booking_cancellation_by_institution_email(educational_booking: EducationalBooking) -> bool:
    booking_email = educational_booking.booking.stock.offer.bookingEmail
    if booking_email:
        data = get_education_booking_cancellation_by_institution_email_data(educational_booking)
        return mails.send(recipients=[booking_email], data=data)
    return True  # nothing to send is ok
