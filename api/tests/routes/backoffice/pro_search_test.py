from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions.models import Permissions
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


pytestmark = pytest.mark.usefixtures("db_session")


def assert_user_equals(found_user, expected_user):
    assert found_user["resourceType"] == "proUser"
    assert found_user["id"] == expected_user.id
    assert found_user["payload"]["firstName"] == expected_user.firstName
    assert found_user["payload"]["lastName"] == expected_user.lastName
    assert found_user["payload"]["email"] == expected_user.email
    assert found_user["payload"]["phoneNumber"] == expected_user.phoneNumber


class ProSearchTest:
    def _create_accounts(
        self,
        number: int = 12,
        first_names: list[str] = ("Alice", "Bob", "Oscar"),
        last_names: list[str] = ("Martin", "Bernard", "Durand", "Dubois"),
    ) -> None:
        self.pro_accounts = []
        for i in range(number):
            first_name = first_names[i % len(first_names)]
            last_name = last_names[i % len(last_names)]
            user = users_factories.UserFactory(
                firstName=first_name, lastName=last_name, email=f"{first_name.lower()}.{last_name.lower()}@example.com"
            )
            # Associate with two offerers, this helps to check that account is returned only once
            offerers_factories.UserOffererFactory(user=user)
            offerers_factories.UserOffererFactory(user=user)
            self.pro_accounts.append(user)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_by_id(self, client):
        # given
        self._create_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=self.pro_accounts[5].id),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_user_equals(response_list[0], self.pro_accounts[5])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_by_email(self, client):
        # given
        self._create_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=self.pro_accounts[2].email),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_user_equals(response_list[0], self.pro_accounts[2])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_by_last_name(self, client):
        # given
        self._create_accounts()
        user = users_factories.UserFactory(firstName="Admin", lastName="Dubois")
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="Dubois"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 3
        assert {u["payload"]["lastName"] for u in response_list} == {"Dubois"}
        assert {u["payload"]["firstName"] for u in response_list} == {"Alice", "Bob", "Oscar"}

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_by_first_and_last_name(self, client):
        # given
        self._create_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="Alice Dubois"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_user_equals(response_list[0], self.pro_accounts[3])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_empty_query(self, client):
        # given
        self._create_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=""),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 0

    @pytest.mark.parametrize("query", ["'", '""', "%", "*", "([{#/="])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_unexpected(self, client, query):
        # given
        self._create_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=query),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_also_beneficiary(self, client):
        # given
        pro_beneficiary = users_factories.BeneficiaryGrant18Factory(
            firstName="Paul",
            lastName="Ochon",
            email="po@example.net",
            phoneNumber="+33740506070",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        offerers_factories.UserOffererFactory(user=pro_beneficiary)
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=pro_beneficiary.id),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_user_equals(response_list[0], pro_beneficiary)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="anything"),
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_as_anonymous(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="anything"),
        )

        # then
        assert response.status_code == 403
