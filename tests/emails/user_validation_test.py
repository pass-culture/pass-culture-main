from pcapi import settings
import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_user
from pcapi.utils.mailing import make_admin_user_validation_email
from pcapi.utils.mailing import make_pro_user_validation_email
from pcapi.utils.token import random_token

from tests.conftest import clean_database


class ProValidationEmailsTest:
    def test_make_pro_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = create_user(email="test@example.com")
        user.generate_validation_token()

        # When
        email = make_pro_user_validation_email(user)
        expected = {
            "FromName": "pass Culture pro",
            "Subject": "[pass Culture pro] Validation de votre adresse email pour le pass Culture",
            "MJ-TemplateID": 778688,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "nom_structure": "John Doe",
                "lien_validation_mail": f"{settings.PRO_URL}/inscription/validation/{user.validationToken}",
            },
        }

        # Then
        assert email == expected


class AdminValidationEmailsTest:
    @clean_database
    def test_make_admin_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        reset_token = random_token()
        user = users_factories.UserFactory(email="admin@example.com", isAdmin=True, resetPasswordToken=reset_token)

        # When
        email = make_admin_user_validation_email(user)
        expected = {
            "FromName": "pass Culture admin",
            "Subject": "[pass Culture admin] Validation de votre adresse email pour le pass Culture",
            "MJ-TemplateID": 778688,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "lien_validation_mail": f"{settings.PRO_URL}/creation-de-mot-de-passe/{reset_token}",
            },
        }

        # Then
        assert email == expected
