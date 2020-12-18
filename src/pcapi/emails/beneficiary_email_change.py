from pcapi.repository.feature_queries import feature_send_mail_to_users_enabled
from pcapi.settings import DEV_EMAIL_ADDRESS
from pcapi.settings import SUPPORT_EMAIL_ADDRESS


def build_beneficiary_information_email_change_data(beneficiary_email: str, beneficiary_name: str) -> dict:
    return {
        "FromEmail": SUPPORT_EMAIL_ADDRESS,
        "MJ-TemplateID": 2066067,
        "MJ-TemplateLanguage": True,
        "To": beneficiary_email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        "Vars": {
            "beneficiary_name": beneficiary_name,
        },
    }


def build_beneficiary_confirmation_email_change_data(
    beneficiary_name: str, confirmation_link: str, new_email: str
) -> dict:
    return {
        "FromEmail": SUPPORT_EMAIL_ADDRESS,
        "MJ-TemplateID": 2066065,
        "MJ-TemplateLanguage": True,
        "To": new_email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        "Vars": {
            "beneficiary_name": beneficiary_name,
            "confirmation_link": confirmation_link,
        },
    }
