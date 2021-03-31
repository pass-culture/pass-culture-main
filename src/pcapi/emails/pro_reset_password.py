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
