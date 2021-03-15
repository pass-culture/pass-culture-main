from typing import Dict

from pcapi import settings
from pcapi.core.users.models import Token
from pcapi.core.users.models import User


def retrieve_data_for_reset_password_pro_email(user: User, token: Token) -> Dict:
    reinit_password_url = f"{settings.PRO_URL}/mot-de-passe-perdu?token={token.value}"

    return {
        "MJ-TemplateID": 779295,
        "MJ-TemplateLanguage": True,
        "Vars": {"lien_nouveau_mdp": reinit_password_url},
    }
