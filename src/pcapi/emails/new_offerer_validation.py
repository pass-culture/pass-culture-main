from typing import Dict

from pcapi.emails.beneficiary_booking_cancellation import SUPPORT_EMAIL_ADDRESS
from pcapi.models import Offerer
from pcapi.repository.feature_queries import feature_send_mail_to_users_enabled
from pcapi.repository.offerer_queries import find_new_offerer_user_email
from pcapi.utils.mailing import DEV_EMAIL_ADDRESS
from pcapi.utils.mailing import format_environment_for_email


def retrieve_data_for_new_offerer_validation_email(offerer: Offerer) -> Dict:
    recipients = find_new_offerer_user_email(offerer.id)
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
