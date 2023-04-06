import datetime
import math
import re
from unittest import mock

from dateutil.relativedelta import relativedelta
from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import repository as fraud_repository
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions.models import Permissions
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.factories import DepositGrantFactory
from pcapi.models import db
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.routes.backoffice.serialization import PaginableQuery


pytestmark = pytest.mark.usefixtures("db_session")


def create_bunch_of_accounts():
    underage = users_factories.UnderageBeneficiaryFactory(
        firstName="Gédéon",
        lastName="Groidanlabénoir",
        email="gg@example.net",
        phoneNumber="+33123456789",
        phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
    )
    grant_18 = users_factories.BeneficiaryGrant18Factory(
        firstName="Abdel Yves Akhim",
        lastName="Flaille",
        email="ayaf@example.net",
        phoneNumber="+33756273849",
        phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
    )
    pro = users_factories.ProFactory(  # associated with no offerer
        firstName="Gérard", lastName="Mentor", email="gm@example.com", phoneNumber="+33246813579"
    )
    random = users_factories.UserFactory(
        firstName="Anne", lastName="Algézic", email="aa@example.net", phoneNumber="+33606060606"
    )
    no_address = users_factories.UserFactory(
        firstName="Jean-Luc",
        lastName="Delarue",
        email="jld@example.com",
        phoneNumber="+33234567890",
        city=None,
        address=None,
    )
    # Same first name as random:
    users_factories.UserFactory(
        firstName="Anne", lastName="Autre", email="autre@example.com", phoneNumber="+33780000000"
    )

    # Pro account should not be returned
    pro_user = users_factories.ProFactory(firstName="Gérard", lastName="Flaille", email="pro@example.net")
    offerers_factories.UserOffererFactory(user=pro_user)

    # Beneficiary which is also hired by a pro should be returned
    offerers_factories.UserOffererFactory(user=grant_18)

    return underage, grant_18, pro, random, no_address


def assert_user_equals(found_user, expected_user):
    assert found_user["firstName"] == expected_user.firstName
    assert found_user["lastName"] == expected_user.lastName
    assert found_user["dateOfBirth"] == expected_user.dateOfBirth.isoformat()
    assert found_user["id"] == expected_user.id
    assert found_user["email"] == expected_user.email
    assert found_user["phoneNumber"] == expected_user.phoneNumber
    assert found_user["roles"] == [role.value for role in expected_user.roles]
    assert found_user["isActive"] is expected_user.isActive


