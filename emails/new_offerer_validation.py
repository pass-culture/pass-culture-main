from typing import Dict

from emails.beneficiary_booking_cancellation import SUPPORT_EMAIL_ADDRESS
from models import UserOfferer, Offerer
from repository.user_queries import find_all_emails_of_user_offerers_admins
from utils.mailing import format_environment_for_email, create_email_recipients


def retrieve_data_for_new_offerer_validation_email(user_offerer: UserOfferer, offerer: Offerer) -> Dict:
    offerer_id = _get_offerer_id(offerer, user_offerer)
    recipients = find_all_emails_of_user_offerers_admins(offerer_id)
    environment = format_environment_for_email()

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 778723,
        'MJ-TemplateLanguage': True,
        'To': create_email_recipients(recipients),
        'Vars': {
            'nom_structure': offerer.name,
            'env': environment,
        },
    }


def _get_offerer_id(offerer: Offerer, user_offerer: UserOfferer) -> int:
    if offerer is None:
        offerer_id = user_offerer.offerer.id
    else:
        offerer_id = offerer.id
    return offerer_id
