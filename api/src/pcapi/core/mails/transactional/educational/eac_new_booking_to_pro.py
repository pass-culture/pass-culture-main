from pcapi.core import mails
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.utils import get_collective_offer_full_address
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime


def send_eac_new_booking_email_to_pro(booking: CollectiveBooking) -> None:
    booking_emails = booking.collectiveStock.collectiveOffer.bookingEmails
    if not booking_emails:
        return
    data = get_eac_new_booking_to_pro_email_data(booking)
    main_recipient, bcc_recipients = [booking_emails[0]], booking_emails[1:]

    mails.send(recipients=main_recipient, bcc_recipients=bcc_recipients, data=data)


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
            "VENUE_NAME": offer.venue.common_name,
            "EVENT_DATE": get_date_formatted_for_email(get_event_datetime(stock)),
            "EVENT_HOUR": get_time_formatted_for_email(get_event_datetime(stock)),
            "QUANTITY": 1,  #  business rule: It must always be 1
            "PRICE": price,
            "FORMATTED_PRICE": format_price(stock.price, offer.venue),
            "REDACTOR_FIRSTNAME": educational_redactor.firstName,
            "REDACTOR_LASTNAME": educational_redactor.lastName,
            "REDACTOR_EMAIL": educational_redactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": educational_institution.name,
            "EDUCATIONAL_INSTITUTION_CITY": educational_institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": educational_institution.postalCode,
            "IS_EVENT": True,  #  business rule: It must always be True
            "BOOKING_ID": booking.id,
            "COLLECTIVE_OFFER_ADDRESS": get_collective_offer_full_address(offer),
        },
    )
