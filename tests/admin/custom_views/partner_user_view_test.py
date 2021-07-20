from unittest.mock import patch

from wtforms import Form

from pcapi.admin.custom_views.partner_user_view import PartnerUserView
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User

from tests.conftest import TestClient
from tests.conftest import clean_database


class PartnerUserViewTest:
    def test_should_generate_a_random_password_on_creation(self, app, db_session):
        # given
        user = User()
        user.password = None
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=True)

        # then
        assert user.password is not None

    def test_should_preserve_password_on_edition(self, app, db_session):
        # given
        user = User()
        user.password = "OriginalPassword"
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=False)

        # then
        assert user.password == "OriginalPassword"

    def test_a_partner_should_never_be_a_beneficiary(self, app, db_session):
        # given
        user = User()
        user.add_beneficiary_role()
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=False)

        # then
        assert user.isBeneficiary == False
        assert not user.has_beneficiary_role

    def test_a_partner_should_never_be_an_admin(self, app, db_session):
        # given
        user = User()
        user.add_admin_role()
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=False)

        # then
        assert user.isAdmin == False
        assert not user.has_admin_role

    def test_a_partner_should_not_need_to_fill_cultural_survey(self, app, db_session):
        # given
        user = User()
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=True)

        # then
        assert user.needsToFillCulturalSurvey == False

    def test_a_partner_should_not_need_to_see_beneficiaries_tutorial(self, app, db_session):
        # given
        user = User()
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=True)

        # then
        assert user.hasSeenTutorials == True

    def test_should_create_the_public_name(self, app, db_session):
        # given
        user = User()
        user.firstName = "Ken"
        user.lastName = "Thompson"
        user.publicName = None
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=False)

        # then
        assert user.publicName == "Ken Thompson"

    @clean_database
    @override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES="superadmin@example.com")
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_super_admin_can_suspend_then_unsuspend_partner(self, mocked_validate_csrf_token, app):
        super_admin = users_factories.UserFactory(email="superadmin@example.com", isAdmin=True)
        partner = users_factories.UserFactory(email="partner@example.com")
        client = TestClient(app.test_client()).with_auth(super_admin.email)

        # Super admin suspends partner
        url = f"/pc/back-office/partner_users/suspend?user_id={partner.id}"
        suspend_response = client.post(url, form={"reason": "fraud", "csrf_token": "token"})
        assert suspend_response.status_code == 302
        assert not partner.isActive

        # Super admin unsuspends partner
        url = f"/pc/back-office/partner_users/unsuspend?user_id={partner.id}"
        unsuspend_response = client.post(url, form={"reason": "fraud", "csrf_token": "token"})
        assert unsuspend_response.status_code == 302
        assert partner.isActive

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.mixins.resend_validation_email_mixin.users_api.request_email_confirmation")
    def test_resend_validation_email_to_partner(
        self, mocked_request_email_confirmation, mocked_validate_csrf_token, app
    ):
        admin = users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        partner = users_factories.UserFactory(email="partner@example.com", isEmailValidated=False)
        client = TestClient(app.test_client()).with_auth(admin.email)

        url = f"/pc/back-office/partner_users/resend-validation-email?user_id={partner.id}"
        resend_validation_email_response = client.post(url, form={"csrf_token": "token"})
        assert resend_validation_email_response.status_code == 302
        mocked_request_email_confirmation.assert_called_once_with(partner)
