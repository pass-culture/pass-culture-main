import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.core import mails
from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import constants as users_constants


def retrieve_data_for_offerer_attachment_invitation_new_user(
    offerer: offerers_models.Offerer,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_NEW_USER.value,
        params={
            "OFFERER_NAME": offerer.name,
            "REGISTRATION_LINK": f"{settings.PRO_URL}/inscription/compte/creation",
        },
    )


def retrieve_data_for_offerer_attachment_invitation_existing_user_with_validated_email(
    offerer: offerers_models.Offerer,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_VALIDATED_USER_EMAIL.value,
        params={"OFFERER_NAME": offerer.name, "JOIN_LINK": settings.PRO_URL},
    )


def retrieve_data_for_offerer_attachment_invitation_existing_user_with_not_validated_email(
    offerer: offerers_models.Offerer, user: users_models.User
) -> models.TransactionalEmailData:
    token = token_utils.Token.get_token(token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, user.id)
    if not token:
        token = token_utils.Token.create(
            token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
            # FIXME (yacine, 2024-04-08): for now, the pro user cannot re-send the token themselves.
            # The default (30 minutes) TTL could thus be too low, so we use an augmented TTL. Once
            # pro users can re-send tokens, we can use the default TTL (EMAIL_VALIDATION_TOKEN_LIFE_TIME).
            ttl=users_constants.EMAIL_VALIDATION_TOKEN_FOR_PRO_LIFE_TIME,
            user_id=user.id,
        )
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_NOT_VALIDATED_USER_EMAIL.value,
        params={
            "OFFERER_NAME": offerer.name,
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/inscription/compte/confirmation/{token.encoded_token}",
        },
    )


def retrieve_data_for_offerer_attachment_invitation_accepted(user: users_models.User) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_ACCEPTED.value, params={"USER_NAME": user.full_name}
    )


def send_offerer_attachment_invitation(
    recipient_emails: list[str], offerer: offerers_models.Offerer, user: users_models.User | None = None
) -> None:
    if user and not user.isEmailValidated:
        data = retrieve_data_for_offerer_attachment_invitation_existing_user_with_not_validated_email(offerer, user)
    elif user:
        data = retrieve_data_for_offerer_attachment_invitation_existing_user_with_validated_email(offerer)
    else:
        data = retrieve_data_for_offerer_attachment_invitation_new_user(offerer)
    mails.send(recipients=recipient_emails, data=data)


def send_offerer_attachment_invitation_accepted(invited_user: users_models.User, receipient_email: str) -> None:
    offerer_attachment_invitation_accepted_data = retrieve_data_for_offerer_attachment_invitation_accepted(invited_user)
    mails.send(recipients=[receipient_email], data=offerer_attachment_invitation_accepted_data)
