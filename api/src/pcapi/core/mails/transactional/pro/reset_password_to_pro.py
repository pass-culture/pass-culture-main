from typing import Union

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.api import create_reset_password_token
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.models.feature import FeatureToggle
from pcapi.utils.mailing import build_pc_pro_reset_password_link


def get_reset_password_to_pro_email_data(user: User, token: Token) -> Union[dict, SendinblueTransactionalEmailData]:
    reinit_password_url = build_pc_pro_reset_password_link(token.value)
    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "MJ-TemplateID": 779295,
            "MJ-TemplateLanguage": True,
            "Vars": {"lien_nouveau_mdp": reinit_password_url},
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.RESET_PASSWORD_TO_PRO.value,
        params={
            "LIEN_NOUVEAU_MDP": reinit_password_url,
        },
    )


def send_reset_password_to_pro_email(user: User) -> bool:
    token = create_reset_password_token(user)
    data = get_reset_password_to_pro_email_data(user, token)
    return mails.send(recipients=[user.email], data=data)


def get_reset_password_link_to_admin_email_data(created_user: User, reset_password_link: str) -> dict:
    return {
        "Subject": "Création d'un compte pro",
        "Html-part": (
            "<div><div>Bonjour,</div>"
            f"<div>Vous venez de créer le compte de {created_user.firstName} {created_user.lastName}.</div>"
            f"<div>Le lien de création de mot de passe est <a href='{reset_password_link}'>{reset_password_link}</a></div>"
        ),
    }


# FIXME (tgabin, 2022-01-31): below is sendinblue format to send transactional email without template
# The branching mailjet/sendinblue need to be upgraded to take in charge the dictionnary below
# return {
#     "subject": "Création d'un compte pro",
#     "htmlContent": (
#         "<html><head></head><body>"
#         "<div><div>Bonjour,</div>"
#         f"<div>Vous venez de créer le compte de {created_user.firstName} {created_user.lastName}.</div>"
#         f"<div>Le lien de création de mot de passe est <a href='{reset_password_link}'>{reset_password_link}</a></div>"
#         "</body></html>"
#     ),
# }


def send_reset_password_link_to_admin_email(created_user: User, admin_email: User, reset_password_link: str) -> bool:
    data = get_reset_password_link_to_admin_email_data(created_user, reset_password_link)
    return mails.send(recipients=[admin_email], data=data)
