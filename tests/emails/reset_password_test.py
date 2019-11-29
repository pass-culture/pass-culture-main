from unittest.mock import patch

from tests.test_utils import create_user
from emails.user_reset_password import make_reset_password_email_data


class MakeResetPasswordEmailDataTest:
    @patch('utils.mailing.ENV', 'testing')
    @patch('utils.mailing.IS_PROD', False)
    @patch('utils.mailing.SUPPORT_EMAIL_ADDRESS', 'john.doe@example.com')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    def test_should_write_email_with_right_data_when_not_production_environment(self, app):
        # Given
        user = create_user(email="johnny.wick@example.com", first_name="Johnny", reset_password_token='ABCDEFG')

        # When
        reset_password_email_data = make_reset_password_email_data(user=user)

        # Then
        assert reset_password_email_data == {
            'FromEmail': 'john.doe@example.com',
            'MJ-TemplateID': 912168,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'prenom_user': 'Johnny',
                    'token': 'ABCDEFG',
                    'env': '-testing'
                }
        }

    @patch('utils.mailing.ENV', 'production')
    @patch('utils.mailing.IS_PROD', True)
    @patch('utils.mailing.SUPPORT_EMAIL_ADDRESS', 'john.doe@example.com')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def test_should_write_email_with_right_data_when_production_environment(self, app):
        # Given
        user = create_user(email="johnny.wick@example.com", first_name="Johnny", reset_password_token='ABCDEFG')

        # When
        reset_password_email_data = make_reset_password_email_data(user=user)

        # Then
        assert reset_password_email_data == {
            'FromEmail': 'john.doe@example.com',
            'MJ-TemplateID': 912168,
            'MJ-TemplateLanguage': True,
            'To': 'johnny.wick@example.com',
            'Vars':
                {
                    'prenom_user': 'Johnny',
                    'token': 'ABCDEFG',
                    'env': ''
                }
        }
