from unittest.mock import patch

from emails.new_offerer_validation import retrieve_data_for_new_offerer_validation_email
from tests.test_utils import create_user, create_offerer, create_user_offerer


class MakeNewOffererValidationEmailTest:
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    @patch('emails.new_offerer_validation.format_environment_for_email', return_value='-testing')
    @patch('emails.new_offerer_validation.find_all_emails_of_user_offerers_admins',
           return_value=['admin@example.com'])
    @patch('emails.new_offerer_validation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    def test_email_is_sent_to_dev_at_passculture_when_not_production_environment(self,
                                                                                 feature_send_mail_to_users_enabled,
                                                                                 find_all_emails_of_user_offerers_admins,
                                                                                 format_environment_for_email):
        # Given
        user = create_user(email='admin@example.com')
        offerer = create_offerer(name='Le Théâtre SAS')
        user_offerer = create_user_offerer(user, offerer, is_admin=True)

        # When
        new_offerer_validation_email = retrieve_data_for_new_offerer_validation_email(user_offerer, offerer)

        # Then
        assert new_offerer_validation_email == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 778723,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_structure': 'Le Théâtre SAS',
                    'env': '-testing'
                }
        }

    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    @patch('emails.new_offerer_validation.format_environment_for_email', return_value='')
    @patch('emails.new_offerer_validation.find_all_emails_of_user_offerers_admins',
           return_value=['admin1@example.com', 'admin2@example.com'])
    @patch('emails.new_offerer_validation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    def test_email_is_sent_to_user_offerers_admins_when_environment_is_production(self,
                                                                                  feature_send_mail_to_users_enabled,
                                                                                  find_all_emails_of_user_offerers_admins,
                                                                                  format_environment_for_email):
        # Given
        user = create_user(email='admin@example.com')
        offerer = create_offerer(name='Le Théâtre SAS')
        user_offerer = create_user_offerer(user, offerer, is_admin=True)

        # When
        new_offerer_validation_email = retrieve_data_for_new_offerer_validation_email(user_offerer, offerer)

        # Then
        assert new_offerer_validation_email == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 778723,
            'MJ-TemplateLanguage': True,
            'To': 'admin1@example.com, admin2@example.com',
            'Vars':
                {
                    'nom_structure': 'Le Théâtre SAS',
                    'env': ''
                }
        }
