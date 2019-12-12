from typing import Dict

from models import User
from utils.mailing import SUPPORT_EMAIL_ADDRESS, format_environment_for_email


def get_activation_email_data(user: User) -> Dict:
    first_name = user.firstName.capitalize()
    email = user.email
    token = user.resetPasswordToken
    env = format_environment_for_email()

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'Mj-TemplateID': 994771,
        'Mj-TemplateLanguage': True,
        'To': email,
        'Vars': {
            'prenom_user': first_name,
            'token': token,
            'email': email,
            'env': env
        },
    }
