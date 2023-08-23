from pcapi import settings
from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.models as users_models


def retrieve_data_for_offerer_attachment_invitation_new_user(
    offerer: offerers_models.Offerer,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_NEW_USER.value, params={"OFFERER_NAME": offerer.name}
    )


def retrieve_data_for_offerer_attachment_invitation_existing_user_with_validated_email(
    offerer: offerers_models.Offerer,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_VALIDATED_USER_EMAIL.value,
        params={"OFFERER_NAME": offerer.name},
    )


def retrieve_data_for_offerer_attachment_invitation_existing_user_with_not_validated_email(
    offerer: offerers_models.Offerer, user: users_models.User
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_NOT_VALIDATED_USER_EMAIL.value,
        params={
            "OFFERER_NAME": offerer.name,
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/inscription/validation/{user.validationToken}",
        },
    )


def retrieve_data_for_offerer_attachment_invitation_accepted() -> models.TransactionalEmailData:
    return models.TransactionalEmailData(template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_ACCEPTED.value)


def retrieve_data_for_offerer_attachment_invitation_confirmed() -> models.TransactionalEmailData:
    return models.TransactionalEmailData(template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_CONFIRMED.value)


def send_offerer_attachment_invitation(
    recipient_emails: list[str], offerer: offerers_models.Offerer, user: users_models.User | None = None
) -> bool:
    if user and not user.isEmailValidated:
        data = retrieve_data_for_offerer_attachment_invitation_existing_user_with_not_validated_email(offerer, user)
    elif user:
        data = retrieve_data_for_offerer_attachment_invitation_existing_user_with_validated_email(offerer)
    else:
        data = retrieve_data_for_offerer_attachment_invitation_new_user(offerer)
    return mails.send(recipients=recipient_emails, data=data)


def send_offerer_attachment_invitation_accepted(receipient_emails: list[str]) -> bool:
    offerer_attachment_invitation_accepted_data = retrieve_data_for_offerer_attachment_invitation_accepted()
    return mails.send(recipients=receipient_emails, data=offerer_attachment_invitation_accepted_data)


def send_offerer_attachment_invitation_confirmed(recipient_emails: list[str]) -> bool:
    offerer_attachment_invitation_confirmed = retrieve_data_for_offerer_attachment_invitation_confirmed()
    return mails.send(recipients=recipient_emails, data=offerer_attachment_invitation_confirmed)
