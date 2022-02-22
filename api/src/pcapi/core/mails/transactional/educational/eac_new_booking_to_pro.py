from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def send_eac_new_booking_email_to_pro(booking: Booking) -> bool:
    booking_email = booking.stock.offer.bookingEmail
    if not booking_email:
        return True
    data = get_eac_new_booking_to_pro_email_data(booking)
    return mails.send(recipients=[booking_email], data=data)


def get_eac_new_booking_to_pro_email_data(booking: Booking) -> SendinblueTransactionalEmailData:
    stock: Stock = booking.stock
    offer: Offer = stock.offer
    educational_booking: EducationalBooking = booking.educationalBooking

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EAC_NEW_BOOKING_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": format_booking_date_for_email(booking),
            "EVENT_HOUR": format_booking_hours_for_email(booking),
            "QUANTITY": booking.quantity,
            "REDACTOR_FIRSTNAME": educational_booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": educational_booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": educational_booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": educational_booking.educationalInstitution.name,
            "EDUCATIONAL_INSTITUTION_CITY": educational_booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": educational_booking.educationalInstitution.postalCode,
            "IS_EVENT": offer.isEvent,
        },
    )
