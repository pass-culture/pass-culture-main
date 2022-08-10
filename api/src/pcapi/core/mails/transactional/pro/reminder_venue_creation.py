from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.repository import find_new_offerer_user_email
from pcapi.settings import PRO_URL
from pcapi.utils.human_ids import humanize


def get_reminder_venue_creation_email_data(offerer: Offerer) -> SendinblueTransactionalEmailData:

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.REMINDER_VENUE_CREATION_TO_PRO.value,
        params={
            "PRO_URL": PRO_URL,
            "OFFERER_ID": humanize(offerer.id),
        },
    )


def send_reminder_venue_creation_to_pro(offerer: Offerer) -> bool:
    recipient = find_new_offerer_user_email(offerer.id)
    if not recipient:
        return True
    data = get_reminder_venue_creation_email_data(offerer)
    return mails.send(recipients=[recipient], data=data)
