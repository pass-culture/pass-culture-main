from typing import Dict
from typing import Union
from urllib.parse import quote

from pcapi.domain.beneficiary.beneficiary import Beneficiary
from pcapi.models import UserSQLEntity
from pcapi.utils.mailing import SUPPORT_EMAIL_ADDRESS
from pcapi.utils.mailing import format_environment_for_email


def get_activation_email_data(user: Union[UserSQLEntity, Beneficiary]) -> Dict:
    first_name = user.firstName.capitalize()
    email = user.email
    token = user.resetPasswordToken
    env = format_environment_for_email()

    return {
        "FromEmail": SUPPORT_EMAIL_ADDRESS,
        "Mj-TemplateID": 994771,
        "Mj-TemplateLanguage": True,
        "To": email,
        "Vars": {"prenom_user": first_name, "token": token, "email": quote(email), "env": env},
    }
