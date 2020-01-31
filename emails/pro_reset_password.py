from typing import Dict

from models import User
from repository.feature_queries import feature_send_mail_to_users_enabled
from utils.mailing import SUPPORT_EMAIL_ADDRESS, DEV_EMAIL_ADDRESS, format_environment_for_email
from utils.config import API_URL

def retrieve_data_for_reset_password_pro_email(user: User) -> Dict:
    user_email = user.email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS
    user_reset_password_token = user.resetPasswordToken
    env = format_environment_for_email()
    reinit_password_url = f'{API_URL}/mot-de-passe-perdu?token=?token{user_reset_password_token}'

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 779295,
        'MJ-TemplateLanguage': True,
        'To': user_email,
        'Vars':
            {
                'lien_nouveau_mdp': reinit_password_url,
                'env': env
            }
    }
