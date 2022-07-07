from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalWithoutTemplateEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.api import create_reset_password_token
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.utils.mailing import build_pc_pro_reset_password_link


def get_reset_password_to_pro_email_data(user: User, token: Token) -> SendinblueTransactionalEmailData:
    reinit_password_url = build_pc_pro_reset_password_link(token.value)  # type: ignore [arg-type]

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.RESET_PASSWORD_TO_PRO.value,
        params={
            "LIEN_NOUVEAU_MDP": reinit_password_url,
        },
    )


def send_reset_password_email_to_pro(user: User) -> bool:
    token = create_reset_password_token(user)
    data = get_reset_password_to_pro_email_data(user, token)
    return mails.send(recipients=[user.email], data=data)  # type: ignore [list-item]


def get_reset_password_link_to_admin_email_data(
    created_user: User, reset_password_link: str
) -> SendinblueTransactionalWithoutTemplateEmailData:

    return SendinblueTransactionalWithoutTemplateEmailData(
        subject="Création d'un compte pro",
        html_content=(
            "<html><head></head><body>"
            "<div><div>Bonjour,</div>"
            f"<div>Vous venez de créer le compte de {created_user.firstName} {created_user.lastName}.</div>"
            f"<div>Le lien de création de mot de passe est <a href='{reset_password_link}'>{reset_password_link}</a></div>"
        ),
    )


def send_reset_password_link_to_admin_email(created_user: User, admin_email: User, reset_password_link: str) -> bool:
    data = get_reset_password_link_to_admin_email_data(created_user, reset_password_link)
    return mails.send(recipients=[admin_email], data=data)
