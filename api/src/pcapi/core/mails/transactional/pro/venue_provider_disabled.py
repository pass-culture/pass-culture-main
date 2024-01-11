from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_venue_provider_disabled_email(recipient: str) -> None:
    data = models.TransactionalEmailData(template=TransactionalEmail.VENUE_SYNC_DISABLED.value)
    mails.send(recipients=[recipient], data=data)
