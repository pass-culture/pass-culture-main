from typing import Dict

from pcapi import settings


def make_duplicate_beneficiary_pre_subscription_rejected_data(
    beneficiary_email: str,
) -> Dict:
    return {
        "FromEmail": settings.SUPPORT_EMAIL_ADDRESS,
        "Mj-TemplateID": 1530996,
        "Mj-TemplateLanguage": True,
        "To": beneficiary_email,
    }


def make_not_eligible_beneficiary_pre_subscription_rejected_data(
    beneficiary_email: str,
) -> Dict:
    return {
        "FromEmail": settings.SUPPORT_EMAIL_ADDRESS,
        "Mj-TemplateID": 1619528,
        "Mj-TemplateLanguage": True,
        "To": beneficiary_email,
    }
