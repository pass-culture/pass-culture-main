from typing import Union

from pcapi.core import mails
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_education_booking_cancellation_by_institution_email_data(
    booking: Union[CollectiveBooking, EducationalBooking],
) -> SendinblueTransactionalEmailData:
    if isinstance(booking, CollectiveBooking):
        stock = booking.collectiveStock
        offer = stock.collectiveOffer
    else:
        stock = booking.booking.stock
        offer = stock.offer
    institution = booking.educationalInstitution
    redactor = booking.educationalRedactor
    return SendinblueTransactionalEmailData(
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


def send_education_booking_cancellation_by_institution_email(
    booking: Union[CollectiveBooking, EducationalBooking]
) -> bool:
    if isinstance(booking, CollectiveBooking):
        booking_email = booking.collectiveStock.collectiveOffer.bookingEmail
    else:
        booking_email = booking.booking.stock.offer.bookingEmail
    if booking_email:
        data = get_education_booking_cancellation_by_institution_email_data(booking)
        return mails.send(recipients=[booking_email], data=data)
    return True  # nothing to send is ok
