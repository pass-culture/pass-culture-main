from typing import Dict

from models import UserSQLEntity
from repository.feature_queries import feature_send_mail_to_users_enabled
from utils.mailing import SUPPORT_EMAIL_ADDRESS, DEV_EMAIL_ADDRESS, format_environment_for_email


def retrieve_data_for_reset_password_user_email(user: UserSQLEntity) -> Dict:
    user_first_name = user.firstName
    user_email = user.email
    user_reset_password_token = user.resetPasswordToken
    env = format_environment_for_email()

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 912168,
        'MJ-TemplateLanguage': True,
        'To': user_email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        'Vars':
            {
                'prenom_user': user_first_name,
                'token': user_reset_password_token,
                'env': env
            }
    }