class PublicAccountSearchTest:
    def _create_accounts(self, number, first_names=("Mireille", "Robert")):
        for i in range(number):
            users_factories.UserFactory(
                firstName=first_names[i % len(first_names)],
                lastName=f"{i:02}",
            )

    def _check_pagination(self, content, result_items, items_per_page, page=1):
        pages = math.ceil(result_items / items_per_page)
        assert content["pages"] == pages
        assert content["total"] == result_items
        assert content["page"] == page
        assert content["size"] == result_items % items_per_page if (page == pages) else items_per_page

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_id(self, client):
        # given
        underage, _, _, _, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=underage.id),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 1
        assert_user_equals(response.json["data"][0], underage)

    @pytest.mark.parametrize(
        "query,expected_found",
        [
            ("Yves", "Abdel Yves Akhim"),
            ("Abdel Akhim", "Abdel Yves Akhim"),
            ("Gérard", "Gérard"),
            ("Gerard", "Gérard"),
            ("Jean Luc", "Jean-Luc"),
        ],
    )
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_first_name(self, client, query, expected_found):
        # given
        _, _, _, _, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=query),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 1
        assert response.json["data"][0]["firstName"] == expected_found

    @pytest.mark.parametrize("query", ["ALGÉZIC", "Algézic", "Algezic"])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_name(self, client, query):
        # given
        _, _, _, random, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=query),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 1
        assert_user_equals(response.json["data"][0], random)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_order_by_priority(self, client):
        # given
        create_bunch_of_accounts()
        users_factories.BeneficiaryGrant18Factory(firstName="Théo", lastName="Dorant")
        users_factories.BeneficiaryGrant18Factory(firstName="Théodule", lastName="Dorantissime")
        users_factories.BeneficiaryGrant18Factory(firstName="Théos", lastName="Doranta")
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="Théo Dorant"),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 3
        assert response.json["data"][0]["firstName"] == "Théo"
        assert response.json["data"][0]["lastName"] == "Dorant"
        assert response.json["data"][1]["firstName"] == "Théos"
        assert response.json["data"][1]["lastName"] == "Doranta"
        assert response.json["data"][2]["firstName"] == "Théodule"
        assert response.json["data"][2]["lastName"] == "Dorantissime"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_email(self, client):
        # given
        _, _, _, random, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=random.email),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 1
        assert_user_equals(response.json["data"][0], random)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_email_domain(self, client):
        # given
        underage, grant_18, _, random, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="@example.net"),
        )

        # then
        assert response.status_code == 200
        found_users = response.json["data"]
        assert {user["email"] for user in found_users} == {underage.email, grant_18.email, random.email}

    @pytest.mark.parametrize("query", ["+33756273849", "0756273849", "756273849"])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_phone(self, client, query):
        # given
        _, grant_18, _, _, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=query),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 1
        assert_user_equals(response.json["data"][0], grant_18)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_even_with_missing_city_address(self, client):
        # given
        _, _, _, _, no_address = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=no_address.phoneNumber),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 1
        assert_user_equals(response.json["data"][0], no_address)

    @pytest.mark.parametrize("query", ["Abdel Yves Akhim Flaille", "Abdel Flaille", "Flaille Akhim", "Yves Abdel"])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_both_first_name_and_name(self, client, query):
        # given
        _, grant_18, _, _, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=query),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 1
        assert_user_equals(response.json["data"][0], grant_18)

    @pytest.mark.parametrize("query", ["Gédéon Flaille", "Abdal Flaille", "Autre Algézic"])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_names_which_do_not_match(self, client, query):
        # given
        create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=query),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_empty_query(self, client):
        # given
        create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=""),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 0

    @pytest.mark.parametrize("query", ["'", '""', "Ge*", "([{#/="])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_unexpected(self, client, query):
        # given
        create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=query),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_search_public_account_with_percent_is_forbidden(self, client):
        # given
        create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="%terms"),
        )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_young_but_also_pro(self, client):
        # given
        # She has started subscription process, but is also hired by an offerer
        young_and_pro = users_factories.BeneficiaryGrant18Factory(
            firstName="Maud",
            lastName="Zarella",
            email="mz@example.com",
            dateOfBirth=datetime.date.today() - relativedelta(years=16, days=5),
        )
        offerers_factories.UserOffererFactory(user=young_and_pro)
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q=young_and_pro.email),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 1
        assert_user_equals(response.json["data"][0], young_and_pro)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="anything"),
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_as_anonymous(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="anything"),
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_pagination_default(self, client):
        # given
        total_items = 50
        items_per_page = PaginableQuery.__fields__["perPage"].default
        self._create_accounts(total_items)
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="Robert"),
        )

        # then
        assert response.status_code == 200
        content = response.json
        self._check_pagination(content, total_items / 2, items_per_page, 1)
        data = content["data"]
        assert len(data) == content["size"]
        assert all(account["firstName"] == "Robert" for account in data)
        assert [account["lastName"] for account in data] == [f"{i:02}" for i in range(1, 40, 2)]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_pagination_custom_page_size(self, client):
        # given
        total_items = 50
        items_per_page = 10
        self._create_accounts(total_items)
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="Mireille", perPage=items_per_page),
        )

        # then
        assert response.status_code == 200
        content = response.json
        self._check_pagination(content, total_items / 2, items_per_page, 1)
        data = content["data"]
        assert len(data) == content["size"]
        assert all(account["firstName"] == "Mireille" for account in data)
        assert [account["lastName"] for account in data] == [f"{i:02}" for i in range(0, 20, 2)]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_pagination_custom_page_number(self, client):
        # given
        total_items = 50
        items_per_page = PaginableQuery.__fields__["perPage"].default
        page = 2
        self._create_accounts(total_items)
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="Mireille", page=page),
        )

        # then
        assert response.status_code == 200
        content = response.json
        self._check_pagination(content, total_items / 2, items_per_page, page)
        data = content["data"]
        assert len(data) == content["size"]
        assert all(account["firstName"] == "Mireille" for account in data)
        assert [account["lastName"] for account in data] == [f"{i:02}" for i in range(40, 50, 2)]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_pagination_custom_page_number_and_size(self, client):
        # given
        total_items = 50
        items_per_page = 5
        page = 3
        self._create_accounts(total_items)
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="Mireille", page=page, perPage=items_per_page),
        )

        # then
        assert response.status_code == 200
        content = response.json
        self._check_pagination(content, total_items / 2, items_per_page, page)
        data = content["data"]
        assert len(data) == content["size"]
        assert all(account["firstName"] == "Mireille" for account in data)
        assert [account["lastName"] for account in data] == [f"{i:02}" for i in range(20, 30, 2)]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_pagination_ordering(self, client):
        # given
        total_items = 30
        items_per_page = PaginableQuery.__fields__["perPage"].default
        page = 1
        self._create_accounts(total_items, ("Micheline", "Michel"))
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="Michel", sort="firstName,-lastName"),
        )

        # then
        assert response.status_code == 200
        content = response.json
        self._check_pagination(content, total_items, items_per_page, page)
        data = content["data"]
        assert len(data) == content["size"]
        assert all(account["firstName"] == "Michel" for account in data[:15])
        assert [account["lastName"] for account in data[:15]] == [f"{i:02}" for i in range(29, 0, -2)]
        assert all(account["firstName"] == "Micheline" for account in data[15:])
        assert [account["lastName"] for account in data[15:]] == [f"{i:02}" for i in range(28, 19, -2)]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_error_on_bad_sorted_field(self, client):
        # given
        total_items = 30
        self._create_accounts(total_items)
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_public_account", q="Michel", sort="thisFieldDoesNotExist"),
        )

        # then
        assert response.status_code == 400
        content = response.json
        assert "sorting" in content
        assert "thisFieldDoesNotExist" in content["sorting"]


