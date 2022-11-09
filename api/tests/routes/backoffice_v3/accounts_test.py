from flask import g
from flask import url_for
import pytest

import pcapi.core.fraud.models as fraud_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.notifications.sms import testing as sms_testing
import pcapi.utils.email as email_utils

from .helpers import accounts as accounts_helpers
from .helpers import search as search_helpers
from .helpers import unauthorized as unauthorized_helpers


pytestmark = pytest.mark.usefixtures("db_session")


class SearchPublicAccountsUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.search_public_accounts"


class SearchPublicAccountsAuthorizedTest(search_helpers.SearchHelper):
    endpoint = "backoffice_v3_web.search_public_accounts"

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_search_result_page(self, client, legit_user):  # type: ignore
        url = url_for(self.endpoint, terms=legit_user.email, order_by="", page=1, per_page=20)

        response = client.with_session_auth(legit_user.email).get(url)

        assert response.status_code == 200, f"[{response.status}] {response.location}"
        assert legit_user.email in str(response.data)

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_malformed_query(self, client, legit_user):  # type: ignore
        url = url_for(self.endpoint, terms=legit_user.email, order_by="unknown_field")

        response = client.with_session_auth(legit_user.email).get(url)

        assert response.status_code == 400


class GetPublicAccountTest(accounts_helpers.PageRendersHelper):
    endpoint = "backoffice_v3_web.get_public_account"

    class GetPublicAccountUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.get_public_account"
        endpoint_kwargs = {"user_id": 1}


class EditPublicAccountTest(accounts_helpers.PageRendersHelper):
    endpoint = "backoffice_v3_web.edit_public_account"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.edit_public_account"
        endpoint_kwargs = {"user_id": 1}


