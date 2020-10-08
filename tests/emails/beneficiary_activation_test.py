from unittest.mock import patch

from emails.beneficiary_activation import get_activation_email_data
from model_creators.generic_creators import create_user


class GetActivationEmailTest:
    @patch('emails.beneficiary_activation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_activation.format_environment_for_email', return_value='')
    def test_should_return_dict_when_environment_is_production(self, mock_format_environment_for_email):
        # Given
        user = create_user(email='fabien+test@example.net', first_name='Fabien', reset_password_token='ABCD123')

        # When
        activation_email_data = get_activation_email_data(user)

        # Then
        assert activation_email_data == {
            'FromEmail': 'support@example.com',
            'Mj-TemplateID': 994771,
            'Mj-TemplateLanguage': True,
            'To': 'fabien+test@example.net',
            'Vars': {
                'prenom_user': 'Fabien',
                'token': 'ABCD123',
                'email': 'fabien%2Btest%40example.net',
                'env': ''
            },
        }

    @patch('emails.beneficiary_activation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_activation.format_environment_for_email', return_value='-development')
    def test_should_return_dict_when_environment_is_development(self, mock_format_environment_for_email):
        # Given
        user = create_user(email='fabien+test@example.net', first_name='Fabien', reset_password_token='ABCD123')

        # When
        activation_email_data = get_activation_email_data(user)

        # Then
        assert activation_email_data['Vars'] == {
            'prenom_user': 'Fabien',
            'token': 'ABCD123',
            'email': 'fabien%2Btest%40example.net',
            'env': '-development'
        }