class GetPublicAccountTest:
    @pytest.mark.parametrize(
        "index,expected_roles",
        [(0, ["UNDERAGE_BENEFICIARY"]), (1, ["BENEFICIARY"]), (2, ["PRO"]), (3, [])],
    )
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_public_account(self, client, index, expected_roles):
        # given
        users = create_bunch_of_accounts()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PUBLIC_ACCOUNT])

        user = users[index]

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_public_account", user_id=user.id),
        )

        # then
        assert response.status_code == 200
        assert response.json == {
            "address": user.address,
            "city": user.city,
            "dateOfBirth": user.dateOfBirth.isoformat() if user.dateOfBirth else None,
            "email": user.email,
            "firstName": user.firstName,
            "id": user.id,
            "isActive": True,
            "lastName": user.lastName,
            "phoneNumber": user.phoneNumber,
            "postalCode": user.postalCode,
            "roles": expected_roles,
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_public_account_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_public_account", user_id=user.id),
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_public_account_as_anonymous(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_public_account", user_id=1),
        )

        # then
        assert response.status_code == 403


class UpdatePublicAccountTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_update_public_account(self, client):
        # given
        _, user, _, _, _ = create_bunch_of_accounts()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_public_account", user_id=user.id),
            json={
                "firstName": "Upda",
                "lastName": "Ted",
                "address": "Quai Branly",
                "postalCode": "75007",
                "city": "Paris",
                "idPieceNumber": "ABCDE",
            },
        )

        # then
        assert response.status_code == 200
        assert response.json == {
            "address": user.address,
            "city": user.city,
            "dateOfBirth": user.dateOfBirth.isoformat() if user.dateOfBirth else None,
            "email": user.email,
            "firstName": "Upda",
            "id": user.id,
            "isActive": True,
            "lastName": "Ted",
            "phoneNumber": user.phoneNumber,
            "postalCode": user.postalCode,
            "roles": ["BENEFICIARY"],
        }

        db.session.refresh(user)
        assert user.firstName == "Upda"
        assert user.lastName == "Ted"
        assert user.address == "Quai Branly"
        assert user.postalCode == "75007"
        assert user.city == "Paris"
        assert user.email == "ayaf@example.net"
        assert user.isEmailValidated
        assert user.idPieceNumber == "ABCDE"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_update_public_account_email(self, client):
        # given
        user, _, _, _, _ = create_bunch_of_accounts()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_public_account", user_id=user.id),
            json={"email": "Updated@example.com"},
        )

        # then
        assert response.status_code == 200
        assert response.json == {
            "address": user.address,
            "city": user.city,
            "dateOfBirth": user.dateOfBirth.isoformat() if user.dateOfBirth else None,
            "email": "updated@example.com",
            "firstName": "Gédéon",
            "id": user.id,
            "isActive": True,
            "lastName": "Groidanlabénoir",
            "phoneNumber": "+33123456789",
            "postalCode": user.postalCode,
            "roles": ["UNDERAGE_BENEFICIARY"],
        }

        # check that email has been changed immediately after admin request
        db.session.refresh(user)
        assert user.email == "updated@example.com"
        assert not user.isEmailValidated

        # check that a line has been added in email history
        email_history: list[users_models.UserEmailHistory] = users_models.UserEmailHistory.query.filter(
            users_models.UserEmailHistory.userId == user.id
        ).all()
        assert len(email_history) == 1
        assert email_history[0].eventType == users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST
        assert email_history[0].oldEmail == "gg@example.net"
        assert email_history[0].newEmail == "updated@example.com"

        # check that a new token has been generated
        token: users_models.Token = users_models.Token.query.filter(users_models.Token.userId == user.id).one()
        assert token.type == users_models.TokenType.EMAIL_VALIDATION

        # check that email is sent
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == "updated@example.com"
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.EMAIL_CONFIRMATION.value.__dict__
        assert token.value in mails_testing.outbox[0].sent_data["params"]["CONFIRMATION_LINK"]

        # click on confirmation link to validate new email
        # when
        token_from_link = re.search(
            r"token%3D([^%]*)%", mails_testing.outbox[0].sent_data["params"]["CONFIRMATION_LINK"]
        ).group(1)
        response = client.post(url_for("native_v1.validate_email"), json={"email_validation_token": token_from_link})

        # then
        assert response.status_code == 200
        db.session.refresh(user)
        assert user.email == "updated@example.com"
        assert user.isEmailValidated

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_update_public_account_invalid_email(self, client):
        # given
        user, _, _, _, _ = create_bunch_of_accounts()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_public_account", user_id=user.id),
            json={"email": "updated.example.com"},
        )

        # then
        assert response.status_code == 400
        assert response.json == {"email": ["Le format d'email est incorrect."]}

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_update_public_account_used_email(self, client):
        # given
        user1, user2, _, _, _ = create_bunch_of_accounts()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_public_account", user_id=user1.id),
            json={"email": user2.email},
        )

        # then
        assert response.status_code == 400
        assert response.json == {"email": "L'email est déjà associé à un autre utilisateur"}

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_update_public_account_phone_number(self, client):
        # given
        _, user, _, _, _ = create_bunch_of_accounts()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_public_account", user_id=user.id),
            json={"phoneNumber": "0987654321"},
        )

        # then
        assert response.status_code == 400
        assert response.json == {"phoneNumber": "La modification du numéro de téléphone n'est pas autorisée"}

        db.session.refresh(user)
        assert user.phoneNumber == "+33756273849"  # unchanged
        assert user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_update_public_account_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_public_account", user_id=user.id),
            json={"email": "updated@example.com"},
        )

        # then
        assert response.status_code == 403


class GetBeneficiaryCreditTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_beneficiary_credit(self, client):
        # given
        _, grant_18, _, _, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.READ_PUBLIC_ACCOUNT])

        bookings_factories.BookingFactory(
            user=grant_18,
            stock__offer__product=offers_factories.DigitalProductFactory(),
            amount=12.5,
        )

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_beneficiary_credit", user_id=grant_18.id),
        )

        # then
        assert response.status_code == 200
        assert response.json == {
            "dateCreated": grant_18.deposit.dateCreated.isoformat(),
            "initialCredit": 300.0,
            "remainingCredit": 287.5,
            "remainingDigitalCredit": 87.5,
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_non_beneficiary_credit(self, client):
        # given
        _, _, pro, random, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.READ_PUBLIC_ACCOUNT])

        # when
        responses = [
            client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.get_beneficiary_credit", user_id=user.id),
            )
            for user in (pro, random)
        ]

        # then
        for response in responses:
            assert response.status_code == 200
            assert response.json == {
                "dateCreated": None,
                "initialCredit": 0.0,
                "remainingCredit": 0.0,
                "remainingDigitalCredit": 0.0,
            }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_beneficiary_credit_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_beneficiary_credit", user_id=1),
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_beneficiary_credit_as_anonymous(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_beneficiary_credit", user_id=1),
        )

        # then
        assert response.status_code == 403


