from pcapi import settings
from pcapi.model_creators.generic_creators import create_user
from pcapi.utils.mailing import make_pro_user_validation_email


class UserValidationEmailsTest:
    def test_make_pro_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = create_user(email="test@example.com")
        user.generate_validation_token()

        # When
        email = make_pro_user_validation_email(user)
        expected = {
            "FromEmail": "dev@example.com",
            "FromName": "pass Culture pro",
            "Subject": "[pass Culture pro] Validation de votre adresse email pour le pass Culture",
            "MJ-TemplateID": 778688,
            "MJ-TemplateLanguage": True,
            "Recipients": [{"Email": "test@example.com", "Name": "John Doe"}],
            "Vars": {
                "nom_structure": "John Doe",
                "lien_validation_mail": f"{settings.PRO_URL}/inscription/validation/{user.validationToken}",
            },
        }

        # Then
        assert email == expected
