from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_venue_provider_deleted_email(recipient: str) -> bool:
    data = models.TransactionalEmailData(template=TransactionalEmail.VENUE_SYNC_DELETED.value)
    return mails.send(recipients=[recipient], data=data)
