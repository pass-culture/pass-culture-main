from unittest.mock import patch

from bs4 import BeautifulSoup

from tests.test_utils import create_user
from utils.mailing import make_user_validation_email


class UserValidationEmailsTest:
    def test_make_webapp_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = create_user(email="test@example.com")
        user.generate_validation_token()
        app_origin_url = 'portail-pro'

        # When
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            email = make_user_validation_email(user, app_origin_url, is_webapp=True)

        # Then
        email_html = BeautifulSoup(email['Html-part'], 'html.parser')
        mail_content = email_html.find("div", {"id": 'mail-content'}).text
        assert 'Bonjour {},'.format(user.publicName) in email_html.find("p", {"id": 'mail-greeting'}).text
        assert "Vous venez de créer un compte pass Culture avec votre adresse test@example.com." in mail_content
        assert 'localhost/validate/user/{}'.format(user.validationToken) in \
               email_html.find('a', href=True)['href']
        assert 'Vous pouvez valider votre adresse email en suivant ce lien :' in mail_content
        assert 'localhost/validate/user/{}'.format(user.validationToken) in mail_content
        assert email['To'] == user.email
        assert email['FromName'] == 'pass Culture'
        assert email['Subject'] == 'Validation de votre adresse email pour le pass Culture'
        assert email['FromEmail'] == 'support@passculture.app'

    def test_make_pro_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = create_user(email="test@example.com")
        user.generate_validation_token()
        app_origin_url = 'portail-pro'

        # When
        email = make_user_validation_email(user, app_origin_url, is_webapp=False)
        expected = {
            'FromEmail': 'dev@passculture.app',
            'FromName': 'pass Culture pro',
            'Subject': '[pass Culture pro] Validation de votre adresse email pour le pass Culture',
            'MJ-TemplateID': 778688,
            'MJ-TemplateLanguage': True,
            'Recipients': [
                {
                    'Email': 'test@example.com',
                    'Name': 'John Doe'
                }
            ],
            'Vars':
                {
                    'nom_structure': 'John Doe',
                    'lien_validation_mail': f'{app_origin_url}/inscription/validation/{user.validationToken}'
                }
        }

        # Then
        assert email == expected
