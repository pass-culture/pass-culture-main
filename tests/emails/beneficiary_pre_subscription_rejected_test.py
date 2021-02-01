from pcapi.emails.beneficiary_pre_subscription_rejected import (
    make_not_eligible_beneficiary_pre_subscription_rejected_data,
)
from pcapi.emails.beneficiary_pre_subscription_rejected import make_duplicate_beneficiary_pre_subscription_rejected_data


def test_make_duplicate_beneficiary_pre_subscription_rejected_data():
    data = make_duplicate_beneficiary_pre_subscription_rejected_data()

    assert data == {
        "Mj-TemplateID": 1530996,
        "Mj-TemplateLanguage": True,
    }


def test_make_not_eligible_beneficiary_pre_subscription_rejected_data():
    data = make_not_eligible_beneficiary_pre_subscription_rejected_data()

    assert data == {
        "Mj-TemplateID": 1619528,
        "Mj-TemplateLanguage": True,
    }
