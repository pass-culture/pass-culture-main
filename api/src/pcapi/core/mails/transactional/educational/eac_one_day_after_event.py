from pcapi.core import mails
from pcapi.core.educational import models as educational_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def send_eac_alert_one_day_after_event(booking: educational_models.CollectiveBooking) -> None:
    if not booking.collectiveStock.collectiveOffer.bookingEmails:
        return
    data = get_eac_one_day_after_event_data(booking)
    mails.send(
        recipients=[booking.collectiveStock.collectiveOffer.bookingEmails[0]],
        bcc_recipients=booking.collectiveStock.collectiveOffer.bookingEmails[1:],
        data=data,
    )


def get_eac_one_day_after_event_data(
    booking: educational_models.CollectiveBooking,
) -> models.TransactionalEmailData:
    stock = booking.collectiveStock
    offer = stock.collectiveOffer

    return models.TransactionalEmailData(
        template=TransactionalEmail.EAC_ONE_DAY_AFTER_EVENT.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": format_booking_date_for_email(booking),
            "EVENT_HOUR": format_booking_hours_for_email(booking),
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
        },
    )
