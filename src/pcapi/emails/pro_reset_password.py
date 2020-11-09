from typing import Dict

from pcapi.models import UserSQLEntity
from pcapi.repository.feature_queries import feature_send_mail_to_users_enabled
from pcapi.utils.config import PRO_URL
from pcapi.utils.mailing import DEV_EMAIL_ADDRESS
from pcapi.utils.mailing import SUPPORT_EMAIL_ADDRESS
from pcapi.utils.mailing import format_environment_for_email


def retrieve_data_for_reset_password_pro_email(user: UserSQLEntity) -> Dict:
    user_email = user.email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS
    user_reset_password_token = user.resetPasswordToken
    env = format_environment_for_email()
    reinit_password_url = f'{PRO_URL}/mot-de-passe-perdu?token={user_reset_password_token}'

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
