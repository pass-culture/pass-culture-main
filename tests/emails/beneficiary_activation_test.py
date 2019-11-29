from unittest.mock import patch

from tests.test_utils import create_user
from utils.mailing import get_activation_email_data


class GetActivationEmailTest:
    @patch('utils.mailing.IS_PROD', True)
    def test_should_return_dict_when_environment_is_production(self):
        # Given
        user = create_user(first_name='Fabien', email='fabien@example.net', reset_password_token='ABCD123')

        # When
        activation_email_data = get_activation_email_data(user)

        # Then
        assert activation_email_data == {
            'FromEmail': 'support@passculture.app',
            'Mj-TemplateID': 994771,
            'Mj-TemplateLanguage': True,
            'To': 'fabien@example.net',
            'Vars': {
                'prenom_user': 'Fabien',
                'token': 'ABCD123',
                'email': 'fabien@example.net',
                'env': ''
            },
        }

    @patch('utils.mailing.IS_PROD', False)
    def test_should_return_dict_when_environment_is_development(self):
        # Given
        user = create_user(first_name='Fabien', email='fabien@example.net', reset_password_token='ABCD123')

        # When
        activation_email_data = get_activation_email_data(user)

        # Then
        assert activation_email_data['Vars'] == {
            'prenom_user': 'Fabien',
            'token': 'ABCD123',
            'email': 'fabien@example.net',
            'env': '-development'
        }
