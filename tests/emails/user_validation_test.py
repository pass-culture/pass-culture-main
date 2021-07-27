from pcapi import settings
import pcapi.core.users.factories as users_factories
from pcapi.utils.mailing import make_admin_user_validation_email
from pcapi.utils.mailing import make_pro_user_validation_email

from tests.conftest import clean_database


class ProValidationEmailsTest:
    def test_make_pro_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = users_factories.ProFactory.build(publicName="John Doe", email="test@example.com")
        user.generate_validation_token()

        # When
        email = make_pro_user_validation_email(user)
        expected = {
            "FromName": "pass Culture pro",
            "Subject": "[pass Culture pro] Validation de votre adresse email pour le pass Culture",
            "MJ-TemplateID": 1660341,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "lien_validation_mail": f"{settings.PRO_URL}/inscription/validation/{user.validationToken}",
                "nom_structure": "John Doe",
            },
        }

        # Then
        assert email == expected


class AdminValidationEmailsTest:
    @clean_database
    def test_make_admin_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = users_factories.AdminFactory(email="admin@example.com")
        users_factories.ResetPasswordToken(user=user, value="ABCDEF")

        # When
        email = make_admin_user_validation_email(user, user.tokens[0].value)
        expected = {
            "FromName": "pass Culture admin",
            "Subject": "[pass Culture admin] Validation de votre adresse email pour le pass Culture",
            "MJ-TemplateID": 1660341,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "lien_validation_mail": f"{settings.PRO_URL}/creation-de-mot-de-passe/ABCDEF",
            },
        }

        # Then
        assert email == expected
