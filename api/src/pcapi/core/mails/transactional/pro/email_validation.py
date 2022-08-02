from pcapi import settings
from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import Token
from pcapi.core.users.models import User


def get_email_validation_to_pro_email_data(user: User) -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EMAIL_VALIDATION_TO_PRO.value,
        params={
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/inscription/validation/{user.validationToken}",
        },
    )


def send_email_validation_to_pro_email(user: User) -> bool:
    data = get_email_validation_to_pro_email_data(user)
    return mails.send(recipients=[user.email], data=data)


def get_email_validation_to_admin_email_data(token: str) -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EMAIL_VALIDATION_TO_PRO.value,
        params={
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/creation-de-mot-de-passe/{token}",
        },
    )


def send_email_validation_to_admin_email(user: User, token: Token) -> bool:
    data = get_email_validation_to_admin_email_data(token.value)  # type: ignore [arg-type]
    return mails.send(recipients=[user.email], data=data)
