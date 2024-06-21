from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_offerer_individual_subscription_reminder(recipient_email: str) -> None:
    offerer_individual_subscription_reminder_data = models.TransactionalEmailData(
        template=TransactionalEmail.REMINDER_OFFERER_INDIVIDUAL_SUBSCRIPTION.value
    )
    mails.send(recipients=[recipient_email], data=offerer_individual_subscription_reminder_data)
