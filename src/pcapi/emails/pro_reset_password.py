from typing import Dict

from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.utils.mailing import build_pc_pro_reset_password_link


def retrieve_data_for_reset_password_pro_email(user: User, token: Token) -> Dict:
    reinit_password_url = build_pc_pro_reset_password_link(token.value)

    return {
        "MJ-TemplateID": 779295,
        "MJ-TemplateLanguage": True,
        "Vars": {"lien_nouveau_mdp": reinit_password_url},
    }


def retrieve_data_for_reset_password_link_to_admin_email(created_user: User, reset_password_link: str) -> Dict:
    return {
        "Subject": "Création d'un compte pro",
        "Html-part": (
            "<div><div>Bonjour,</div>"
            f"<div>Vous venez de créer le compte de {created_user.firstName} {created_user.lastName}.</div>"
            f"<div>Le lien de création de mot de passe est <a href='{reset_password_link}'>{reset_password_link}</a></div>"
        ),
    }
