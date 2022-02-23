from babel.dates import format_date

from pcapi.core import mails
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import get_event_datetime


def get_eac_satisfaction_study_to_pro_email_data(
    educational_booking: EducationalBooking,
) -> SendinblueTransactionalEmailData:
    event_date = format_date(get_event_datetime(educational_booking.booking.stock), format="full", locale="fr")
    offer = educational_booking.booking.stock.offer

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EAC_SATISFACTION_STUDY_TO_PRO.value,
        params={
            "EVENT_DATE": event_date or "",
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.publicName if offer.venue.publicName else offer.venue.name,
            "REDACTOR_FIRSTNAME": educational_booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": educational_booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": educational_booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": educational_booking.educationalInstitution.name,
            "EDUCATIONAL_INSTITUTION_CITY": educational_booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": educational_booking.educationalInstitution.postalCode,
        },
    )


def send_eac_satisfaction_study_email_to_pro(educational_booking: EducationalBooking) -> bool:
    data = get_eac_satisfaction_study_to_pro_email_data(educational_booking)
    return mails.send(recipients=[educational_booking.booking.stock.offer.venue.bookingEmail], data=data)
