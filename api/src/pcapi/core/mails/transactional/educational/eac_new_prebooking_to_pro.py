from babel.dates import format_date

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import get_event_datetime


def send_eac_new_prebooking_email_to_pro(stock: Stock, booking: Booking) -> bool:
    if not booking.stock.offer.bookingEmail:
        return True
    data = get_eac_new_prebooking_email_data(booking)
    return mails.send(recipients=[stock.offer.bookingEmail], data=data)  # type: ignore [list-item]


def get_eac_new_prebooking_email_data(booking: Booking) -> dict:
    stock: Stock = booking.stock
    offer: Offer = stock.offer
    educational_booking: EducationalBooking = booking.educationalBooking  # type: ignore [assignment]

    return SendinblueTransactionalEmailData(  # type: ignore [return-value]
        template=TransactionalEmail.EAC_NEW_PREBOOKING_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": format_date(
                get_event_datetime(educational_booking.booking.stock), format="full", locale="fr"
            ),
            "EVENT_HOUR": format_booking_hours_for_email(booking),
            "QUANTITY": booking.quantity,
            "PRICE": str(booking.amount) if booking.amount > 0 else "Gratuit",
            "REDACTOR_FIRSTNAME": educational_booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": educational_booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": educational_booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": educational_booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": educational_booking.educationalInstitution.postalCode,
            "EDUCATIONAL_INSTITUTION_NAME": educational_booking.educationalInstitution.name,
            "IS_EVENT": offer.isEvent,
        },
    )


def send_eac_new_collective_prebooking_email_to_pro(booking: CollectiveBooking) -> bool:
    if not booking.collectiveStock.collectiveOffer.bookingEmail:
        return True
    data = get_eac_new_collective_prebooking_email_data(booking)
    return mails.send(recipients=[booking.collectiveStock.collectiveOffer.bookingEmail], data=data)


def get_eac_new_collective_prebooking_email_data(booking: CollectiveBooking) -> SendinblueTransactionalEmailData:
    stock: Stock = booking.collectiveStock
    offer: Offer = stock.collectiveOffer

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EAC_NEW_PREBOOKING_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": format_date(get_event_datetime(booking.collectiveStock), format="full", locale="fr"),
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
