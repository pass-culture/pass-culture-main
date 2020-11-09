from unittest.mock import patch

from pcapi.emails.beneficiary_pre_subscription_rejected import (
    make_not_eligible_beneficiary_pre_subscription_rejected_data,
)
from pcapi.emails.beneficiary_pre_subscription_rejected import make_duplicate_beneficiary_pre_subscription_rejected_data

from tests.domain_creators.generic_creators import create_domain_beneficiary_pre_subcription


def test_make_duplicate_beneficiary_pre_subscription_rejected_data():
    # Given
    email = "test@example.org"
    beneficiary_pre_subscription = create_domain_beneficiary_pre_subcription(email=email)

    # When
    data = make_duplicate_beneficiary_pre_subscription_rejected_data(beneficiary_pre_subscription)

    # Then
    assert data == {
        'FromEmail': 'support@example.com',
        'Mj-TemplateID': 1530996,
        'Mj-TemplateLanguage': True,
        'To': email,
    }


def test_make_not_eligible_beneficiary_pre_subscription_rejected_data():
    # Given
    email = "test@example.org"
    beneficiary_pre_subscription = create_domain_beneficiary_pre_subcription(email=email)

    # When
    data = make_not_eligible_beneficiary_pre_subscription_rejected_data(beneficiary_pre_subscription)

    # Then
    assert data == {
        'FromEmail': 'support@example.com',
        'Mj-TemplateID': 1619528,
        'Mj-TemplateLanguage': True,
        'To': email,
    }
