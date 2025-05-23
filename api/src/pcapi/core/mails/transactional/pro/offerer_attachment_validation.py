import pcapi.core.offerers.models as offerers_models
from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_offerer_attachment_validation_email_data(
    offerer: offerers_models.Offerer,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value,
        params={"OFFERER_NAME": offerer.name},
    )


def send_offerer_attachment_validation_email_to_pro(user_offerer: offerers_models.UserOfferer) -> None:
    data = get_offerer_attachment_validation_email_data(user_offerer.offerer)
    mails.send(recipients=[user_offerer.user.email], data=data)


def get_offerer_attachment_rejection_email_data(
    offerer: offerers_models.Offerer,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_REJECTION.value, params={"OFFERER_NAME": offerer.name}
    )


def send_offerer_attachment_rejection_email_to_pro(user_offerer: offerers_models.UserOfferer) -> None:
    data = get_offerer_attachment_rejection_email_data(user_offerer.offerer)
    mails.send(recipients=[user_offerer.user.email], data=data)
