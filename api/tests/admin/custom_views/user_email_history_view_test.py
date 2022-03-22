from flask import url_for
import pytest

from pcapi.core.testing import assert_model_count_delta
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models


@pytest.fixture(name="admin_client", scope="function")
def admin_client_fixture(client):
    users_factories.AdminFactory(email="admin@example.com")
    return client.with_session_auth("admin@example.com")


VALIDATE_EMAIL_PATH = "user_email_history.validate_user_email"
INDEX_PATH = "user_email_history.index_view"
BENEFICIARY_DETAILS_PATH = "support_beneficiary.details_view"


@pytest.mark.usefixtures("db_session")
class UserEmailHistoryViewTest:
    def test_admin_validation(self, admin_client):
        user = users_factories.BeneficiaryGrant18Factory()
        entry = users_factories.EmailUpdateEntryFactory(user=user)

        with assert_model_count_delta(users_models.UserEmailHistory, 1):
            url = url_for(VALIDATE_EMAIL_PATH, entry_id=entry.id)
            response = admin_client.post(url)

            assert response.status_code == 302
            assert response.location == url_for(INDEX_PATH, _external=True)

    @override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=[])
    def test_only_super_admins_can_validate(self, admin_client):
        """
        Test that a regular admin cannot validate a user's new email
        address.

        Note: outside of production env, all admins are super admins.
        """
        user = users_factories.BeneficiaryGrant18Factory()
        entry = users_factories.EmailUpdateEntryFactory(user=user)

        with assert_model_count_delta(users_models.UserEmailHistory, 0):
            url = url_for(VALIDATE_EMAIL_PATH, entry_id=entry.id)
            response = admin_client.post(url)

            assert response.status_code == 302
            assert response.location == url_for(INDEX_PATH, _external=True)

    @pytest.mark.parametrize(
        "validation_factory",
        [
            users_factories.EmailValidationEntryFactory,
            users_factories.EmailAdminValidationEntryFactory,
        ],
    )
    def test_already_validated(self, admin_client, validation_factory):
        user = users_factories.BeneficiaryGrant18Factory()
        update_entry = users_factories.EmailUpdateEntryFactory(user=user)
        validation_factory(user=user)

        with assert_model_count_delta(users_models.UserEmailHistory, 0):
            url = url_for(VALIDATE_EMAIL_PATH, entry_id=update_entry.id)
            response = admin_client.post(url)

            assert response.status_code == 302
            assert response.location == url_for(INDEX_PATH, _external=True)

    def test_next_url(self, admin_client):
        """
        Test that the expected redirect happens when valid query
        parameters are passed.
        """
        user = users_factories.BeneficiaryGrant18Factory()
        entry = users_factories.EmailUpdateEntryFactory(user=user)

        url = url_for(VALIDATE_EMAIL_PATH, entry_id=entry.id, next=BENEFICIARY_DETAILS_PATH, id=user.id)
        response = admin_client.post(url)

        assert response.status_code == 302
        assert response.location == url_for(BENEFICIARY_DETAILS_PATH, id=user.id, _external=True)

    def test_next_url_broken(self, admin_client):
        """
        Test that the default redirect is used when the query parameters
        are not valid.
        """
        user = users_factories.BeneficiaryGrant18Factory()
        entry = users_factories.EmailUpdateEntryFactory(user=user)

        url = url_for(VALIDATE_EMAIL_PATH, entry_id=entry.id, next="nope")
        response = admin_client.post(url)

        assert response.status_code == 302
        assert response.location == url_for(INDEX_PATH, _external=True)
