from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Offerer
from pcapi.models.user_offerer import UserOfferer


def get_offerer_attachment_validation_email_data(offerer: Offerer) -> dict:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value, params={"OFFERER_NAME": offerer.name}
    )


def send_offerer_attachment_validation_email_to_pro(user_offerer: UserOfferer) -> bool:
    data = get_offerer_attachment_validation_email_data(user_offerer.offerer)
    return mails.send(recipients=[user_offerer.user.email], data=data)
