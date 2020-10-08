from unittest.mock import patch

from pcapi.emails.pro_reset_password import retrieve_data_for_reset_password_pro_email
from pcapi.repository import repository
from pcapi.model_creators.generic_creators import create_user, create_offerer, create_user_offerer
from tests.conftest import clean_database


class MakeProResetPasswordEmailDataTest:
    @patch('pcapi.emails.pro_reset_password.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('pcapi.emails.pro_reset_password.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('pcapi.emails.pro_reset_password.format_environment_for_email', return_value='-testing')
    @patch('pcapi.emails.pro_reset_password.feature_send_mail_to_users_enabled', return_value=False)
    @patch('pcapi.emails.pro_reset_password.PRO_URL', 'http://example.net')
    @clean_database
    def test_email_is_sent_to_dev_at_passculture_when_not_production_environment(self,
                                                                                 mock_send_mail_enabled,
                                                                                 mock_format_env,
                                                                                 app
                                                                                 ):
        # Given
        pro = create_user(email="pro@example.com", reset_password_token='ABCDEFG')
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro, offerer)

        repository.save(user_offerer)

        # When
        reset_password_email_data = retrieve_data_for_reset_password_pro_email(user=pro)

        # Then
        assert reset_password_email_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 779295,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars':
                {
                    'lien_nouveau_mdp': 'http://example.net/mot-de-passe-perdu?token=ABCDEFG',
                    'env': '-testing'
                }
        }


    @patch('pcapi.emails.pro_reset_password.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('pcapi.emails.pro_reset_password.format_environment_for_email', return_value='')
    @patch('pcapi.emails.pro_reset_password.feature_send_mail_to_users_enabled', return_value=True)
    @patch('pcapi.emails.pro_reset_password.PRO_URL', 'http://example.net')
    @clean_database
    def test_email_is_sent_to_pro_offerer_when_production_environment(self,
                                                                      mock_send_mail_enabled,
                                                                      mock_format_env,
                                                                      app):
        # Given
        pro = create_user(email="pro@example.com", reset_password_token='ABCDEFG')
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro, offerer)

        repository.save(user_offerer)

        # When
        reset_password_email_data = retrieve_data_for_reset_password_pro_email(user=pro)

        # Then
        assert reset_password_email_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 779295,
            'MJ-TemplateLanguage': True,
            'To': 'pro@example.com',
            'Vars':
                {
                    'lien_nouveau_mdp': 'http://example.net/mot-de-passe-perdu?token=ABCDEFG',
                    'env': ''
                }
        }
