from unittest.mock import patch

import pcapi.core.mails.testing as mails_testing
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User

from tests.conftest import TestClient
from tests.conftest import clean_database


class AdminUserViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_admin_user_creation(self, mocked_validate_csrf_token, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)

        data = dict(
            email="new-admin@example.com",
            firstName="Powerfull",
            lastName="Admin",
            departementCode="76",
        )

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/admin_users/new", form=data)

        assert response.status_code == 302

        user_created = User.query.filter_by(email="new-admin@example.com").one()
        assert user_created.firstName == "Powerfull"
        assert user_created.lastName == "Admin"
        assert user_created.publicName == "Powerfull Admin"
        assert user_created.dateOfBirth is None
        assert user_created.departementCode == "76"
        assert user_created.postalCode is None
        assert user_created.isBeneficiary is False
        assert user_created.isAdmin is True
        assert user_created.hasSeenProTutorials is True
        assert user_created.needsToFillCulturalSurvey is False

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_admin_user_receive_a_reset_password_token(self, mocked_validate_csrf_token, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)

        data = dict(
            email="new-admin@example.com",
            firstName="Powerfull",
            lastName="Admin",
            departementCode="76",
        )

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/admin_users/new", form=data)

        assert response.status_code == 302

        user_created = User.query.filter_by(email="new-admin@example.com").one()
        assert user_created.resetPasswordToken is not None

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data == {
            "FromEmail": "support@example.com",
            "FromName": "pass Culture admin",
            "Subject": "[pass Culture admin] Validation de votre adresse email pour le pass Culture",
            "MJ-TemplateID": 1660341,
            "MJ-TemplateLanguage": True,
            "To": "new-admin@example.com",
            "Vars": {
                "lien_validation_mail": "http://localhost:3001/creation-de-mot-de-passe/"
                + user_created.resetPasswordToken,
                "env": "-development",
            },
        }

    @override_settings(IS_PROD=True)
    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES="")
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_admin_user_creation_is_restricted_in_prod(self, mocked_validate_csrf_token, app, db_session):
        users_factories.UserFactory(email="user@example.com", isAdmin=True)

        data = dict(
            email="new-admin@example.com",
            firstName="Powerfull",
            lastName="Admin",
            departementCode="76",
        )

        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.post("/pc/back-office/admin_users/new", form=data)

        assert response.status_code == 302

        filtered_users = User.query.filter_by(email="new-admin@example.com").all()
        assert len(filtered_users) == 0
