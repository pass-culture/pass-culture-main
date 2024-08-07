from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.repository import find_new_offerer_user_email


def get_new_offerer_validation_email_data(offerer: Offerer) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.NEW_OFFERER_VALIDATION.value, params={"OFFERER_NAME": offerer.name}
    )


def send_new_offerer_validation_email_to_pro(offerer: Offerer) -> None:
    offerer_email = find_new_offerer_user_email(offerer.id)
    data = get_new_offerer_validation_email_data(offerer)
    mails.send(recipients=[offerer_email], data=data)


def get_new_offerer_rejection_email_data(offerer: Offerer) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.NEW_OFFERER_REJECTION.value,
        params={
            "OFFERER_NAME": offerer.name,
            "REJECTION_REASON": offerer.rejectionReason.name if offerer.rejectionReason else "",
        },
    )


def send_new_offerer_rejection_email_to_pro(offerer: Offerer) -> None:
    offerer_email = find_new_offerer_user_email(offerer.id)
    data = get_new_offerer_rejection_email_data(offerer)
    mails.send(recipients=[offerer_email], data=data)
