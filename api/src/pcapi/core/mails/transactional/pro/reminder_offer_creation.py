from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_reminder_offer_creation_j5_to_pro(venue_booking_email: str) -> None:
    recipient = venue_booking_email
    if not recipient:
        return
    data = models.TransactionalEmailData(template=TransactionalEmail.REMINDER_OFFER_CREATION_5_DAYS_AFTER_TO_PRO.value)
    mails.send(recipients=[recipient], data=data)


def send_reminder_offer_creation_j10_to_pro(venue_booking_email: str) -> None:
    recipient = venue_booking_email
    if not recipient:
        return
    data = models.TransactionalEmailData(template=TransactionalEmail.REMINDER_OFFER_CREATION_10_DAYS_AFTER_TO_PRO.value)
    mails.send(recipients=[recipient], data=data)
