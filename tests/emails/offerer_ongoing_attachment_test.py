from unittest.mock import patch

from pcapi.emails.offerer_ongoing_attachment import retrieve_data_for_offerer_ongoing_attachment_email
from pcapi.repository import repository
from tests.conftest import clean_database
from pcapi.model_creators.generic_creators import create_offerer, create_user, create_user_offerer


class ProOffererAttachmentValidationEmailTest:
    @clean_database
    @patch('pcapi.emails.offerer_ongoing_attachment.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('pcapi.emails.offerer_ongoing_attachment.feature_send_mail_to_users_enabled', return_value=False)
    @patch('pcapi.emails.offerer_ongoing_attachment.format_environment_for_email', return_value='-testing')
    @patch('pcapi.emails.offerer_ongoing_attachment.find_user_offerer_email', return_value='pro@example.com')
    @patch('pcapi.emails.offerer_ongoing_attachment.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    def test_should_return_data_email_with_dev_email_address_when_not_in_production(self,
                                                                                    feature_send_mail_to_users_enabled,
                                                                                    format_environment_for_email,
                                                                                    find_user_offerer_email,
                                                                                    app):
        # Given
        offerer = create_offerer(name='Le Théâtre SAS')
        pro_user = create_user()
        user_offerer = create_user_offerer(pro_user, offerer)

        repository.save(pro_user, user_offerer)

        # When
        offerer_attachment_validation_email = retrieve_data_for_offerer_ongoing_attachment_email(user_offerer)

        # Then
        assert offerer_attachment_validation_email == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 778749,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars':
                {
                    'nom_structure': 'Le Théâtre SAS',
                    'env': '-testing'
                }
        }

    @clean_database
    @patch('pcapi.emails.offerer_ongoing_attachment.feature_send_mail_to_users_enabled', return_value=True)
    @patch('pcapi.emails.offerer_ongoing_attachment.format_environment_for_email', return_value='')
    @patch('pcapi.emails.offerer_ongoing_attachment.find_user_offerer_email',
           return_value='pro@example.com')
    @patch('pcapi.emails.offerer_ongoing_attachment.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    def test_should_return_data_email_with_pro_email_address_when_environment_is_production(self,
                                                                                            feature_send_mail_to_users_enabled,
                                                                                            format_environment_for_email,
                                                                                            find_user_offerer_email,
                                                                                            app):
        # Given
        offerer = create_offerer(name='Le Théâtre SAS')
        pro_user = create_user(email='pro@example.com')
        user_offerer = create_user_offerer(pro_user, offerer)

        repository.save(user_offerer)

        # When
        offerer_attachment_validation_email = retrieve_data_for_offerer_ongoing_attachment_email(user_offerer)

        # Then
        assert offerer_attachment_validation_email == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 778749,
            'MJ-TemplateLanguage': True,
            'To': 'pro@example.com',
            'Vars':
                {
                    'nom_structure': 'Le Théâtre SAS',
                    'env': ''
                }
        }
