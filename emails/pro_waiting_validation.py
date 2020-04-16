from typing import Dict

from models import UserSQLEntity, Offerer
from repository.feature_queries import feature_send_mail_to_users_enabled
from utils.mailing import SUPPORT_EMAIL_ADDRESS, DEV_EMAIL_ADDRESS


def retrieve_data_for_pro_user_waiting_offerer_validation_email(user: UserSQLEntity, offerer: Offerer) -> Dict:
    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 778329,
        'MJ-TemplateLanguage': True,
        'To': user.email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        'Vars': {
            'nom_structure': offerer.name
        },
    }
