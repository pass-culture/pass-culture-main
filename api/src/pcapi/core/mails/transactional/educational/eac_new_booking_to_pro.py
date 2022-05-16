from typing import Union

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def send_eac_new_booking_email_to_pro(booking: Union[Booking, CollectiveBooking]) -> bool:
    if isinstance(booking, Booking):
        booking_email = booking.stock.offer.bookingEmail
    else:
        booking_email = booking.collectiveStock.collectiveOffer.bookingEmail
    if not booking_email:
        return True
    data = get_eac_new_booking_to_pro_email_data(booking)
    return mails.send(recipients=[booking_email], data=data)


def get_eac_new_booking_to_pro_email_data(
    booking: Union[Booking, CollectiveBooking]
) -> SendinblueTransactionalEmailData:
    if isinstance(booking, Booking):
        stock: Stock = booking.stock
        offer: Offer = stock.offer
        price = f"{booking.amount} €" if booking.amount > 0 else "Gratuit"
        educational_redactor: EducationalRedactor = booking.educationalBooking.educationalRedactor  # type: ignore [union-attr]
        educational_institution: EducationalInstitution = booking.educationalBooking.educationalInstitution  # type: ignore [union-attr]
    else:
        # the below [no-redef] happen because the type of the same variable is not consistent in the function
        stock: CollectiveStock = booking.collectiveStock  # type: ignore [no-redef]
        offer: CollectiveOffer = stock.collectiveOffer  # type: ignore [no-redef]
        price = f"{stock.price} €" if stock.price > 0 else "Gratuit"
        educational_redactor: EducationalRedactor = booking.educationalRedactor  # type: ignore [no-redef]
        educational_institution: EducationalInstitution = booking.educationalInstitution  # type: ignore [no-redef]

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EAC_NEW_BOOKING_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": format_booking_date_for_email(booking),
            "EVENT_HOUR": format_booking_hours_for_email(booking),
            "QUANTITY": 1,  #  business rule: It must always be 1
            "PRICE": price,
            "REDACTOR_FIRSTNAME": educational_redactor.firstName,
            "REDACTOR_LASTNAME": educational_redactor.lastName,
            "REDACTOR_EMAIL": educational_redactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": educational_institution.name,
            "EDUCATIONAL_INSTITUTION_CITY": educational_institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": educational_institution.postalCode,
            "IS_EVENT": True,  #  business rule: It must always be True
        },
    )
