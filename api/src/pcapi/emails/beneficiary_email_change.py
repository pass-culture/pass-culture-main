def build_beneficiary_information_email_change_data(beneficiary_name: str) -> dict:
    return {
        "MJ-TemplateID": 2066067,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "beneficiary_name": beneficiary_name,
        },
    }


def build_beneficiary_confirmation_email_change_data(beneficiary_name: str, confirmation_link: str) -> dict:
    return {
        "MJ-TemplateID": 2066065,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "beneficiary_name": beneficiary_name,
            "confirmation_link": confirmation_link,
        },
    }
