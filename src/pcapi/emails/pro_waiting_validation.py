from typing import Dict

from pcapi.models import Offerer
from pcapi.models import UserSQLEntity
from pcapi.repository.feature_queries import feature_send_mail_to_users_enabled
from pcapi.utils.mailing import DEV_EMAIL_ADDRESS
from pcapi.utils.mailing import SUPPORT_EMAIL_ADDRESS


def retrieve_data_for_pro_user_waiting_offerer_validation_email(user: UserSQLEntity, offerer: Offerer) -> Dict:
    return {
        "FromEmail": SUPPORT_EMAIL_ADDRESS,
        "MJ-TemplateID": 778329,
        "MJ-TemplateLanguage": True,
        "To": user.email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        "Vars": {"nom_structure": offerer.name},
    }
