from unittest.mock import patch

from tests.domain_creators.generic_creators import \
    create_domain_beneficiary_pre_subcription

from emails.beneficiary_pre_subscription_rejected import \
    make_beneficiary_pre_subscription_rejected_data


@patch('emails.beneficiary_pre_subscription_rejected.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
def test_make_beneficiary_pre_subscription_rejected_data():
    # Given
    email = "test@example.org"
    beneficiary_pre_subscription = create_domain_beneficiary_pre_subcription(email=email)

    # When
    data = make_beneficiary_pre_subscription_rejected_data(beneficiary_pre_subscription)

    # Then
    assert data == {
        'FromEmail': 'support@example.com',
        'Mj-TemplateID': 1530996,
        'Mj-TemplateLanguage': True,
        'To': email,
    }
