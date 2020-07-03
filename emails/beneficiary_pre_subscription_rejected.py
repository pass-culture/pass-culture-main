import os
from typing import Dict

from domain.beneficiary_pre_subscription.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription

SUPPORT_EMAIL_ADDRESS = os.environ.get('SUPPORT_EMAIL_ADDRESS')


def make_beneficiary_pre_subscription_rejected_data(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> Dict:
    beneficiary_email = beneficiary_pre_subscription.email

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'Mj-TemplateID': 1530996,
        'Mj-TemplateLanguage': True,
        'To': beneficiary_email,
    }
