from pcapi.settings import SUPPORT_EMAIL_ADDRESS


def build_beneficiary_information_email_change_data(beneficiary_email: str, beneficiary_name: str) -> dict:
    return {
        "FromEmail": SUPPORT_EMAIL_ADDRESS,
        "MJ-TemplateID": 2066067,
        "MJ-TemplateLanguage": True,
        "To": beneficiary_email,
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
        "To": new_email,
        "Vars": {
            "beneficiary_name": beneficiary_name,
            "confirmation_link": confirmation_link,
        },
    }
