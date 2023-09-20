from babel.dates import format_date

from pcapi.core import mails
import pcapi.core.educational.models as educational_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import get_event_datetime


def send_eac_pending_booking_confirmation_limit_date_in_3_days(booking: educational_models.CollectiveBooking) -> bool:
    if not booking.stock.offer.bookingEmails:  # type: ignore [attr-defined]
        return True
    data = get_data_pending_booking_confirmation_limit_date_in_3_days(booking)
    main_recipient, bcc_recipients = [booking.stock.offer.bookingEmails[0]], booking.stock.offer.bookingEmails[1:]  # type: ignore [attr-defined]
    return mails.send(recipients=main_recipient, bcc_recipients=bcc_recipients, data=data)


def get_data_pending_booking_confirmation_limit_date_in_3_days(
    booking: educational_models.CollectiveBooking,
) -> models.TransactionalEmailData:
    stock: educational_models.CollectiveStock = booking.stock  # type: ignore [assignment]
    offer: educational_models.CollectiveOffer = stock.offer  # type: ignore [assignment]

    return models.TransactionalEmailData(
        template=TransactionalEmail.EAC_PENDING_BOOKING_WITH_BOOKING_LIMIT_DATE_3_DAYS.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": format_date(get_event_datetime(stock), format="full", locale="fr"),
            "USER_FIRSTNAME": booking.educationalRedactor.firstName,
            "USER_LASTNAME": booking.educationalRedactor.lastName,
            "USER_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "BOOKING_ID": booking.id,
        },
    )
