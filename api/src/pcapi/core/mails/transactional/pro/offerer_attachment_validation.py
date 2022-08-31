from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.models as offerers_models


def get_offerer_attachment_validation_email_data(offerer: offerers_models.Offerer) -> dict:
    return models.SendinblueTransactionalEmailData(  # type: ignore [return-value]
        template=TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value,
        params={"OFFERER_NAME": offerer.name},
    )


def send_offerer_attachment_validation_email_to_pro(user_offerer: offerers_models.UserOfferer) -> bool:
    data = get_offerer_attachment_validation_email_data(user_offerer.offerer)
    return mails.send(recipients=[user_offerer.user.email], data=data)
