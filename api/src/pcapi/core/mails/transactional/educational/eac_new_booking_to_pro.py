from pcapi.core import mails
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def send_eac_new_booking_email_to_pro(booking: CollectiveBooking) -> bool:
    booking_email = booking.collectiveStock.collectiveOffer.bookingEmail
    if not booking_email:
        return True
    data = get_eac_new_booking_to_pro_email_data(booking)
    return mails.send(recipients=[booking_email], data=data)


def get_eac_new_booking_to_pro_email_data(booking: CollectiveBooking) -> models.TransactionalEmailData:
    stock = booking.collectiveStock
    offer = stock.collectiveOffer
    price = f"{stock.price} €" if stock.price > 0 else "Gratuit"
    educational_redactor = booking.educationalRedactor
    educational_institution = booking.educationalInstitution

    return models.TransactionalEmailData(
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