class GetUserHistoryTest:
    def _test_user_history(self, client, user) -> dict:
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_user_subscription_history", user_id=user.id),
        )

        # then
        assert response.status_code == 200
        return response.json["subscriptions"]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_user_history_16y_no_subscription(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=16, days=5)
        )

        data = self._test_user_history(client, user)

        assert data == {
            "UNDERAGE": {
                "idCheckHistory": [],
                "subscriptionItems": [
                    {"status": "ok", "type": "email-validation"},
                    {"status": "not-applicable", "type": "phone-validation"},
                    {"status": "not-applicable", "type": "user-profiling"},
                    {"status": "todo", "type": "profile-completion"},
                    {"status": "todo", "type": "identity-check"},
                    {"status": "todo", "type": "honor-statement"},
                ],
            },
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_user_history_18y_no_subscription(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, days=5)
        )

        data = self._test_user_history(client, user)

        assert data == {
            "AGE18": {
                "idCheckHistory": [],
                "subscriptionItems": [
                    {"status": "ok", "type": "email-validation"},
                    {"status": "todo", "type": "phone-validation"},
                    {"status": "not-enabled", "type": "user-profiling"},
                    {"status": "todo", "type": "profile-completion"},
                    {"status": "todo", "type": "identity-check"},
                    {"status": "todo", "type": "honor-statement"},
                ],
            },
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_user_subscription_history_ubble(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, days=5),
            activity=users_models.ActivityEnum.STUDENT.value,
        )
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
            resultContent=fraud_factories.UbbleContentFactory(),
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
        )

        data = self._test_user_history(client, user)

        assert data["AGE18"]["subscriptionItems"] == [
            {"status": "ok", "type": "email-validation"},
            {"status": "ok", "type": "phone-validation"},
            {"status": "not-enabled", "type": "user-profiling"},
            {"status": "ok", "type": "profile-completion"},
            {"status": "todo", "type": "identity-check"},
            {"status": "ok", "type": "honor-statement"},
        ]

        # "idCheckHistory" contains timestamped/random data generated by factories
        # data are not sorted when retrieved from the database making the test flaky
        # therefore we sort the data before comparing
        data["AGE18"]["idCheckHistory"] = sorted(
            data["AGE18"]["idCheckHistory"], key=lambda history: history["dateCreated"]
        )
        assert len(data["AGE18"]["idCheckHistory"]) == 3

        assert data["AGE18"]["idCheckHistory"][0]["type"] == "profile_completion"
        assert data["AGE18"]["idCheckHistory"][0]["dateCreated"]
        assert data["AGE18"]["idCheckHistory"][0]["status"] == "ok"

        assert data["AGE18"]["idCheckHistory"][1]["type"] == "ubble"
        assert data["AGE18"]["idCheckHistory"][1]["dateCreated"]
        assert data["AGE18"]["idCheckHistory"][1]["thirdPartyId"]
        assert data["AGE18"]["idCheckHistory"][1]["status"] == "suspiscious"
        assert data["AGE18"]["idCheckHistory"][1]["reason"] is None
        assert data["AGE18"]["idCheckHistory"][1]["reasonCodes"] == ["id_check_not_supported"]
        assert isinstance(data["AGE18"]["idCheckHistory"][1]["technicalDetails"], dict)

        assert data["AGE18"]["idCheckHistory"][2]["type"] == "honor_statement"
        assert data["AGE18"]["idCheckHistory"][2]["dateCreated"]
        assert data["AGE18"]["idCheckHistory"][2]["status"] == "ok"
        assert data["AGE18"]["idCheckHistory"][2]["reason"] is None
        assert not data["AGE18"]["idCheckHistory"][2]["reasonCodes"]
        assert not data["AGE18"]["idCheckHistory"][2]["technicalDetails"]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_user_subscription_history_dms(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=15, days=5),
            activity=users_models.ActivityEnum.HIGH_SCHOOL_STUDENT.value,
        )

        # 15-17: no phone validation

        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            applicationId=24680,
            beneficiary=user,
            source=users_factories.BeneficiaryImportSources.demarches_simplifiees.value,
            sourceId=13579,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        dms_author = users_factories.UserFactory(email="dms_author@exemple.com")
        users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport=beneficiary_import,
            status=ImportStatus.CREATED,
            author=dms_author,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
            thirdPartyId="24680",
            resultContent=fraud_factories.DMSContentFactory(procedure_number=13579, application_number=24680),
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
        )

        data = self._test_user_history(client, user)

        assert data["UNDERAGE"]["subscriptionItems"] == [
            {"status": "ok", "type": "email-validation"},
            {"status": "not-applicable", "type": "phone-validation"},
            {"status": "not-applicable", "type": "user-profiling"},
            {"status": "ok", "type": "profile-completion"},
            {"status": "ok", "type": "identity-check"},
            {"status": "ok", "type": "honor-statement"},
        ]

        # "idCheckHistory" contains timestamped/random data generated by factories

        underage_history = sorted(data["UNDERAGE"]["idCheckHistory"], key=lambda o: o["type"])
        assert len(underage_history) == 3

        assert underage_history[2]["type"] == "profile_completion"
        assert underage_history[2]["dateCreated"]
        assert underage_history[2]["status"] == "ok"

        assert underage_history[0]["type"] == "dms"
        assert underage_history[0]["dateCreated"]
        assert underage_history[0]["thirdPartyId"] == "24680"
        assert underage_history[0]["status"] == "ok"
        assert underage_history[0]["reason"] is None
        assert underage_history[0]["sourceId"] == "13579"

        assert underage_history[1]["type"] == "honor_statement"
        assert underage_history[1]["dateCreated"]
        assert underage_history[1]["status"] == "ok"
        assert underage_history[1]["reason"] is None
        assert not underage_history[1]["reasonCodes"]
        assert not underage_history[1]["technicalDetails"]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_user_subscription_history_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_user_subscription_history", user_id=1),
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_user_subscription_history_as_anonymous(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_user_subscription_history", user_id=1),
        )

        # then
        assert response.status_code == 403


class PostManualReviewTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_review_ko_application(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.KO
        )
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).first()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role is True

        dms_content = fraud_models.DMSContent(**check.resultContent)
        assert user.firstName == dms_content.first_name
        assert user.lastName == dms_content.last_name
        assert user.idPieceNumber == dms_content.id_piece_number

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).first()
        assert fraud_check.status == check.status

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_review_dms_application(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).first()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role is True
        assert len(user.deposits) == 1

        dms_content = fraud_models.DMSContent(**check.resultContent)
        assert user.firstName == dms_content.first_name
        assert user.lastName == dms_content.last_name
        assert user.idPieceNumber == dms_content.id_piece_number

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_review_educonnect_application(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=15, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).one()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_underage_beneficiary_role
        assert len(user.deposits) == 1

        educonnect_content = fraud_models.EduconnectContent(**check.resultContent)
        assert user.firstName == educonnect_content.get_first_name()
        assert user.lastName == educonnect_content.get_last_name()
        assert user.idPieceNumber == educonnect_content.get_id_piece_number()

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_review_ubble_application(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).one()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role
        assert len(user.deposits) == 1

        ubble_content = fraud_models.ubble_fraud_models.UbbleContent(**check.resultContent)
        assert user.firstName == ubble_content.get_first_name()
        assert user.lastName == ubble_content.get_last_name()
        assert user.idPieceNumber == ubble_content.get_id_piece_number()

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_ko_review_does_not_activate_beneficiary(self, client):
        # given
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.AdminFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "KO", "eligibility": None},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).one_or_none()
        assert review is not None
        assert review.author == reviewer
        assert review.review == fraud_models.FraudReviewStatus.KO
        assert user.has_beneficiary_role is False

        assert fraud_repository.has_admin_ko_review(user) is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_with_unknown_data(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None, "pouet": "coin coin"},
        )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_with_missing_data(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"review": "OK", "eligibility": None},
        )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_without_permission(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_as_anonymous(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_unknown_account(self, client):
        # given
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            # a user with this id should not exist
            url_for("backoffice_blueprint.review_public_account", user_id=15041980),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
        )

        # then
        assert response.status_code == 412

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_ok_already_beneficiary_account(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        DepositGrantFactory(user=user)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
        )

        # then
        assert response.status_code == 412

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_review_with_non_default_eligibility(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": "AGE18"},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).first()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role is True
        assert len(user.deposits) == 1

        dms_content = fraud_models.DMSContent(**check.resultContent)
        assert user.firstName == dms_content.first_name
        assert user.lastName == dms_content.last_name
        assert user.idPieceNumber == dms_content.id_piece_number


class ResendValidationEmailTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email(self, client):
        # given
        user = users_factories.UserFactory(isEmailValidated=False)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=user.id),
        )

        # then
        assert response.status_code == 204

        # check that validation is unchanged
        updated_user: users_models.User = users_models.User.query.get(user.id)
        assert updated_user.isEmailValidated is False

        # check that a new token has been generated
        token: users_models.Token = users_models.Token.query.filter(users_models.Token.userId == user.id).one()
        assert token.type == users_models.TokenType.EMAIL_VALIDATION

        # check that email is sent
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.EMAIL_CONFIRMATION.value.__dict__
        assert token.value in mails_testing.outbox[0].sent_data["params"]["CONFIRMATION_LINK"]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email_already_validated(self, client):
        # given
        pro_user = users_factories.UserFactory(isEmailValidated=True)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=pro_user.id),
        )

        # then
        assert response.status_code == 400
        assert response.json["user_id"] == "L'adresse email est déjà validée"
        assert len(mails_testing.outbox) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email_pro(self, client):
        # given
        pro_user = users_factories.ProFactory(isEmailValidated=False)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=pro_user.id),
        )

        # then
        assert response.status_code == 400
        assert response.json["user_id"] == "Cette action n'est pas supportée pour les utilisateurs admin ou pro"
        assert len(mails_testing.outbox) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email_admin(self, client):
        # given
        admin_user = users_factories.AdminFactory(isEmailValidated=False)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=admin_user.id),
        )

        # then
        assert response.status_code == 400
        assert response.json["user_id"] == "Cette action n'est pas supportée pour les utilisateurs admin ou pro"
        assert len(mails_testing.outbox) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email_without_permission(self, client):
        # given
        user = users_factories.UserFactory(isEmailValidated=False)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.READ_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=user.id),
        )

        # then
        assert response.status_code == 403
        assert len(mails_testing.outbox) == 0


class SendPhoneValidationCodeTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_send_phone_validation_code(self, client):
        # given
        user = users_factories.UserFactory(phoneValidationStatus=None, phoneNumber="+33612345678")
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.send_phone_validation_code", user_id=user.id),
        )

        # then
        assert response.status_code == 204
        phone_validation_codes = users_models.Token.query.filter(
            users_models.Token.user == user,
            users_models.Token.type == users_models.TokenType.PHONE_VALIDATION,
        ).all()
        assert len(phone_validation_codes) == 1
        assert phone_validation_codes[0].expirationDate is None
        assert phone_validation_codes[0].isUsed is False

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_phone_validation_code_sending_ignores_limit(self, client):
        # given
        user = users_factories.UserFactory(phoneValidationStatus=None, phoneNumber="+33612345678")
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        with mock.patch("pcapi.core.fraud.phone_validation.sending_limit.is_SMS_sending_allowed") as limit_mock:
            limit_mock.return_value = False
            response = client.with_explicit_token(auth_token).post(
                url_for("backoffice_blueprint.send_phone_validation_code", user_id=user.id),
            )

        # then
        assert limit_mock.call_count == 0
        assert response.status_code == 204
        phone_validation_codes = users_models.Token.query.filter(
            users_models.Token.user == user,
            users_models.Token.type == users_models.TokenType.PHONE_VALIDATION,
        ).all()
        assert len(phone_validation_codes) == 1
        assert phone_validation_codes[0].expirationDate is None
        assert phone_validation_codes[0].isUsed is False

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_send_phone_validation_code_when_already_validated(self, client):
        # given
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33612345678",
        )
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.send_phone_validation_code", user_id=user.id),
        )

        # then
        assert response.status_code == 400
        assert response.json.get("user_id") == "Le numéro de téléphone est déjà validé"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_send_phone_validation_code_to_duplicated_number(self, client):
        # given
        user = users_factories.UserFactory(phoneValidationStatus=None, phoneNumber="+33612345678")
        users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber=user.phoneNumber,
            roles=[users_models.UserRole.BENEFICIARY],
        )
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.send_phone_validation_code", user_id=user.id),
        )

        # then
        assert response.status_code == 400
        assert response.json.get("user_id") == "Un compte est déjà associé à ce numéro"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_send_phone_validation_code_to_beneficiary(self, client):
        # given
        user = users_factories.BeneficiaryGrant18Factory(isEmailValidated=True, phoneNumber="+33612345678")
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.send_phone_validation_code", user_id=user.id),
        )

        # then
        assert response.status_code == 400
        assert response.json.get("user_id") == "L'utilisateur est déjà bénéficiaire"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_send_phone_validation_code_without_validated_email(self, client):
        # given
        user = users_factories.UserFactory(isEmailValidated=False, phoneNumber="+33612345678")
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.send_phone_validation_code", user_id=user.id),
        )

        # then
        assert response.status_code == 400
        assert response.json.get("user_id") == "L'email de l'utilisateur n'est pas encore validé"


class GetPublicAccountHistoryTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_get_public_account_history(self, client):
        # given
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=50),
        )
        review = fraud_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=users_factories.UserFactory(),
            dateReviewed=datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
            review=fraud_models.FraudReviewStatus.OK,
        )
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.READ_PUBLIC_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_public_history", user_id=user.id),
        )

        # then
        assert response.status_code == 200
        history = response.json.get("history", [])
        assert history
        assert len(history) == 2
        assert history[0] == {
            "action": "revue manuelle",
            "datetime": review.dateReviewed.isoformat(),
            "message": f"revue {review.review.value} par {review.author.full_name}: {review.reason}",
        }
        assert history[1] == {
            "action": "fraud check",
            "datetime": fraud_check.dateCreated.isoformat(),
            "message": (
                f"{fraud_check.type.value}, {fraud_check.eligibilityType.value}, "
                f"{fraud_check.status.value}, [raison inconnue], {fraud_check.reason}"
            ),
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_public_account_history_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(users_factories.UserFactory(), [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_public_history", user_id=user.id),
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_public_account_history_as_anonymous(self, client):
        # given
        user = users_factories.UserFactory()

        # when
        response = client.get(
            url_for("backoffice_blueprint.get_public_history", user_id=user.id),
        )

        # then
        assert response.status_code == 403
