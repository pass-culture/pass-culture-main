from unittest import mock

from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions.factories import RoleFactory
from pcapi.core.permissions.models import Permission
from pcapi.core.permissions.models import Permissions
from pcapi.core.testing import override_features
from pcapi.core.users import factories as user_factories
from pcapi.repository import repository


pytestmark = pytest.mark.usefixtures("db_session")


def create_bunch_of_accounts():
    underage = user_factories.UnderageBeneficiaryFactory(
        firstName="Gédéon", lastName="Groidanlabénoir", email="gg@example.com", phoneNumber="0123456789"
    )
    grant_18 = user_factories.BeneficiaryGrant18Factory(
        firstName="Abdel Yves Akhim", lastName="Flaille", email="ayaf@example.com", phoneNumber="0516273849"
    )
    pro = user_factories.ProFactory(
        firstName="Gérard", lastName="Mentor", email="gm@example.com", phoneNumber="0246813579"
    )
    random = user_factories.UserFactory(
        firstName="Anne", lastName="Algézic", email="aa@example.com", phoneNumber="0606060606"
    )

    return underage, grant_18, pro, random


def create_search_role():
    permission = Permission.query.filter_by(name=Permissions.SEARCH_PUBLIC_ACCOUNT.name).first()
    role = RoleFactory(name="public search")
    role.permissions.append(permission)
    repository.save(role)

    return role


def create_read_account_role():
    permission = Permission.query.filter_by(name=Permissions.READ_PUBLIC_ACCOUNT.name).first()
    role = RoleFactory(name="read user accounts")
    role.permissions.append(permission)
    repository.save(role)

    return role


class PublicAccountSearchTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_id(self, client):
        # given
        underage, _, _, _ = create_bunch_of_accounts()
        search_role = create_search_role()
        user = user_factories.UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = [search_role.name]
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(
                url_for("backoffice_blueprint.search_public_account", q=underage.id)
            )

        # then
        assert response.status_code == 200
        assert len(response.json["accounts"]) == 1
        found_user = response.json["accounts"][0]
        assert found_user["firstName"] == underage.firstName
        assert found_user["lastName"] == underage.lastName
        assert found_user["dateOfBirth"] == underage.dateOfBirth.isoformat()
        assert found_user["id"] == underage.id
        assert found_user["email"] == underage.email
        assert found_user["phoneNumber"] == underage.phoneNumber
        assert found_user["roles"] == ["UNDERAGE_BENEFICIARY"]
        assert found_user["isActive"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_name(self, client):
        # given
        _, grant_18, _, _ = create_bunch_of_accounts()
        search_role = create_search_role()
        user = user_factories.UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = [search_role.name]
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(
                url_for("backoffice_blueprint.search_public_account", q=grant_18.firstName)
            )

        # then
        assert response.status_code == 200
        assert len(response.json["accounts"]) == 1
        found_user = response.json["accounts"][0]
        assert found_user["firstName"] == grant_18.firstName
        assert found_user["lastName"] == grant_18.lastName
        assert found_user["dateOfBirth"] == grant_18.dateOfBirth.isoformat()
        assert found_user["id"] == grant_18.id
        assert found_user["email"] == grant_18.email
        assert found_user["phoneNumber"] == grant_18.phoneNumber
        assert found_user["roles"] == ["BENEFICIARY"]
        assert found_user["isActive"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_email(self, client):
        # given
        _, _, _, random = create_bunch_of_accounts()
        search_role = create_search_role()
        user = user_factories.UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = [search_role.name]
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(
                url_for("backoffice_blueprint.search_public_account", q=random.email)
            )

        # then
        assert response.status_code == 200
        assert len(response.json["accounts"]) == 1
        found_user = response.json["accounts"][0]
        assert found_user["firstName"] == random.firstName
        assert found_user["lastName"] == random.lastName
        assert found_user["dateOfBirth"] == random.dateOfBirth.isoformat()
        assert found_user["id"] == random.id
        assert found_user["email"] == random.email
        assert found_user["phoneNumber"] == random.phoneNumber
        assert found_user["roles"] == []
        assert found_user["isActive"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_phone(self, client):
        # given
        _, _, _, random = create_bunch_of_accounts()
        search_role = create_search_role()
        user = user_factories.UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = [search_role.name]
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(
                url_for("backoffice_blueprint.search_public_account", q=random.phoneNumber)
            )

        # then
        assert response.status_code == 200
        assert len(response.json["accounts"]) == 1
        found_user = response.json["accounts"][0]
        assert found_user["firstName"] == random.firstName
        assert found_user["lastName"] == random.lastName
        assert found_user["dateOfBirth"] == random.dateOfBirth.isoformat()
        assert found_user["id"] == random.id
        assert found_user["email"] == random.email
        assert found_user["phoneNumber"] == random.phoneNumber
        assert found_user["roles"] == []
        assert found_user["isActive"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_without_permission(self, client):
        # given
        no_perm_role = RoleFactory(name="no public search")
        user = user_factories.UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = [no_perm_role.name]
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(
                url_for("backoffice_blueprint.search_public_account", q="anything")
            )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_as_anonymous(self, client):
        # given
        create_search_role()

        # when
        response = client.get(url_for("backoffice_blueprint.search_public_account", q="anything"))

        # then
        assert response.status_code == 401


class GetPublicAccountTest:
    @pytest.mark.parametrize(
        "index,expected_roles",
        [(0, ["UNDERAGE_BENEFICIARY"]), (1, ["BENEFICIARY"]), (2, ["PRO"]), (3, [])],
    )
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_public_account(self, client, index, expected_roles):
        # given
        users = create_bunch_of_accounts()
        role = create_read_account_role()
        admin = user_factories.UserFactory()

        user = users[index]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            admin.groups = [role.name]
            current_user_mock.return_value = admin

            # when
            response = client.with_session_auth(admin.email).get(
                url_for("backoffice_blueprint.get_public_account", user_id=user.id)
            )

        # then
        assert response.status_code == 200
        assert response.json == {
            "dateOfBirth": user.dateOfBirth.isoformat() if user.dateOfBirth else None,
            "email": user.email,
            "firstName": user.firstName,
            "id": user.id,
            "isActive": True,
            "lastName": user.lastName,
            "phoneNumber": user.phoneNumber,
            "roles": expected_roles,
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_public_account_without_permission(self, client):
        # given
        no_perm_role = RoleFactory(name="no read user")
        user = user_factories.UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = [no_perm_role.name]
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(
                url_for("backoffice_blueprint.get_public_account", user_id=user.id)
            )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_public_account_as_anonymous(self, client):
        # given
        create_search_role()

        # when
        response = client.get(url_for("backoffice_blueprint.get_public_account", user_id=1))

        # then
        assert response.status_code == 401


class GetBeneficiaryCreditTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_beneficiary_credit(self, client):
        # given
        _, grant_18, _, _ = create_bunch_of_accounts()
        role = create_read_account_role()
        admin = user_factories.UserFactory()

        bookings_factories.IndividualBookingFactory(
            individualBooking__user=grant_18,
            stock__offer__product=offers_factories.DigitalProductFactory(),
            amount=12.5,
        )

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            admin.groups = [role.name]
            current_user_mock.return_value = admin

            # when
            response = client.with_session_auth(admin.email).get(
                url_for("backoffice_blueprint.get_beneficiary_credit", user_id=grant_18.id)
            )

        # then
        assert response.status_code == 200
        assert response.json == {
            "initialCredit": 300.0,
            "remainingCredit": 287.5,
            "remainingDigitalCredit": 87.5,
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_non_beneficiary_credit(self, client):
        # given
        _, _, pro, random = create_bunch_of_accounts()
        role = create_read_account_role()
        admin = user_factories.UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            admin.groups = [role.name]
            current_user_mock.return_value = admin

            # when
            responses = [
                client.with_session_auth(admin.email).get(
                    url_for("backoffice_blueprint.get_beneficiary_credit", user_id=user.id)
                )
                for user in (pro, random)
            ]

        # then
        for response in responses:
            assert response.status_code == 200
            assert response.json == {
                "initialCredit": 0.0,
                "remainingCredit": 0.0,
                "remainingDigitalCredit": 0.0,
            }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_beneficiary_credit_without_permission(self, client):
        # given
        no_perm_role = RoleFactory(name="no read user")
        user = user_factories.UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = [no_perm_role.name]
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(
                url_for("backoffice_blueprint.get_beneficiary_credit", user_id=1)
            )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_beneficiary_credit_as_anonymous(self, client):
        # given
        create_search_role()

        # when
        response = client.get(url_for("backoffice_blueprint.get_beneficiary_credit", user_id=1))

        # then
        assert response.status_code == 401
