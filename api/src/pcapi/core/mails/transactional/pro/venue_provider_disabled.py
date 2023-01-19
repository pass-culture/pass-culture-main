from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Venue


def send_venue_provider_disabled_email(recipient: str) -> bool:
    data = models.TransactionalEmailData(template=TransactionalEmail.VENUE_SYNC_DISABLED.value)
    return mails.send(recipients=[recipient], data=data)
