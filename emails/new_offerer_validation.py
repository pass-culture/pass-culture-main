from typing import Dict

from emails.beneficiary_booking_cancellation import SUPPORT_EMAIL_ADDRESS
from models import Offerer
from repository.feature_queries import feature_send_mail_to_users_enabled
from repository.offerer_queries import find_offerer_user_email
from utils.mailing import format_environment_for_email, DEV_EMAIL_ADDRESS


def retrieve_data_for_new_offerer_validation_email(offerer: Offerer) -> Dict:
    recipients = find_offerer_user_email(offerer.id)
    pro_user_email = recipients if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS
    environment = format_environment_for_email()

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 778723,
        'MJ-TemplateLanguage': True,
        'To': pro_user_email,
        'Vars': {
            'offerer_name': offerer.name,
            'env': environment,
        },
    }