class UpdatePublicAccountTest:
    class UnauthorizedTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.update_public_account"
        endpoint_kwargs = {"user_id": 1}
        method = "patch"
        form = {"first_name": "aaaaaaaaaaaaaaaaaaa"}

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_update_field(self, client, legit_user):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()

        new_email = user_to_edit.email + ".UPDATE  "
        expected_new_email = email_utils.sanitize_email(new_email)

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": new_email,
        }

        response = self.update_account(client, legit_user, user_to_edit, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.get_public_account", user_id=user_to_edit.id, _external=True)
        assert response.location == expected_url

        user_to_edit = users_models.User.query.get(user_to_edit.id)
        assert user_to_edit.email == expected_new_email

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_unknown_field(self, client, legit_user):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()
        base_form = {
            "first_name": user_to_edit.firstName,
            "unknown": "field",
        }

        response = self.update_account(client, legit_user, user_to_edit, base_form)
        assert response.status_code == 400

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_email_already_exists(self, client, legit_user):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()
        other_user = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": other_user.email,
        }

        response = self.update_account(client, legit_user, user_to_edit, base_form)
        assert response.status_code == 400

        user_to_edit = users_models.User.query.get(user_to_edit.id)
        assert user_to_edit.email != other_user.email

    def update_account(self, client, legit_user, user_to_edit, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.edit_public_account", user_id=user_to_edit.id)
        client.with_session_auth(legit_user.email).get(edit_url)

        url = url_for("backoffice_v3_web.update_public_account", user_id=user_to_edit.id)

        form["csrf_token"] = g.csrf_token
        return client.with_session_auth(legit_user.email).patch(url, form=form)


class ResendValidationEmailTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.resend_validation_email"
        endpoint_kwargs = {"user_id": 1}

    class MissingCsrfTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.resend_validation_email"
        endpoint_kwargs = {"user_id": 1}

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_resend_validation_email(self, client, legit_user):
        user = users_factories.BeneficiaryGrant18Factory(isEmailValidated=False)
        response = self.send_resend_validation_email_request(client, legit_user, user)

        assert response.status_code == 303
        assert len(mails_testing.outbox) == 1

    @pytest.mark.parametrize("user_factory", [users_factories.AdminFactory, users_factories.ProFactory])
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_no_email_sent_if_admin_pro(self, client, legit_user, user_factory):
        user = user_factory()
        response = self.send_resend_validation_email_request(client, legit_user, user)

        assert response.status_code == 303
        assert not mails_testing.outbox

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_no_email_sent_if_already_validated(self, client, legit_user):
        user = users_factories.BeneficiaryGrant18Factory(isEmailValidated=True)
        response = self.send_resend_validation_email_request(client, legit_user, user)

        assert response.status_code == 303
        assert not mails_testing.outbox

    def send_resend_validation_email_request(self, client, legit_user, user):
        # generate csrf token
        account_detail_url = url_for("backoffice_v3_web.get_public_account", user_id=user.id)
        client.with_session_auth(legit_user.email).get(account_detail_url)

        url = url_for("backoffice_v3_web.resend_validation_email", user_id=user.id)
        form = {"csrf_token": g.csrf_token}

        return client.with_session_auth(legit_user.email).post(url, form=form)


class SendValidationCodeTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.send_validation_code"
        endpoint_kwargs = {"user_id": 1}

    class MissingCsrfTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.send_validation_code"
        endpoint_kwargs = {"user_id": 1}

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_send_validation_code(self, client, legit_user):
        user = users_factories.UserFactory(phoneNumber="+33601020304", isEmailValidated=True)
        response = self.send_request(client, legit_user, user)

        assert response.status_code == 303
        assert len(sms_testing.requests) == 1

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_nothing_sent_use_cases(self, client, legit_user):
        other_user = users_factories.BeneficiaryGrant18Factory(
            phoneNumber="+33601020304",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        users = [
            # no phone number
            users_factories.UserFactory(phoneNumber=None),
            # phone number already validated
            users_factories.UserFactory(
                phoneNumber="+33601020304", phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
            ),
            # user is already beneficiary
            users_factories.BeneficiaryGrant18Factory(phoneNumber="+33601020304"),
            # email has not been validated
            users_factories.UserFactory(phoneNumber="+33601020304", isEmailValidated=False),
            # phone number is already used
            users_factories.UserFactory(phoneNumber=other_user.phoneNumber),
        ]

        for idx, user in enumerate(users):
            response = self.send_request(client, legit_user, user)

            assert response.status_code == 303, f"[{idx}] found: {response.status_code}, expected: 303"
            assert not sms_testing.requests, f"[{idx}] {len(sms_testing.requests)} sms sent"

    def send_request(self, client, legit_user, user):
        # generate csrf token
        account_detail_url = url_for("backoffice_v3_web.get_public_account", user_id=user.id)
        client.with_session_auth(legit_user.email).get(account_detail_url)

        url = url_for("backoffice_v3_web.send_validation_code", user_id=user.id)
        form = {"csrf_token": g.csrf_token}

        return client.with_session_auth(legit_user.email).post(url, form=form)


class EditPublicAccountReviewTest(accounts_helpers.PageRendersHelper):
    endpoint = "backoffice_v3_web.edit_public_account_review"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.edit_public_account_review"
        endpoint_kwargs = {"user_id": 1}


class UpdatePublicAccountReviewTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.review_public_account"
        endpoint_kwargs = {"user_id": 1}

    class MissingCsrfTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.review_public_account"
        endpoint_kwargs = {"user_id": 1}

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_add_new_fraud_review_to_account(self, client, legit_user):
        user = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.KO.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.add_new_review(client, legit_user, user, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        user = users_models.User.query.get(user.id)

        assert len(user.deposits) == 1
        assert len(user.beneficiaryFraudReviews) == 1

        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.reason == "test"

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_malformed_form(self, client, legit_user):
        user = users_factories.UserFactory()

        base_form = {
            "status": "invalid",
            "eligibility": "invalid",
            "reason": "test",
        }

        response = self.add_new_review(client, legit_user, user, base_form)
        assert response.status_code == 400

        user = users_models.User.query.get(user.id)
        assert not user.deposits

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_reason_not_compulsory(self, client, legit_user):
        user = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.KO.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
        }

        response = self.add_new_review(client, legit_user, user, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        user = users_models.User.query.get(user.id)

        assert len(user.deposits) == 1
        assert len(user.beneficiaryFraudReviews) == 1

        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.reason == None

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_missing_identity_fraud_check_filled(self, client, legit_user):
        # not a beneficiary, does not have any identity fraud check
        # filled by default.
        user = users_factories.UserFactory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.add_new_review(client, legit_user, user, base_form)
        assert response.status_code == 303

        user = users_models.User.query.get(user.id)
        assert not user.deposits

    def add_new_review(self, client, legit_user, user_to_edit, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.edit_public_account", user_id=user_to_edit.id)
        client.with_session_auth(legit_user.email).get(edit_url)

        url = url_for("backoffice_v3_web.review_public_account", user_id=user_to_edit.id)

        form["csrf_token"] = g.csrf_token
        return client.with_session_auth(legit_user.email).post(url, form=form)
