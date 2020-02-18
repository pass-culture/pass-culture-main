from unittest.mock import patch

from repository import repository
from emails.offerer_attachment_validation import retrieve_data_for_offerer_attachment_validation_email
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_user, create_user_offerer


class ProOffererAttachmentValidationEmailTest:
    @clean_database
    @patch('emails.offerer_attachment_validation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.offerer_attachment_validation.feature_send_mail_to_users_enabled', return_value=False)
    @patch('emails.offerer_attachment_validation.format_environment_for_email', return_value='-testing')
    @patch('emails.offerer_attachment_validation.find_user_offerer_email',
           return_value='pro@example.com')
    @patch('emails.offerer_attachment_validation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    def test_email_is_sent_to_dev_at_passculture_when_not_production_environment(self,
                                                                                 feature_send_mail_to_users_enabled,
                                                                                 format_environment_for_email,
                                                                                 find_user_offerer_email,
                                                                                 app):
        # Given
        offerer = create_offerer(name='Le Théâtre SAS')
        pro_user = create_user(email='pro@example.com')
        user_offerer = create_user_offerer(pro_user, offerer)

        repository.save(pro_user, user_offerer)

        # When
        offerer_attachment_validation_email = retrieve_data_for_offerer_attachment_validation_email(user_offerer)

        # Then
        assert offerer_attachment_validation_email == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 778756,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars':
                {
                    'nom_structure': 'Le Théâtre SAS',
                    'env': '-testing'
                }
        }

    @clean_database
    @patch('emails.offerer_attachment_validation.feature_send_mail_to_users_enabled', return_value=True)
    @patch('emails.offerer_attachment_validation.format_environment_for_email', return_value='')
    @patch('emails.offerer_attachment_validation.find_user_offerer_email',
           return_value='pro@example.com')
    @patch('emails.offerer_attachment_validation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    def test_email_is_sent_to_pro_user_when_environment_is_production(self,
                                                                       feature_send_mail_to_users_enabled,
                                                                       format_environment_for_email,
                                                                       find_user_offerer_email,
                                                                       app):
        # Given
        offerer = create_offerer(name='Le Théâtre SAS')
        pro_user = create_user(email='pro@example.com')
        user_offerer = create_user_offerer(pro_user, offerer)

        repository.save(pro_user, user_offerer)

        # When
        offerer_attachment_validation_email = retrieve_data_for_offerer_attachment_validation_email(user_offerer)

        # Then
        assert offerer_attachment_validation_email == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 778756,
            'MJ-TemplateLanguage': True,
            'To': 'pro@example.com',
            'Vars':
                {
                    'nom_structure': 'Le Théâtre SAS',
                    'env': ''
                }
        }

