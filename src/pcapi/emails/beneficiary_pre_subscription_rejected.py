def make_duplicate_beneficiary_pre_subscription_rejected_data() -> dict:
    return {
        "Mj-TemplateID": 1530996,
        "Mj-TemplateLanguage": True,
    }


def make_not_eligible_beneficiary_pre_subscription_rejected_data() -> dict:
    return {
        "Mj-TemplateID": 1619528,
        "Mj-TemplateLanguage": True,
    }


def make_fraud_suspicion_data() -> dict:
    return {
        "Mj-TemplateID": 2905960,
        "Mj-TemplateLanguage": True,
        "Mj-campaign": "dossier-en-analyse",
    }
