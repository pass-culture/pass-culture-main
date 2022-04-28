from dataclasses import asdict
from datetime import datetime
from datetime import timedelta
import pytest
from unittest.mock import patch

from flask import url_for

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.testing import override_settings
import pcapi.core.users.constants as users_constants
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User

from tests.conftest import TestClient
from tests.conftest import clean_database


class AdminUserViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_admin_user_creation(self, mocked_validate_csrf_token, client):
        admin_email = "admin@example.com"
        users_factories.AdminFactory(email=admin_email)

        data = dict(
            email="NEW-ADMIN@example.com",
            firstName="Powerfull",
            lastName="Admin",
            departementCode="76",
            postalCode="76001",
        )

        assert User.query.filter_by(email="new-admin@example.com").count() == 0

        response = (
            client.with_session_auth(admin_email)
            .post(url_for('admin_users.create_view'), form=data)
        )

        assert response.status_code == 200

        user_created = User.query.filter_by(email="new-admin@example.com").one()
        assert user_created.firstName == "Powerfull"
        assert user_created.lastName == "Admin"
        assert user_created.publicName == "Powerfull Admin"
        assert user_created.dateOfBirth is None
        assert user_created.departementCode == "76"
        assert user_created.postalCode == "76001"
        assert user_created.has_admin_role is True
        assert not user_created.has_beneficiary_role
        assert user_created.has_admin_role
        assert user_created.hasSeenProTutorials is True
        assert user_created.hasSeenProRgs is True
        assert user_created.needsToFillCulturalSurvey is False

        token = Token.query.filter_by(userId=user_created.id).first()
        assert token.type == TokenType.RESET_PASSWORD
        assert token.expirationDate > datetime.utcnow() + timedelta(hours=20)

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_admin_user_receive_a_reset_password_token(self, mocked_validate_csrf_token, app):
        users_factories.AdminFactory(email="admin@example.com")

        data = dict(
            email="new-admin@example.com",
            firstName="Powerfull",
            lastName="Admin",
            departementCode="76",
            postalCode="76000",
        )

        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/admin_users/new", form=data)

        assert response.status_code == 302

        user_created = User.query.filter_by(email="new-admin@example.com").one()
        assert len(user_created.tokens) == 1
        assert user_created.tokens[0].type == TokenType.RESET_PASSWORD

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["params"] == {
            "EMAIL_VALIDATION_LINK": "http://localhost:3001/creation-de-mot-de-passe/" + user_created.tokens[0].value
        }
        assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.EMAIL_VALIDATION_TO_PRO.value)

    @override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=[])
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_admin_user_creation_is_restricted_in_prod(self, mocked_validate_csrf_token, app, db_session):
        users_factories.AdminFactory(email="user@example.com")

        data = dict(
            email="new-admin@example.com",
            firstName="Powerfull",
            lastName="Admin",
            departementCode="76",
            postalCode="76000",
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/pc/back-office/admin_users/new", form=data)

        assert response.status_code == 302

        filtered_users = User.query.filter_by(email="new-admin@example.com").all()
        assert len(filtered_users) == 0

    @clean_database
    @override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=["superadmin@example.com"])
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_super_admin_can_suspend_then_unsuspend_simple_admin(self, mocked_validate_csrf_token, app):
        super_admin = users_factories.AdminFactory(email="superadmin@example.com")
        admin = users_factories.AdminFactory(email="admin@example.com")
        client = TestClient(app.test_client()).with_session_auth(super_admin.email)

        # Suspend
        url = f"/pc/back-office/admin_users/suspend?user_id={admin.id}"
        suspend_response = client.post(
            url, form={"reason": users_constants.SuspensionReason.FRAUD_SUSPICION.value, "csrf_token": "token"}
        )
        assert suspend_response.status_code == 302
        assert not admin.isActive

        # Unsuspend
        url = f"/pc/back-office/admin_users/unsuspend?user_id={admin.id}"
        unsuspend_response = client.post(
            url, form={"reason": users_constants.SuspensionReason.FRAUD_SUSPICION.value, "csrf_token": "token"}
        )
        assert unsuspend_response.status_code == 302
        assert admin.isActive

    @clean_database
    @override_settings(IS_PROD=True)
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_simple_admin_can_not_suspend_admin(self, mocked_validate_csrf_token, app):
        admin_1 = users_factories.AdminFactory(email="admin1@example.com")
        admin_2 = users_factories.AdminFactory(email="admin2@example.com")
        client = TestClient(app.test_client()).with_session_auth(admin_1.email)

        # admin_1 tries to suspend admin_2 (and fails to)
        url = f"/pc/back-office/admin_users/suspend?user_id={admin_2.id}"
        response = client.post(url, form={"reason": "fraud", "csrf_token": "token"})

        assert response.status_code == 403
        assert admin_2.isActive

    @clean_database
    @override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=["superadmin@example.com"])
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_simple_admin_can_not_unsuspend_simple_admin(self, mocked_validate_csrf_token, app):
        super_admin = users_factories.AdminFactory(email="superadmin@example.com")
        admin_1 = users_factories.AdminFactory(email="admin1@example.com")
        admin_2 = users_factories.AdminFactory(email="admin2@example.com")
        super_admin_client = TestClient(app.test_client()).with_session_auth(super_admin.email)
        admin_1_client = TestClient(app.test_client()).with_session_auth(admin_1.email)

        # super_admin suspends admin_2
        url = f"/pc/back-office/admin_users/suspend?user_id={admin_2.id}"
        suspend_response = super_admin_client.post(
            url, form={"reason": users_constants.SuspensionReason.FRAUD_SUSPICION.value, "csrf_token": "token"}
        )
        assert suspend_response.status_code == 302
        assert not admin_2.isActive

        # admin_1 tries to unsuspend admin_2 (and fails to)
        url = f"/pc/back-office/admin_users/unsuspend?user_id={admin_2.id}"
        unsuspend_response = admin_1_client.post(url, form={"reason": "fraud", "csrf_token": "token"})
        assert unsuspend_response.status_code == 403
        assert not admin_2.isActive
