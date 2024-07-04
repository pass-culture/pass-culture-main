import datetime
import re
from unittest import mock

from dateutil.relativedelta import relativedelta
from flask import url_for
import pytest
import pytz

from pcapi.core import token as token_utils
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription.models import SubscriptionItemStatus
from pcapi.core.subscription.models import SubscriptionStep
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.models import EligibilityType
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.notifications.sms import testing as sms_testing
from pcapi.repository import repository
from pcapi.routes.backoffice.accounts import forms as account_forms
from pcapi.routes.backoffice.accounts.blueprint import RegistrationStep
from pcapi.routes.backoffice.accounts.blueprint import RegistrationStepStatus
from pcapi.routes.backoffice.accounts.blueprint import TunnelType
from pcapi.routes.backoffice.accounts.blueprint import _get_fraud_reviews_desc
from pcapi.routes.backoffice.accounts.blueprint import _get_id_check_histories_desc
from pcapi.routes.backoffice.accounts.blueprint import _get_progress
from pcapi.routes.backoffice.accounts.blueprint import _get_status
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_for_tunnel
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_age18
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_underage
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_underage_age18
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_unspecified
from pcapi.routes.backoffice.accounts.blueprint import _get_subscription_item_status_by_eligibility
from pcapi.routes.backoffice.accounts.blueprint import _get_tunnel
from pcapi.routes.backoffice.accounts.blueprint import _get_tunnel_type
from pcapi.routes.backoffice.accounts.blueprint import _set_steps_with_active_and_disabled
from pcapi.routes.backoffice.accounts.blueprint import get_eligibility_history
from pcapi.routes.backoffice.accounts.blueprint import get_public_account_history
from pcapi.tasks.serialization import gdpr_tasks
from pcapi.utils import email as email_utils

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers import search as search_helpers
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper
from .helpers.url import assert_response_location


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


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
    pro = users_factories.UserFactory(
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


# TODO (prouzet) tests in which cards are checked
def assert_user_equals(result_card_text: str, expected_user: users_models.User):
    assert f"{expected_user.firstName} {expected_user.lastName} " in result_card_text
    assert f"User ID : {expected_user.id} " in result_card_text
    assert f"Email : {expected_user.email} " in result_card_text
    if birth_date := expected_user.validatedBirthDate or expected_user.dateOfBirth:
        assert f"Date de naissance : {birth_date.strftime('%d/%m/%Y')} " in result_card_text
    if users_models.UserRole.BENEFICIARY in expected_user.roles:
        assert "Pass 18 " in result_card_text
    if users_models.UserRole.UNDERAGE_BENEFICIARY in expected_user.roles:
        assert "Pass 15-17 " in result_card_text
    if not expected_user.isActive:
        assert "Suspendu" in result_card_text
        if expected_user.suspension_reason:
            assert (
                f"Raison de suspension : {users_constants.SUSPENSION_REASON_CHOICES.get(users_constants.SuspensionReason(expected_user.suspension_reason))} le {expected_user.suspension_date.strftime('%d/%m/%Y')}"
                in result_card_text
            )


class SearchPublicAccountsTest(search_helpers.SearchHelper, GetEndpointHelper):
    endpoint = "backoffice_web.public_accounts.search_public_accounts"
    needed_permission = perm_models.Permissions.READ_PUBLIC_ACCOUNT

    # session + current user
    expected_num_queries_when_no_query = 2

    # + results + count
    expected_num_queries = expected_num_queries_when_no_query + 2

    # + results in email history + count
    expected_num_queries_when_old_email_and_single_result = expected_num_queries + 2

    def test_malformed_query(self, authenticated_client, legit_user):
        url = url_for(self.endpoint, q=legit_user.email, per_page="unknown_field")

        with assert_num_queries(self.expected_num_queries_when_no_query):
            response = authenticated_client.get(url)
            assert response.status_code == 400

    @pytest.mark.parametrize("query", ["", " ", "   "])
    def test_empty_query(self, authenticated_client, query):
        with assert_num_queries(self.expected_num_queries_when_no_query):
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 400

    def test_can_search_public_account_by_id(self, authenticated_client):
        underage, _, _, _, _ = create_bunch_of_accounts()
        user_id = underage.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=str(user_id)))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=underage.id,
            q=underage.id,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_public_account_by_multiple_ids(self, authenticated_client):
        searched_user1, _, _, searched_user2, _ = create_bunch_of_accounts()
        search_query = f" {searched_user1.id}, {searched_user2.id}"

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))
            assert response.status_code == 200

        cards_titles = html_parser.extract_cards_titles(response.data)
        assert set(cards_titles) == {searched_user1.full_name, searched_user2.full_name}

    def test_can_search_public_account_by_small_id(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="2"))
            assert response.status_code == 200

        assert b"Attention, la recherche doit contenir au moins 3 lettres." not in response.data

    @pytest.mark.parametrize("query", ["'", '""', "v", "xx"])
    def test_can_search_public_account_by_short_name(self, authenticated_client, query):
        with assert_num_queries(self.expected_num_queries_when_no_query):
            response = authenticated_client.get(url_for(self.endpoint, q="v"))
            assert response.status_code == 400

        assert "Attention, la recherche doit contenir au moins 3 lettres." in html_parser.extract_warnings(
            response.data
        )

    @pytest.mark.parametrize(
        "query,expected_index",
        [
            ("Yves", 1),  # "Abdel Yves Akhim"
            ("Abdel Akhim", 1),  # "Abdel Yves Akhim"
            ("Gérard", 2),  # Gérard
            ("Gerard", 2),  # Gérard
            ("Jean Luc", 4),  # Jean-Luc
        ],
    )
    def test_can_search_public_account_by_first_name(self, authenticated_client, query, expected_index):
        accounts = create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=accounts[expected_index].id,
            q=query,
            search_rank=1,
            total_items=1,
        )

    @pytest.mark.parametrize("query", ["ALGÉZIC", "Algézic", "Algezic"])
    def test_can_search_public_account_by_name(self, authenticated_client, query):
        _, _, _, random, _ = create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=random.id,
            q=query,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_public_account_by_email(self, authenticated_client):
        _, _, _, random, _ = create_bunch_of_accounts()
        email = random.email

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=email))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=random.id,
            q=email,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_public_account_by_email_domain(self, authenticated_client):
        underage, grant_18, _, random, _ = create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="@example.net"))
            assert response.status_code == 200

        cards_titles = html_parser.extract_cards_titles(response.data)
        assert set(cards_titles) == {underage.full_name, grant_18.full_name, random.full_name}

        cards_text = html_parser.extract_cards_text(response.data)
        assert_user_equals(cards_text[0], underage)
        assert_user_equals(cards_text[1], grant_18)
        assert_user_equals(cards_text[2], random)

    @pytest.mark.parametrize("query", ["+33756273849", "0756273849", "756273849"])
    def test_can_search_public_account_by_phone(self, authenticated_client, query):
        _, grant_18, _, _, _ = create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=grant_18.id,
            q=query,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_public_account_even_with_missing_city_address(self, authenticated_client):
        _, _, _, _, no_address = create_bunch_of_accounts()
        phone_number = no_address.phoneNumber

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=phone_number))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=no_address.id,
            q=phone_number,
            search_rank=1,
            total_items=1,
        )

    @pytest.mark.parametrize("query", ["Abdel Yves Akhim Flaille", "Abdel Flaille", "Flaille Akhim", "Yves Abdel"])
    def test_can_search_public_account_by_both_first_name_and_name(self, authenticated_client, query):
        _, grant_18, _, _, _ = create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=grant_18.id,
            q=query,
            search_rank=1,
            total_items=1,
        )

    @pytest.mark.parametrize("query", ["Gédéon Flaille", "Abdal Flaille", "Autre Algézic"])
    def test_can_search_public_account_names_which_do_not_match(self, authenticated_client, query):
        create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 0

    def test_can_search_public_account_empty_query(self, authenticated_client):
        create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries_when_no_query):
            response = authenticated_client.get(url_for(self.endpoint, q=""))
            assert response.status_code == 400

    @pytest.mark.parametrize("query", ["Ge*", "([{#/="])
    def test_can_search_public_account_unexpected(self, authenticated_client, query):
        create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 0

    def test_search_public_account_with_percent_is_forbidden(self, authenticated_client):
        create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries_when_no_query):
            response = authenticated_client.get(url_for(self.endpoint, q="%terms"))
            assert response.status_code == 400

        assert "Le caractère % n'est pas autorisé" in html_parser.extract_warnings(response.data)

    def test_can_search_public_account_young_but_also_pro(self, authenticated_client):
        # She has started subscription process, but is also hired by an offerer
        young_and_pro = users_factories.BeneficiaryGrant18Factory(
            firstName="Maud",
            lastName="Zarella",
            email="mz@example.com",
            dateOfBirth=datetime.date.today() - relativedelta(years=16, days=5),
        )
        offerers_factories.UserOffererFactory(user=young_and_pro)
        email = young_and_pro.email

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=email))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=young_and_pro.id,
            q=email,
            search_rank=1,
            total_items=1,
        )

    def test_search_suspended_public_account_data(self, authenticated_client):
        underage, grant_18, _, _, _ = create_bunch_of_accounts()
        # we must have at least two results so that it does not redirect to details page and we can check cards content
        common_name = "Supended-Family"
        underage.lastName = common_name
        underage.isActive = False
        grant_18.lastName = common_name
        grant_18.isActive = False
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=None,
            user=underage,
            extraData={"reason": users_constants.SuspensionReason.FRAUD_SUSPICION},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=common_name))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2
        assert_user_equals(cards_text[0], underage)
        assert_user_equals(cards_text[1], grant_18)

    def test_search_suspended_unsuspended_twice(self, authenticated_client):
        user = users_factories.UserFactory(isActive=False)
        email = user.email
        now = datetime.datetime.utcnow()
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=now - datetime.timedelta(days=4),
            user=user,
            extraData={"reason": users_constants.SuspensionReason.UPON_USER_REQUEST},
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_UNSUSPENDED,
            actionDate=now - datetime.timedelta(days=3),
            user=user,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=now - datetime.timedelta(days=2),
            user=user,
            extraData={"reason": users_constants.SuspensionReason.UPON_USER_REQUEST},
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_UNSUSPENDED,
            actionDate=now - datetime.timedelta(days=1),
            user=user,
        )

        db.session.flush()

        # Ensure that search result is redirected, no single card result with "4 résultats"
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=email))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=user.id,
            q=email,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_old_email(self, authenticated_client):
        event = users_factories.EmailValidationEntryFactory()
        event.user.email = event.newEmail
        old_email = event.oldEmail

        db.session.flush()

        with assert_num_queries(self.expected_num_queries_when_old_email_and_single_result):
            response = authenticated_client.get(url_for(self.endpoint, q=old_email))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=event.user.id,
            q=old_email,
            search_rank=1,
            total_items=1,
        )

    @pytest.mark.parametrize(
        "search_filter,expected_user",
        [
            (account_forms.AccountSearchFilter.UNDERAGE.name, "underage_user"),
            (account_forms.AccountSearchFilter.BENEFICIARY.name, "beneficiary_user"),
            (account_forms.AccountSearchFilter.PUBLIC.name, "public_user"),
            (account_forms.AccountSearchFilter.SUSPENDED.name, "suspended_user"),
        ],
    )
    def test_search_with_single_filter(
        self, authenticated_client, search_filter, expected_user
    ):  # pylint: disable=possibly-unused-variable
        common_name = "Last-Name"
        underage_user = users_factories.UnderageBeneficiaryFactory(lastName=common_name)
        beneficiary_user = users_factories.BeneficiaryGrant18Factory(lastName=common_name)
        public_user = users_factories.UserFactory(lastName=common_name)
        suspended_user = users_factories.BeneficiaryGrant18Factory(lastName=common_name, isActive=False)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=common_name, filter=search_filter))
            assert response.status_code == 303

        redirected_id = int(re.match(r".*/(\d+)\?.*", response.location).group(1))
        assert redirected_id == locals()[expected_user].id

    def test_search_with_several_filters(self, authenticated_client):
        common_name = "First-Name"
        underage_user = users_factories.UnderageBeneficiaryFactory(firstName=common_name)
        users_factories.BeneficiaryGrant18Factory(firstName=common_name)
        users_factories.UserFactory(firstName=common_name)
        suspended_user = users_factories.BeneficiaryGrant18Factory(firstName=common_name, isActive=False)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q=common_name,
                    filter=[
                        account_forms.AccountSearchFilter.UNDERAGE.name,
                        account_forms.AccountSearchFilter.SUSPENDED.name,
                    ],
                )
            )
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2
        assert_user_equals(cards_text[0], underage_user)
        assert_user_equals(cards_text[1], suspended_user)


class GetPublicAccountTest(GetEndpointHelper):
    endpoint = "backoffice_web.public_accounts.get_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PUBLIC_ACCOUNT

    # session + current user + user data + bookings + Featureflag
    expected_num_queries = 5

    class ReviewButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS
        button_label = "Revue manuelle"

        @property
        def path(self):
            user = users_factories.UserFactory()
            return url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

    class SuspendButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.SUSPEND_USER
        button_label = "Suspendre le compte"

        @property
        def path(self):
            user = users_factories.UserFactory()
            return url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

    class UnsuspendButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.UNSUSPEND_USER
        button_label = "Réactiver le compte"

        @property
        def path(self):
            user = users_factories.UserFactory(isActive=False)
            return url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

    class AnonymizeUserButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.ANONYMIZE_PUBLIC_ACCOUNT
        button_label = "Anonymiser"

        @property
        def path(self):
            user = users_factories.UserFactory()
            return url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

    @pytest.mark.parametrize(
        "index,expected_badge",
        [(0, "Pass 15-17"), (1, "Pass 18"), (3, None)],
    )
    def test_get_public_account(self, authenticated_client, index, expected_badge):
        users = create_bunch_of_accounts()
        user = users[index]

        user_id = user.id
        # expected_num_queries depends on the number of feature flags checked (2 + user + FF)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"User ID : {user.id} " in content
        assert f"Email : {user.email} " in content
        assert f"Tél : {user.phoneNumber} " in content
        if user.dateOfBirth:
            assert f"Date de naissance {user.dateOfBirth.strftime('%d/%m/%Y')}" in content
        assert "Date de naissance déclarée à l'inscription" not in content
        if user.deposit:
            assert (
                f"Crédité le : {user.deposit.dateCreated.astimezone(tz=pytz.timezone('Europe/Paris')).strftime('%d/%m/%Y à %Hh%M')}"
                in content
            )
            assert (
                f"Date d'expiration du crédit : {user.deposit.expirationDate.astimezone(tz=pytz.timezone('Europe/Paris')).strftime('%d/%m/%Y à %Hh%M')}"
                in content
            )
        assert f"Date de création du compte : {user.dateCreated.strftime('%d/%m/%Y')}" in content
        assert (
            f"Date de dernière connexion : {user.lastConnectionDate.strftime('%d/%m/%Y') if user.lastConnectionDate else ''}"
            in content
        )
        assert f"Adresse {user.address} " in content
        assert url_for("backoffice_web.users.redirect_to_brevo_user_page", user_id=user_id).encode() in response.data

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        if expected_badge:
            assert expected_badge in badges
        assert "Suspendu" not in badges

    def test_get_suspended_public_account(self, legit_user, authenticated_client):
        user = users_factories.UserFactory(isActive=False)
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=datetime.datetime(2023, 11, 3, 11, 12),
            user=user,
            authorUser=legit_user,
            extraData={"reason": users_constants.SuspensionReason.FRAUD_HACK},
        )

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Suspendu : Fraude hacking" in badges

        content = html_parser.content_as_text(response.data)
        assert "Date de suspension : 03/11/2023" in content

    def test_get_public_account_with_modified_email(self, authenticated_client):
        _, grant_18, _, _, _ = create_bunch_of_accounts()
        users_factories.EmailUpdateEntryFactory(user=grant_18)
        user_id = grant_18.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)
        assert parsed_html.find("i", class_="pc-email-changed-icon") is not None

    @pytest.mark.parametrize(
        "reasonCodes",
        ([fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER], [fraud_models.FraudReasonCode.DUPLICATE_USER]),
    )
    def test_get_public_account_with_resolved_duplicate(self, authenticated_client, reasonCodes):
        first_name = "Jack"
        last_name = "Sparrow"
        email = "jsparrow@pirate.mail"
        birth_date = datetime.datetime.utcnow() - relativedelta(years=18, days=15)
        id_piece_number = "1234243344533"

        original_user = users_factories.BeneficiaryGrant18Factory(
            firstName=first_name, lastName=last_name, dateOfBirth=birth_date, email=email, idPieceNumber=id_piece_number
        )

        reason = None
        if reasonCodes == [fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER]:
            reason = f"La pièce d'identité n°{id_piece_number} est déjà prise par l'utilisateur {original_user.id}"
        elif reasonCodes == [fraud_models.FraudReasonCode.DUPLICATE_USER]:
            reason = f"Duplicat de l'utilisateur {original_user.id}"

        duplicate_user = users_factories.UserFactory(
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName=first_name,
            lastName=last_name,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=reasonCodes,
            reason=reason,
            resultContent=fraud_factories.UbbleContentFactory(
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date.date().isoformat(),
                id_document_number=id_piece_number,
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        with assert_num_queries(self.expected_num_queries + 1):  # +1 to get duplicate user info
            response = authenticated_client.get(url_for(self.endpoint, user_id=duplicate_user.id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"User ID doublon : {original_user.id}" in content

    def test_get_public_account_birth_dates(self, authenticated_client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, days=15),
            validatedBirthDate=datetime.datetime.utcnow() - relativedelta(years=17, days=15),
        )
        user_id = user.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"Date de naissance {user.validatedBirthDate.strftime('%d/%m/%Y')} " in content
        assert f"Date de naissance déclarée à l'inscription {user.dateOfBirth.strftime('%d/%m/%Y')} " in content

    def test_get_beneficiary_credit(self, authenticated_client):
        _, grant_18, _, _, _ = create_bunch_of_accounts()

        bookings_factories.BookingFactory(
            user=grant_18,
            stock__offer__subcategoryId=subcategories.VOD.id,
            stock__offer__url="http://example.com",
            amount=12.5,
            user__deposit__expirationDate=datetime.datetime(year=2031, month=12, day=31),
        )

        user_id = grant_18.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        # Remaining credit + Title + Initial Credit
        assert "287,50 € Crédit restant 300,00 €" in cards_text
        assert "87,50 € Crédit digital restant 100,00 €" in cards_text

    def test_get_non_beneficiary_credit(self, authenticated_client):
        _, _, _, random, _ = create_bunch_of_accounts()
        user_id = random.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert "Crédit restant" not in html_parser.content_as_text(response.data)

    def test_get_beneficiary_bookings(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()
        b1 = bookings_factories.CancelledBookingFactory(
            user=user, amount=12.5, dateCreated=datetime.date.today() - relativedelta(days=2)
        )
        b2 = bookings_factories.UsedBookingFactory(user=user, amount=20)
        bookings_factories.UsedBookingFactory()

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        bookings = html_parser.extract_table_rows(response.data, parent_class="bookings-tab-pane")
        assert len(bookings) == 2

        assert bookings[0]["Offreur"] == b2.offerer.name
        assert bookings[0]["Nom de l'offre"] == b2.stock.offer.name
        assert bookings[0]["Prix"] == "20,00 €"
        assert bookings[0]["Date de résa"].startswith(datetime.date.today().strftime("Le %d/%m/%Y"))
        assert bookings[0]["État"] == "Le jeune a consommé l'offre"
        assert bookings[0]["Contremarque"] == b2.token

        assert bookings[1]["Offreur"] == b1.offerer.name
        assert bookings[1]["Nom de l'offre"] == b1.stock.offer.name
        assert bookings[1]["Prix"] == "12,50 €"
        assert bookings[1]["Date de résa"].startswith(
            (datetime.date.today() - relativedelta(days=2)).strftime("Le %d/%m/%Y")
        )
        assert bookings[1]["État"] == "L'offre n'a pas eu lieu"
        assert bookings[1]["Contremarque"] == b1.token

        text = html_parser.content_as_text(response.data)
        assert f"Utilisée le : {datetime.date.today().strftime('%d/%m/%Y')}" in text
        assert f"Annulée le : {datetime.date.today().strftime('%d/%m/%Y')}" in text
        assert "Motif d'annulation : Annulée par le bénéficiaire" in text
        assert f"Email du pro : {b1.venue.bookingEmail}" in text  # extra row for bookings[1]
        assert f"Email du pro : {b2.venue.bookingEmail}" in text  # extra row for bookings[0]

    def test_get_beneficiary_bookings_empty(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.UsedBookingFactory()

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert not html_parser.extract_table_rows(response.data, parent_class="bookings-tab-pane")
        assert "Aucune réservation à ce jour" in response.data.decode("utf-8")

    def test_fraud_check_link(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()
        # modifiy the date for clearer tests
        user.beneficiaryFraudChecks[0].dateCreated = datetime.date.today() - datetime.timedelta(days=5)
        old_dms = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=datetime.date.today() - datetime.timedelta(days=2),
        )

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)

        main_dossier_card = str(
            parsed_html.find("div", class_="pc-script-user-accounts-additional-data-main-fraud-check")
        )
        assert (
            f"https://www.demarches-simplifiees.fr/procedures/{old_dms.source_data().procedure_number}/dossiers/{old_dms.thirdPartyId}"
            in main_dossier_card
        )

        new_dms = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=datetime.date.today() - datetime.timedelta(days=1),
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))

        parsed_html = html_parser.get_soup(response.data)
        main_dossier_card = str(
            parsed_html.find("div", class_="pc-script-user-accounts-additional-data-main-fraud-check")
        )
        assert (
            f"https://www.demarches-simplifiees.fr/procedures/{new_dms.source_data().procedure_number}/dossiers/{new_dms.thirdPartyId}"
            in main_dossier_card
        )

    def test_get_public_account_history(self, legit_user, authenticated_client):
        # More than 30 days ago to have deterministic order because "Import ubble" is generated randomly between
        # -30 days and -1 day in BeneficiaryImportStatusFactory
        user = users_factories.BeneficiaryGrant18Factory(
            dateCreated=datetime.datetime.utcnow() - relativedelta(days=40)
        )
        no_date_action = history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=None,
            user=user,
            authorUser=legit_user,
            extraData={"reason": users_constants.SuspensionReason.FRAUD_SUSPICION},
        )
        admin = users_factories.AdminFactory()
        unsuspended = history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_UNSUSPENDED,
            actionDate=datetime.datetime.utcnow() - relativedelta(days=35),
            user=user,
            authorUser=admin,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.INFO_MODIFIED,
            actionDate=datetime.datetime.utcnow() - relativedelta(days=30),
            user=user,
            authorUser=admin,
            comment=None,
            extraData={
                "modified_info": {
                    "firstName": {"new_info": None, "old_info": "François"},
                    "lastName": {"new_info": "Leblanc", "old_info": "Pignon"},
                    "validatedBirthDate": {"new_info": "2000-09-19", "old_info": "2001-04-14"},
                }
            },
        )

        # Here we want to check that it does not crash with None date in the history (legacy action migrated)
        # Force actionDate because it was replaced with default (now) when inserted in database
        no_date_action.actionDate = None
        repository.save(no_date_action)

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert response.status_code == 200
        history_rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(history_rows) == 6

        assert history_rows[0]["Type"] == "Étape de vérification"
        assert history_rows[0]["Date/Heure"].startswith(datetime.date.today().strftime("Le %d/%m/%Y à"))
        assert history_rows[0]["Commentaire"] == "ubble, age-18, ok, [raison inconnue], None"
        assert not history_rows[0]["Auteur"]

        assert history_rows[1]["Type"] == "Import ubble"
        assert history_rows[1]["Date/Heure"].startswith("Le ")
        assert history_rows[1]["Commentaire"].startswith("CREATED")
        assert not history_rows[1]["Auteur"]

        assert history_rows[2]["Type"] == history_models.ActionType.INFO_MODIFIED.value
        assert history_rows[2]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=30)).strftime("Le %d/%m/%Y à ")
        )
        assert history_rows[2]["Commentaire"].startswith("Informations modifiées :")
        assert "Nom : Pignon => Leblanc" in history_rows[2]["Commentaire"]
        assert "Prénom : suppression de : François" in history_rows[2]["Commentaire"]
        assert "Date de naissance : 2001-04-14 => 2000-09-19" in history_rows[2]["Commentaire"]
        assert history_rows[2]["Auteur"] == admin.full_name

        assert history_rows[3]["Type"] == history_models.ActionType.USER_UNSUSPENDED.value
        assert history_rows[3]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=35)).strftime("Le %d/%m/%Y à ")
        )
        assert history_rows[3]["Commentaire"] == unsuspended.comment
        assert history_rows[3]["Auteur"] == admin.full_name

        assert history_rows[4]["Type"] == history_models.ActionType.USER_CREATED.value
        assert history_rows[4]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=40)).strftime("Le %d/%m/%Y à ")
        )
        assert not history_rows[4]["Commentaire"]
        assert history_rows[4]["Auteur"] == user.full_name

        assert history_rows[5]["Type"] == history_models.ActionType.USER_SUSPENDED.value
        assert not history_rows[5]["Date/Heure"]  # Empty date, at the end of the list
        assert history_rows[5]["Commentaire"].startswith("Fraude suspicion")
        assert history_rows[5]["Auteur"] == legit_user.full_name


class UpdatePublicAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.update_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_update_field(self, legit_user, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()
        old_email = user.email

        new_phone_number = "+33836656565"
        new_email = user.email + ".UPDATE  "
        expected_new_email = email_utils.sanitize_email(new_email)
        expected_new_postal_code = "75000"
        expected_city = user.city

        form_data = {
            "first_name": user.firstName,
            "last_name": user.lastName,
            "email": new_email,
            "birth_date": user.birth_date,
            "phone_number": new_phone_number,
            "id_piece_number": user.idPieceNumber,
            "street": user.address,
            "postal_code": expected_new_postal_code,
            "city": expected_city,
            "marketing_email_subscription": "on",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form_data)
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_web.public_accounts.get_public_account", user_id=user.id, active_tab="history", _external=True
        )
        assert response.location == expected_url

        user = users_models.User.query.filter_by(id=user.id).one()
        assert user.email == expected_new_email
        assert user.phoneNumber == new_phone_number
        assert user.idPieceNumber == user.idPieceNumber
        assert user.postalCode == expected_new_postal_code
        assert user.city == expected_city
        assert user.notificationSubscriptions["marketing_email"] is True

        assert len(user.email_history) == 1
        history = user.email_history[0]
        assert history.oldEmail == old_email
        assert history.newEmail == expected_new_email
        assert history.eventType == users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId is None
        assert action.venueId is None
        assert action.extraData["modified_info"] == {
            "phoneNumber": {"new_info": "+33836656565", "old_info": None},
            "postalCode": {"new_info": expected_new_postal_code, "old_info": None},
        }

    def test_update_all_fields(self, legit_user, authenticated_client):
        date_of_birth = datetime.datetime.combine(
            datetime.date.today() - relativedelta(years=18, months=5, days=3), datetime.time.min
        )
        user = users_factories.BeneficiaryGrant18Factory(
            firstName="Edmond",
            lastName="Dantès",
            address="Château d'If",
            postalCode="13007",
            city="Marseille",
            dateOfBirth=date_of_birth,
            email="ed@example.com",
        )

        form_data = {
            "first_name": "Comte ",
            "last_name": "de Monte-Cristo",
            "email": "mc@example.com",
            "birth_date": datetime.date.today() - relativedelta(years=18, months=3, days=5),
            "phone_number": "",
            "id_piece_number": "A123B456C\n",
            "street": "Chemin du Haut des Ormes",
            "postal_code": "78560\t",
            "city": "Port-Marly",
            # implicit "marketing_email_subscription": "",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form_data)
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_web.public_accounts.get_public_account", user_id=user.id, active_tab="history", _external=True
        )
        assert response.location == expected_url

        user = users_models.User.query.filter_by(id=user.id).one()
        assert user.firstName == form_data["first_name"].strip()
        assert user.lastName == form_data["last_name"].strip()
        assert user.email == form_data["email"]
        assert user.dateOfBirth == date_of_birth
        assert user.validatedBirthDate == form_data["birth_date"]
        assert user.idPieceNumber == form_data["id_piece_number"].strip()
        assert user.address == form_data["street"]
        assert user.postalCode == form_data["postal_code"].strip()
        assert user.departementCode == form_data["postal_code"][:2]
        assert user.city == form_data["city"]

        assert len(user.email_history) == 1
        history = user.email_history[0]
        assert history.oldEmail == "ed@example.com"
        assert history.newEmail == "mc@example.com"
        assert history.eventType == users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId is None
        assert action.venueId is None
        assert action.extraData["modified_info"] == {
            "firstName": {"new_info": "Comte", "old_info": "Edmond"},
            "lastName": {"new_info": "de Monte-Cristo", "old_info": "Dantès"},
            "validatedBirthDate": {
                "new_info": form_data["birth_date"].isoformat(),
                "old_info": date_of_birth.date().isoformat(),
            },
            "idPieceNumber": {"new_info": "A123B456C", "old_info": None},
            "address": {"new_info": "Chemin du Haut des Ormes", "old_info": "Château d'If"},
            "postalCode": {"new_info": "78560", "old_info": "13007"},
            "city": {"new_info": "Port-Marly", "old_info": "Marseille"},
            "notificationSubscriptions.marketing_email": {"new_info": False, "old_info": True},
        }

    def test_unknown_field(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()
        base_form = {
            "first_name": user_to_edit.firstName,
            "unknown": "field",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=base_form)
        assert response.status_code == 400

    def test_update_email_triggers_history_token_and_mail(self, authenticated_client):
        user, _, _, _, _ = create_bunch_of_accounts()

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form={"email": "Updated@example.com"})

        assert response.status_code == 303

        # check that email has been changed immediately after admin request
        db.session.refresh(user)
        assert user.email == "updated@example.com"
        assert user.isEmailValidated

        # check email history
        email_history: list[users_models.UserEmailHistory] = users_models.UserEmailHistory.query.filter(
            users_models.UserEmailHistory.userId == user.id
        ).all()
        assert len(email_history) == 1

        assert email_history[0].eventType == users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE
        assert email_history[0].oldEmail == "gg@example.net"
        assert email_history[0].newEmail == "updated@example.com"

    def test_update_invalid_email(self, authenticated_client):
        user, _, _, _, _ = create_bunch_of_accounts()

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form={"email": "updated.example.com"})

        assert response.status_code == 400
        assert "Le formulaire n'est pas valide" in html_parser.extract_alert(response.data)

    def test_email_already_exists(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()
        other_user = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": other_user.email,
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=base_form)
        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "L'email est déjà associé à un autre utilisateur"

        user_to_edit = users_models.User.query.filter_by(id=user_to_edit.id).one()
        assert user_to_edit.email != other_user.email

    def test_invalid_postal_code(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": user_to_edit.email,
            "postal_code": "7500",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=base_form)
        assert response.status_code == 400

    def test_empty_id_piece_number(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": user_to_edit.email,
            "id_piece_number": "",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=base_form)
        assert response.status_code == 303

        user_to_edit = users_models.User.query.filter_by(id=user_to_edit.id).one()
        assert user_to_edit.idPieceNumber is None

    def test_invalid_phone_number(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()
        old_phone_number = user_to_edit.phoneNumber

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": user_to_edit.email,
            "phone_number": "T3L3PH0N3",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=base_form)
        assert response.status_code == 400

        user_to_edit = users_models.User.query.filter_by(id=user_to_edit.id).one()
        assert user_to_edit.phoneNumber == old_phone_number
        assert html_parser.extract_alert(response.data) == "Le numéro de téléphone est invalide"


class ResendValidationEmailTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.resend_validation_email"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_resend_validation_email(self, authenticated_client):
        user = users_factories.UserFactory(isEmailValidated=False)
        response = self.post_to_endpoint(authenticated_client, user_id=user.id)

        assert response.status_code == 303

        # check that validation is unchanged
        updated_user: users_models.User = users_models.User.query.filter_by(id=user.id).one()
        assert updated_user.isEmailValidated is False

        # check that a new token has been generated
        assert token_utils.Token.token_exists(token_utils.TokenType.EMAIL_VALIDATION, user.id)

        # check that email is sent
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.EMAIL_CONFIRMATION.value.__dict__
        assert "token" in mails_testing.outbox[0]["params"]["CONFIRMATION_LINK"]

    @pytest.mark.parametrize("user_factory", [users_factories.AdminFactory, users_factories.ProFactory])
    def test_no_email_sent_if_admin_pro(self, authenticated_client, user_factory):
        user = user_factory()
        response = self.post_to_endpoint(authenticated_client, user_id=user.id)

        assert response.status_code == 303
        assert not mails_testing.outbox

    def test_no_email_sent_if_already_validated(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory(isEmailValidated=True)
        response = self.post_to_endpoint(authenticated_client, user_id=user.id)

        assert response.status_code == 303
        assert not mails_testing.outbox


class ManualPhoneNumberValidationTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.manually_validate_phone_number"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_manual_phone_number_validation(self, authenticated_client):
        user = users_factories.UserFactory(
            phoneValidationStatus=None, phoneNumber="+33601010203", isEmailValidated=True
        )

        token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, users_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
        )
        token_utils.Token.create(
            token_utils.TokenType.PHONE_VALIDATION, users_constants.PHONE_VALIDATION_TOKEN_LIFE_TIME, user.id
        )
        response = self.post_to_endpoint(authenticated_client, user_id=user.id)

        assert user.is_phone_validated is True
        assert response.status_code == 303
        assert history_models.ActionHistory.query.filter(history_models.ActionHistory.user == user).count() == 1
        assert not token_utils.Token.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)
        assert token_utils.Token.token_exists(token_utils.TokenType.RESET_PASSWORD, user.id)


class SendValidationCodeTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.send_validation_code"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_send_validation_code(self, authenticated_client, app):
        user = users_factories.UserFactory(
            phoneValidationStatus=None, phoneNumber="+33601020304", isEmailValidated=True
        )
        response = self.post_to_endpoint(authenticated_client, user_id=user.id)

        assert response.status_code == 303

        assert len(sms_testing.requests) == 1
        assert sms_testing.requests[0]["recipient"] == user.phoneNumber

        assert token_utils.Token.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)
        assert token_utils.SixDigitsToken.get_expiration_date(
            token_utils.TokenType.PHONE_VALIDATION, user.id
        ).timestamp() == pytest.approx(
            (datetime.datetime.utcnow() + users_constants.PHONE_VALIDATION_TOKEN_LIFE_TIME).timestamp(),
            1,
        )

    def test_phone_validation_code_sending_ignores_limit(self, authenticated_client):
        user = users_factories.UserFactory(phoneValidationStatus=None, phoneNumber="+33612345678")

        with mock.patch("pcapi.core.fraud.phone_validation.sending_limit.is_SMS_sending_allowed") as limit_mock:
            limit_mock.return_value = False
            response = self.post_to_endpoint(authenticated_client, user_id=user.id)

        assert limit_mock.call_count == 0
        assert response.status_code == 303
        assert token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_nothing_sent_use_cases(self, authenticated_client):
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
            response = self.post_to_endpoint(authenticated_client, user_id=user.id)

            assert response.status_code == 303, f"[{idx}] found: {response.status_code}, expected: 303"
            assert not sms_testing.requests, f"[{idx}] {len(sms_testing.requests)} sms sent"


class UpdatePublicAccountReviewTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.review_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS

    def test_add_new_fraud_review_to_account(self, authenticated_client, legit_user):
        user = users_factories.UserFactory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.KO.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        user = users_models.User.query.filter_by(id=user.id).one()

        assert len(user.beneficiaryFraudReviews) == 1
        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.author == legit_user
        assert fraud_review.review == fraud_models.FraudReviewStatus.KO
        assert fraud_review.reason == "test"

        assert user.has_beneficiary_role is False

    def test_set_beneficiary_on_underage(self, authenticated_client, legit_user):
        user = users_factories.UnderageBeneficiaryFactory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        user = users_models.User.query.filter_by(id=user.id).one()

        assert len(user.beneficiaryFraudReviews) == 1
        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.author == legit_user
        assert fraud_review.review == fraud_models.FraudReviewStatus.OK
        assert fraud_review.reason == "test"

        assert user.has_beneficiary_role is True

        deposits = (
            finance_models.Deposit.query.filter(finance_models.Deposit.userId == user.id)
            .order_by(finance_models.Deposit.dateCreated)
            .all()
        )

        assert len(deposits) == 2
        assert deposits[0].expirationDate < datetime.datetime.utcnow()
        assert deposits[0].amount < 300
        assert deposits[1].expirationDate > datetime.datetime.utcnow()
        assert deposits[1].amount == 300

    def test_malformed_form(self, authenticated_client):
        user = users_factories.UserFactory()

        base_form = {
            "status": "invalid",
            "eligibility": "invalid",
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        user = users_models.User.query.filter_by(id=user.id).one()
        assert not user.deposits

    def test_reason_not_compulsory(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.KO.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        user = users_models.User.query.filter_by(id=user.id).one()

        assert len(user.deposits) == 1
        assert len(user.beneficiaryFraudReviews) == 1

        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.reason is None

    def test_missing_identity_fraud_check_filled(self, authenticated_client):
        # not a beneficiary, does not have any identity fraud check
        # filled by default.
        user_id = users_factories.UserFactory().id

        base_form = {
            "status": fraud_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=base_form)
        assert response.status_code == 303

        user = users_models.User.query.filter_by(id=user_id).one()
        assert not user.deposits

    def test_accepte_underage_beneficiary_already_beneficiary(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryFactory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.UNDERAGE.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303
        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        user = users_models.User.query.filter_by(id=user.id).one()
        assert len(user.beneficiaryFraudReviews) == 0
        assert user.roles == [users_models.UserRole.BENEFICIARY]

        response = authenticated_client.get(response.location)
        assert (
            "Le compte est déjà bénéficiaire (18+) il ne peut pas aussi être bénéficiaire (15-17)"
            in html_parser.extract_alert(response.data)
        )


class GetPublicAccountHistoryTest:
    def test_history_contains_creation_date(self):
        user = users_factories.UserFactory()

        history = get_public_account_history(user)

        assert len(history) == 1
        assert history[0].actionType == history_models.ActionType.USER_CREATED
        assert history[0].actionDate == user.dateCreated
        assert history[0].authorUser == user

    def test_history_contains_email_changes(self):
        user = users_factories.UserFactory(dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1))
        email_request = users_factories.EmailUpdateEntryFactory(
            user=user, creationDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
        )
        email_confirmation = users_factories.EmailConfirmationEntryFactory(
            user=user, creationDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        )
        email_validation = users_factories.EmailValidationEntryFactory(
            user=user, creationDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        )

        history = get_public_account_history(user)

        assert len(history) >= 2

        assert history[0].actionType == "Validation de changement d'email"
        assert history[0].actionDate == email_validation.creationDate
        assert history[0].comment == f"de {email_validation.oldEmail} à {email_validation.newEmail}"

        assert history[1].actionType == "Confirmation de changement d'email"
        assert history[1].actionDate == email_confirmation.creationDate
        assert history[1].comment == f"de {email_confirmation.oldEmail} à {email_confirmation.newEmail}"

        assert history[2].actionType == "Demande de changement d'email"
        assert history[2].actionDate == email_request.creationDate
        assert history[2].comment == f"de {email_request.oldEmail} à {email_request.newEmail}"

    def test_history_contains_suspensions(self):
        user = users_factories.UserFactory(dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=3))
        author = users_factories.UserFactory()
        suspension_action = history_factories.SuspendedUserActionHistoryFactory(
            user=user,
            authorUser=author,
            actionDate=datetime.datetime.utcnow() - relativedelta(days=2),
            reason=users_constants.SuspensionReason.FRAUD_SUSPICION,
        )
        unsuspension_action = history_factories.UnsuspendedUserActionHistoryFactory(
            user=user,
            authorUser=author,
            actionDate=datetime.datetime.utcnow() - relativedelta(days=1),
        )

        history = get_public_account_history(user)

        assert len(history) >= 2
        assert history[0] == unsuspension_action
        assert history[1] == suspension_action

    def test_history_contains_fraud_checks(self):
        user = users_factories.UserFactory(dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1))
        dms = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
        )
        phone = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
        )
        honor = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
            status=None,
        )

        history = get_public_account_history(user)

        assert len(history) >= 3

        assert history[2].actionType == "Étape de vérification"
        assert history[2].actionDate == dms.dateCreated
        assert (
            history[2].comment
            == f"{dms.type.value}, {dms.eligibilityType.value}, {dms.status.value}, [raison inconnue], {dms.reason}"
        )

        assert history[1].actionType == "Étape de vérification"
        assert history[1].actionDate == phone.dateCreated
        assert (
            history[1].comment
            == f"{phone.type.value}, {phone.eligibilityType.value}, {phone.status.value}, [raison inconnue], {phone.reason}"
        )

        assert history[0].actionType == "Étape de vérification"
        assert history[0].actionDate == honor.dateCreated
        assert (
            history[0].comment
            == f"{honor.type.value}, {honor.eligibilityType.value}, Statut inconnu, [raison inconnue], {honor.reason}"
        )

    def test_history_contains_reviews(self):
        user = users_factories.UserFactory(dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1))
        author_user = users_factories.UserFactory()
        ko = fraud_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=author_user,
            dateReviewed=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
            review=fraud_models.FraudReviewStatus.KO,
            reason="pas glop",
        )
        dms = fraud_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=author_user,
            dateReviewed=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
            review=fraud_models.FraudReviewStatus.REDIRECTED_TO_DMS,
            reason="",
        )

        history = get_public_account_history(user)

        assert len(history) >= 2

        assert history[0].actionType == "Revue manuelle"
        assert history[0].actionDate == ko.dateReviewed
        assert history[0].comment == f"Revue {ko.review.value} : {ko.reason}"
        assert history[0].authorUser == ko.author

        assert history[1].actionType == "Revue manuelle"
        assert history[1].actionDate == dms.dateReviewed
        assert history[1].comment == f"Revue {dms.review.value} : {dms.reason}"
        assert history[0].authorUser == dms.author

    def test_history_contains_imports(self):
        now = datetime.datetime.utcnow()
        user = users_factories.UserFactory(dateCreated=now - datetime.timedelta(days=1))
        author_user = users_factories.UserFactory()
        dms = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            statuses=[
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.DRAFT,
                    date=now - datetime.timedelta(minutes=30),
                    author=author_user,
                    detail="c'est parti",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.ONGOING,
                    date=now - datetime.timedelta(minutes=25),
                    author=author_user,
                    detail="patience",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.REJECTED,
                    date=now - datetime.timedelta(minutes=20),
                    author=author_user,
                    detail="échec",
                ),
            ],
        )
        ubble = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.ubble.value,
            statuses=[
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.DRAFT,
                    date=now - datetime.timedelta(minutes=15),
                    author=author_user,
                    detail="c'est reparti",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.ONGOING,
                    date=now - datetime.timedelta(minutes=10),
                    author=author_user,
                    detail="loading, please wait",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.CREATED,
                    date=now - datetime.timedelta(minutes=5),
                    author=author_user,
                    detail="félicitation",
                ),
            ],
        )

        history = get_public_account_history(user)

        assert len(history) >= 6
        for i, status in enumerate(sorted(dms.statuses, key=lambda s: s.date)):
            assert history[5 - i].actionType == "Import demarches_simplifiees"
            assert history[5 - i].actionDate == status.date
            assert history[5 - i].comment == f"{status.status.value} ({status.detail})"
            assert history[5 - i].authorUser == status.author
        for i, status in enumerate(sorted(ubble.statuses, key=lambda s: s.date)):
            assert history[2 - i].actionType == "Import ubble"
            assert history[2 - i].actionDate == status.date
            assert history[2 - i].comment == f"{status.status.value} ({status.detail})"
            assert history[2 - i].authorUser == status.author

    def test_history_is_sorted_antichronologically(self):
        now = datetime.datetime.utcnow()
        user = users_factories.UserFactory(dateCreated=now - datetime.timedelta(days=1))
        author_user = users_factories.UserFactory()

        users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.ubble.value,
            statuses=[
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.DRAFT,
                    date=now - datetime.timedelta(minutes=45),
                    author=author_user,
                    detail="bonne chance",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.ONGOING,
                    date=now - datetime.timedelta(minutes=40),
                    author=author_user,
                    detail="ça vient",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.REJECTED,
                    date=now - datetime.timedelta(minutes=20),
                    author=author_user,
                    detail="raté",
                ),
            ],
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            dateCreated=now - datetime.timedelta(minutes=35),
        )
        users_factories.EmailUpdateEntryFactory(user=user, creationDate=now - datetime.timedelta(minutes=30))
        users_factories.EmailValidationEntryFactory(user=user, creationDate=now - datetime.timedelta(minutes=15))
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=author_user,
            dateReviewed=now - datetime.timedelta(minutes=5),
            review=fraud_models.FraudReviewStatus.OK,
        )

        history = get_public_account_history(user)

        assert len(history) == 8
        datetimes = [item.actionDate for item in history]
        assert datetimes == sorted(datetimes, reverse=True)


class GetUserRegistrationStepTest(GetEndpointHelper):
    endpoint = "backoffice_web.public_accounts.get_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PUBLIC_ACCOUNT

    # - session
    # - current user
    # - displayed user
    # - user bookings separately
    # - feature flag ENABLE_PHONE_VALIDATION
    expected_num_queries = 5

    @pytest.mark.parametrize(
        "age,id_check_type,expected_items_status_18,expected_id_check_status_18",
        [
            (18, fraud_models.FraudCheckType.EDUCONNECT, SubscriptionItemStatus.TODO, SubscriptionItemStatus.TODO),
            (19, fraud_models.FraudCheckType.EDUCONNECT, SubscriptionItemStatus.VOID, SubscriptionItemStatus.VOID),
            (18, fraud_models.FraudCheckType.UBBLE, SubscriptionItemStatus.TODO, SubscriptionItemStatus.OK),
            (19, fraud_models.FraudCheckType.UBBLE, SubscriptionItemStatus.VOID, SubscriptionItemStatus.VOID),
            (18, fraud_models.FraudCheckType.DMS, SubscriptionItemStatus.TODO, SubscriptionItemStatus.OK),
        ],
    )
    def test_registration_step_underage_ok_age18_void(
        self, authenticated_client, age, id_check_type, expected_items_status_18, expected_id_check_status_18
    ):
        expected_results = [
            ("Validation Email", SubscriptionItemStatus.OK),
            ("Profil Complet", SubscriptionItemStatus.OK),
            ("ID Check", SubscriptionItemStatus.OK),
            ("Attestation sur l'honneur", SubscriptionItemStatus.OK),
            ("Pass 15-17", SubscriptionItemStatus.OK),
            ("Validation N° téléphone", expected_items_status_18),
            ("Profil Complet", expected_items_status_18),
            ("ID Check", expected_id_check_status_18),
            ("Attestation sur l'honneur", expected_items_status_18),
            ("Pass 18", SubscriptionItemStatus.VOID),
        ]
        date_of_birth = datetime.datetime.utcnow() - relativedelta(years=age, months=3)
        user = users_factories.UserFactory(
            dateCreated=date_of_birth + relativedelta(years=17, days=5),
            dateOfBirth=date_of_birth,
            phoneValidationStatus=users_models.PhoneValidationStatusType.UNVALIDATED,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=date_of_birth,
        )
        users_factories.DepositGrantFactory(user=user, amount=30_00, type="GRANT_15_17")
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=id_check_type,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .pc-test-step-status")
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage+age-18"]')
        assert len(step_icon_views) == len(expected_results)
        for i, step_icon in enumerate(step_icon_views):
            expected_text, expected_title = expected_results[i]
            step_title = step_icon.attrs.get("title")
            assert text_views[i].text == expected_text
            assert step_title == expected_title.value

    def test_registration_step_underage_ko_age18_void(self, authenticated_client):
        expected_results = [
            ("Validation Email", SubscriptionItemStatus.OK),
            ("Profil Complet", SubscriptionItemStatus.OK),
            ("ID Check", SubscriptionItemStatus.KO),
            ("Attestation sur l'honneur", SubscriptionItemStatus.VOID),
            ("Pass 15-17", SubscriptionItemStatus.VOID),
            ("Validation N° téléphone", SubscriptionItemStatus.VOID),
            ("Profil Complet", SubscriptionItemStatus.VOID),
            ("ID Check", SubscriptionItemStatus.VOID),
            ("Attestation sur l'honneur", SubscriptionItemStatus.VOID),
            ("Pass 18", SubscriptionItemStatus.VOID),
        ]
        date_of_birth = datetime.datetime(2004, 4, 16)
        user = users_factories.UserFactory(
            dateCreated=datetime.datetime(2022, 2, 21),
            dateOfBirth=date_of_birth,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=date_of_birth,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .pc-test-step-status")
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage+age-18"]')
        assert len(step_icon_views) == len(expected_results)
        for i, step_icon in enumerate(step_icon_views):
            expected_text, expected_title = expected_results[i]
            step_title = step_icon.attrs.get("title")
            assert text_views[i].text == expected_text
            assert step_title == expected_title.value


class RegistrationStepTest:
    @pytest.mark.parametrize(
        "steps,expected_progress",
        [
            (
                [
                    RegistrationStep(
                        step_id=1,
                        description="Test 1",
                        subscription_item_status=SubscriptionItemStatus.SUSPICIOUS.value,
                        icon="bi-test",
                        is_active=True,
                    ),
                    RegistrationStep(
                        step_id=2,
                        description="Test 2",
                        subscription_item_status=SubscriptionItemStatus.VOID.value,
                        icon="bi-test",
                    ),
                ],
                0,
            ),
            (
                [
                    RegistrationStep(
                        step_id=1,
                        description="Test 1",
                        subscription_item_status=SubscriptionItemStatus.OK.value,
                        icon="bi-test",
                    ),
                    RegistrationStep(
                        step_id=2,
                        description="Test 2",
                        subscription_item_status=SubscriptionItemStatus.TODO.value,
                        icon="bi-test",
                        is_active=True,
                    ),
                ],
                100,
            ),
            (
                [
                    RegistrationStep(
                        step_id=1,
                        description="Test 1",
                        subscription_item_status=SubscriptionItemStatus.OK.value,
                        icon="bi-test",
                    ),
                    RegistrationStep(
                        step_id=2,
                        description="Test 2",
                        subscription_item_status=SubscriptionItemStatus.TODO.value,
                        icon="bi-test",
                        is_active=True,
                    ),
                    RegistrationStep(
                        step_id=3,
                        description="Test 3",
                        subscription_item_status=SubscriptionItemStatus.VOID.value,
                        icon="bi-test",
                    ),
                ],
                50,
            ),
        ],
    )
    def test_get_progress(self, steps, expected_progress):
        progress = _get_progress(steps)

        assert progress == expected_progress

    @pytest.mark.parametrize(
        "subscription_item_status,registration_step_status",
        [
            (SubscriptionItemStatus.OK, RegistrationStepStatus.SUCCESS),
            (SubscriptionItemStatus.NOT_APPLICABLE, RegistrationStepStatus.SUCCESS),
            (SubscriptionItemStatus.NOT_ENABLED, RegistrationStepStatus.SUCCESS),
            (SubscriptionItemStatus.SKIPPED, RegistrationStepStatus.SUCCESS),
            (SubscriptionItemStatus.KO, RegistrationStepStatus.ERROR),
            (SubscriptionItemStatus.PENDING, RegistrationStepStatus.WARNING),
            (SubscriptionItemStatus.SUSPICIOUS, RegistrationStepStatus.WARNING),
            (SubscriptionItemStatus.TODO, None),
            (SubscriptionItemStatus.VOID, None),
        ],
    )
    def test_get_status(self, subscription_item_status, registration_step_status):
        assert _get_status(subscription_item_status.value) == registration_step_status

    @pytest.mark.parametrize(
        "dateCreated,dateOfBirth,tunnel_type",
        [
            (
                datetime.datetime.utcnow(),
                None,
                TunnelType.NOT_ELIGIBLE,
            ),
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18 + 1, days=1),
                TunnelType.NOT_ELIGIBLE,
            ),
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                TunnelType.AGE18,
            ),
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1),
                TunnelType.UNDERAGE,
            ),
            (
                datetime.datetime.utcnow() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                TunnelType.UNDERAGE_AGE18,
            ),
        ],
    )
    def test_get_tunnel_type(self, dateCreated, dateOfBirth, tunnel_type):
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, dateCreated=dateCreated
        )

        user.add_beneficiary_role()
        users_factories.DepositGrantFactory(user=user)
        assert _get_tunnel_type(user) is tunnel_type

    @pytest.mark.parametrize(
        "dateCreated,dateOfBirth,age",
        [
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                users_constants.ELIGIBILITY_AGE_18,
            ),
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1),
                users_constants.ACCOUNT_CREATION_MINIMUM_AGE,
            ),
            (
                datetime.datetime.utcnow() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                users_constants.ELIGIBILITY_AGE_18,
            ),
        ],
    )
    def test_get_subscription_item_status_by_eligibility(self, dateCreated, dateOfBirth, age):
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, dateCreated=dateCreated
        )
        user.add_beneficiary_role()

        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        if (
            age == users_constants.ELIGIBILITY_AGE_18
            and users_utils.get_age_at_date(user.birth_date, user.dateCreated) < users_constants.ELIGIBILITY_AGE_18
        ):
            assert len(subscription_item_status[EligibilityType.UNDERAGE.value]) > 0
            assert len(subscription_item_status[EligibilityType.AGE18.value]) > 0
            assert (
                subscription_item_status[EligibilityType.AGE18.value][SubscriptionStep.EMAIL_VALIDATION.value]
                == SubscriptionItemStatus.OK.value
            )
            assert (
                subscription_item_status[EligibilityType.UNDERAGE.value][SubscriptionStep.EMAIL_VALIDATION.value]
                == SubscriptionItemStatus.OK.value
            )
        elif age == users_constants.ELIGIBILITY_AGE_18:
            assert len(subscription_item_status[EligibilityType.UNDERAGE.value]) == 0
            assert len(subscription_item_status[EligibilityType.AGE18.value]) > 0
            assert (
                subscription_item_status[EligibilityType.AGE18.value][SubscriptionStep.EMAIL_VALIDATION.value]
                == SubscriptionItemStatus.OK.value
            )
        else:
            assert len(subscription_item_status[EligibilityType.AGE18.value]) == 0
            assert len(subscription_item_status[EligibilityType.UNDERAGE.value]) > 0
            assert (
                subscription_item_status[EligibilityType.UNDERAGE.value][SubscriptionStep.EMAIL_VALIDATION.value]
                == SubscriptionItemStatus.OK.value
            )

    @pytest.mark.parametrize(
        "item_status_15_17,item_status_18",
        [
            ({SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value}, {}),
            ({}, {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value}),
            (
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
            ),
        ],
    )
    def test_get_steps_tunnel_unspecified(self, item_status_15_17, item_status_18):
        steps = _get_steps_tunnel_unspecified(item_status_15_17, item_status_18)
        assert len(steps) == 2
        for index, step in enumerate(steps):
            assert step.step_id == index + 1

        if item_status_15_17 and item_status_15_17[SubscriptionStep.EMAIL_VALIDATION.value] is not None:
            email_status = item_status_15_17[SubscriptionStep.EMAIL_VALIDATION.value]
        elif item_status_18 and item_status_18[SubscriptionStep.EMAIL_VALIDATION.value] is not None:
            email_status = item_status_18[SubscriptionStep.EMAIL_VALIDATION.value]
        else:
            email_status = SubscriptionItemStatus.PENDING.value

        assert steps[0].description == SubscriptionStep.EMAIL_VALIDATION.value
        assert steps[0].icon == "bi-envelope-fill"
        assert steps[0].subscription_item_status == email_status

        assert steps[1].description == TunnelType.NOT_ELIGIBLE.value
        assert steps[1].icon == "bi-question-circle-fill"
        assert steps[1].subscription_item_status == email_status

    def test_get_id_check_histories_desc(self):
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth)
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
        user.add_beneficiary_role()
        users_factories.DepositGrantFactory(user=user)
        eligibility_history = get_eligibility_history(user)
        id_check_histories = _get_id_check_histories_desc(eligibility_history)

        before_sort_id_check_histories = eligibility_history[EligibilityType.AGE18.value].idCheckHistory
        before_ids = [history.id for history in before_sort_id_check_histories]
        after_ids = [h.id for h in id_check_histories]

        assert before_ids != after_ids
        assert sorted(before_ids, reverse=True) == after_ids

    def test_get_steps_tunnel_age18(self):
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth)
        user.add_beneficiary_role()
        users_factories.DepositGrantFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, eligibilityType=None)
        fraud_factories.BeneficiaryFraudCheckFactory(user=user)
        eligibility_history = get_eligibility_history(user)
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]

        steps = _get_steps_tunnel_age18(user, id_check_histories, item_status_18, fraud_reviews_desc)
        steps_description = [
            SubscriptionStep.EMAIL_VALIDATION.value,
            SubscriptionStep.PHONE_VALIDATION.value,
            SubscriptionStep.PROFILE_COMPLETION.value,
            SubscriptionStep.IDENTITY_CHECK.value,
            SubscriptionStep.HONOR_STATEMENT.value,
            "Pass 18",
        ]
        assert len(steps) == len(steps_description)
        for index, step in enumerate(steps):
            assert step.step_id == index + 1
            assert step.description == steps_description[index]

            if step.description == SubscriptionStep.IDENTITY_CHECK.value:
                assert len(step.fraud_actions_history) == 2

    def test_get_steps_tunnel_underage(self):
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth)
        user.add_beneficiary_role()
        users_factories.DepositGrantFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=None, dateCreated=dateOfBirth + relativedelta(years=15)
        )
        eligibility_history = get_eligibility_history(user)
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]

        steps = _get_steps_tunnel_underage(user, id_check_histories, item_status_15_17, fraud_reviews_desc)
        steps_description = [
            SubscriptionStep.EMAIL_VALIDATION.value,
            SubscriptionStep.PROFILE_COMPLETION.value,
            SubscriptionStep.IDENTITY_CHECK.value,
            SubscriptionStep.HONOR_STATEMENT.value,
            "Pass 15-17",
        ]
        assert len(steps) == len(steps_description)
        for index, step in enumerate(steps):
            assert step.step_id == index + 1
            assert step.description == steps_description[index]

            if step.description == SubscriptionStep.IDENTITY_CHECK.value:
                assert len(step.fraud_actions_history) == 1

    def test_get_steps_tunnel_underage_age18(self):
        now = datetime.datetime.utcnow()
        dateCreated = now - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2)
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, dateCreated=dateCreated
        )
        user.add_beneficiary_role()
        users_factories.DepositGrantFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=None, dateCreated=dateOfBirth + relativedelta(years=15)
        )
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, eligibilityType=None)
        eligibility_history = get_eligibility_history(user)
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]

        steps = _get_steps_tunnel_underage_age18(
            user, id_check_histories, item_status_15_17, item_status_18, fraud_reviews_desc
        )
        steps_description = [
            SubscriptionStep.EMAIL_VALIDATION.value,
            SubscriptionStep.PROFILE_COMPLETION.value,
            SubscriptionStep.IDENTITY_CHECK.value,
            SubscriptionStep.HONOR_STATEMENT.value,
            EligibilityType.UNDERAGE.value,
            SubscriptionStep.PHONE_VALIDATION.value,
            SubscriptionStep.PROFILE_COMPLETION.value,
            SubscriptionStep.IDENTITY_CHECK.value,
            SubscriptionStep.HONOR_STATEMENT.value,
            EligibilityType.AGE18.value,
        ]
        assert len(steps) == len(steps_description)
        for index, step in enumerate(steps):
            assert step.step_id == index + 1
            assert step.description == steps_description[index]

            if step.description == SubscriptionStep.IDENTITY_CHECK.value:
                assert len(step.fraud_actions_history) == 1

    @pytest.mark.parametrize(
        "dateCreated,dateOfBirth,tunnel_type",
        [
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                TunnelType.AGE18,
            ),
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1),
                TunnelType.UNDERAGE,
            ),
            (
                datetime.datetime.utcnow() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                TunnelType.UNDERAGE_AGE18,
            ),
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18 + 1, days=1),
                TunnelType.NOT_ELIGIBLE,
            ),
        ],
    )
    def test_get_steps_for_tunnel(self, dateCreated, dateOfBirth, tunnel_type):
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, dateCreated=dateCreated
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        if tunnel_type in (TunnelType.UNDERAGE, TunnelType.UNDERAGE_AGE18):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.SUSPICIOUS,
                reasonCodes=[fraud_models.FraudReasonCode.DUPLICATE_USER],
                resultContent=fraud_factories.UbbleContentFactory(),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
            )
        if tunnel_type in (TunnelType.AGE18, TunnelType.UNDERAGE_AGE18):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.AGE18,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.SUSPICIOUS,
                reasonCodes=[fraud_models.FraudReasonCode.DUPLICATE_USER],
                resultContent=fraud_factories.UbbleContentFactory(),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.AGE18,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
            )
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
        tunnel_type = _get_tunnel_type(user)
        steps = _get_steps_for_tunnel(
            user, tunnel_type, subscription_item_status, id_check_histories, fraud_reviews_desc
        )

        if tunnel_type is TunnelType.UNDERAGE:
            steps_to_compare = _get_steps_tunnel_underage(
                user, id_check_histories, item_status_15_17, fraud_reviews_desc
            )
            assert steps != steps_to_compare
        elif tunnel_type is TunnelType.AGE18:
            steps_to_compare = _get_steps_tunnel_age18(user, id_check_histories, item_status_18, fraud_reviews_desc)
            assert steps != steps_to_compare
        elif tunnel_type is TunnelType.UNDERAGE_AGE18:
            steps_to_compare = _get_steps_tunnel_underage_age18(
                user, id_check_histories, item_status_15_17, item_status_18, fraud_reviews_desc
            )
            assert steps != steps_to_compare
        else:
            steps_to_compare = _get_steps_tunnel_unspecified(item_status_15_17, item_status_18)
            assert steps == steps_to_compare

        assert len(steps) == len(steps_to_compare)

    def test_fraud_reviews_in_tunnel_steps(self, legit_user):
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth)
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.DUPLICATE_USER],
            resultContent=fraud_factories.UbbleContentFactory(),
        )

        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=legit_user,
            review=fraud_models.FraudReviewStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
        tunnel_type = _get_tunnel_type(user)
        steps = _get_steps_for_tunnel(
            user, tunnel_type, subscription_item_status, id_check_histories, fraud_reviews_desc
        )

        pass18_status_item = next((step for step in steps if step.description == "Pass 18"))
        assert len(pass18_status_item.fraud_actions_history) == 1
        assert pass18_status_item.fraud_actions_history[0]["status"] == fraud_models.FraudReviewStatus.OK.value

    @pytest.mark.parametrize(
        "dateCreated,dateOfBirth,tunnel_type",
        [
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                TunnelType.AGE18,
            ),
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1),
                TunnelType.UNDERAGE,
            ),
            (
                datetime.datetime.utcnow() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                TunnelType.UNDERAGE_AGE18,
            ),
        ],
    )
    def test_set_steps_with_active_and_disabled(self, dateCreated, dateOfBirth, tunnel_type):
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, dateCreated=dateCreated
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        if tunnel_type in (TunnelType.UNDERAGE, TunnelType.UNDERAGE_AGE18):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.SUSPICIOUS,
                reasonCodes=[fraud_models.FraudReasonCode.DUPLICATE_USER],
                resultContent=fraud_factories.UbbleContentFactory(),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
            )
        if tunnel_type in (TunnelType.AGE18, TunnelType.UNDERAGE_AGE18):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.AGE18,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.SUSPICIOUS,
                reasonCodes=[fraud_models.FraudReasonCode.DUPLICATE_USER],
                resultContent=fraud_factories.UbbleContentFactory(),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.AGE18,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
            )
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)

        if tunnel_type is TunnelType.UNDERAGE:
            steps = _get_steps_tunnel_underage(user, id_check_histories, item_status_15_17, fraud_reviews_desc)
            assert steps[3].status["active"] is False
            assert steps[4].status["disabled"] is False
        elif tunnel_type is TunnelType.AGE18:
            steps = _get_steps_tunnel_age18(user, id_check_histories, item_status_18, fraud_reviews_desc)
            assert steps[4].status["active"] is False
            assert steps[5].status["disabled"] is False
        else:
            steps = _get_steps_tunnel_underage_age18(
                user, id_check_histories, item_status_15_17, item_status_18, fraud_reviews_desc
            )
            assert steps[8].status["active"] is False
            assert steps[9].status["disabled"] is False

        _set_steps_with_active_and_disabled(steps)

        if tunnel_type is TunnelType.UNDERAGE:
            assert steps[3].status["active"] is True
            assert steps[4].status["disabled"] is True
        elif tunnel_type is TunnelType.AGE18:
            assert steps[4].status["active"] is True
            assert steps[5].status["disabled"] is True
        else:
            assert steps[8].status["active"] is True
            assert steps[9].status["disabled"] is True

    def test_get_tunnel(self):
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, isEmailValidated=True
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
        )
        eligibility_history = get_eligibility_history(user)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
        tunnel = _get_tunnel(user, eligibility_history, fraud_reviews_desc)
        assert tunnel["type"] == TunnelType.UNDERAGE
        assert tunnel["progress"] == 75

        users_factories.DepositGrantFactory(user=user)
        tunnel_end = _get_tunnel(user, eligibility_history, fraud_reviews_desc)
        assert tunnel_end["progress"] == 100


class AnonymizePublicAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.anonymize_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.ANONYMIZE_PUBLIC_ACCOUNT

    def test_anonymize_public_account(
        self,
        legit_user,
        authenticated_client,
    ):
        user = users_factories.BeneficiaryFactory(validatedBirthDate=datetime.date(2000, 1, 1))

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        assert "Anonymous" in user.firstName
        assert user.roles == [users_models.UserRole.ANONYMIZED]
        history = history_models.ActionHistory.query.one_or_none()
        assert history
        assert history.actionType == history_models.ActionType.USER_ANONYMIZED
        assert history.authorUser == legit_user
        assert history.user == user

    @pytest.mark.parametrize(
        "role",
        [
            users_models.UserRole.PRO,
            users_models.UserRole.NON_ATTACHED_PRO,
            users_models.UserRole.ANONYMIZED,
            users_models.UserRole.ADMIN,
        ],
    )
    def test_anonymize_public_account_when_user_does_not_meet_roles_criteria(
        self,
        authenticated_client,
        role,
    ):
        user = users_factories.UserFactory(roles=[role])

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.UNDERAGE_BENEFICIARY],
            [users_models.UserRole.BENEFICIARY],
            [],
        ],
    )
    def test_anonymize_public_account_when_user_is_too_young(self, authenticated_client, roles):
        user = users_factories.BeneficiaryFactory(
            validatedBirthDate=datetime.datetime.today() - datetime.timedelta(days=365 * 21), roles=roles
        )

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 400

    def test_anonymize_public_account_when_user_has_no_deposit(self, authenticated_client):
        user = users_factories.UserFactory()

        finance_models.Deposit.query.filter(finance_models.Deposit.user == user).delete()

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        assert user.roles == [users_models.UserRole.ANONYMIZED]

    @pytest.mark.parametrize(
        "factory",
        [
            users_factories.BeneficiaryGrant18Factory,
            users_factories.UnderageBeneficiaryFactory,
            users_factories.UserFactory,
        ],
    )
    def test_anonymize_public_account_when_user_is_older_than_21(self, authenticated_client, factory):
        user = factory(validatedBirthDate=datetime.datetime.today() - datetime.timedelta(days=(365 * 21) + 6))

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        assert user.roles == [users_models.UserRole.ANONYMIZED]


class ExtractPublicAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.create_extract_user_gdpr_data"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT

    expected_queries = 5  # session + user + targeted user with joined data + gdpr insert + featureflag

    @override_features(WIP_BENEFICIARY_EXTRACT_TOOL=True)
    @mock.patch("pcapi.routes.backoffice.accounts.blueprint.extract_beneficiary_data.delay")
    def test_extract_public_account(self, _mock_extract, authenticated_client, legit_user):

        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(
            authenticated_client, user_id=user.id, expected_num_queries=self.expected_queries
        )
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        extract_data = users_models.GdprUserDataExtract.query.one()
        assert extract_data.user.id == user.id
        assert extract_data.authorUser == legit_user

        response = authenticated_client.get(response.location)
        assert (
            f"L'extraction des données de l'utilisateur {user.full_name} a été demandée."
            in html_parser.extract_alert(response.data)
        )
        _mock_extract.assert_called_once_with(
            payload=gdpr_tasks.ExtractBeneficiaryDataRequest(extract_id=extract_data.id)
        )

    @override_features(WIP_BENEFICIARY_EXTRACT_TOOL=True)
    def test_extract_public_account_extract_data_already_exists(self, authenticated_client):
        gdpr_data_extract = users_factories.GdprUserDataExtractBeneficiaryFactory()

        response = self.post_to_endpoint(authenticated_client, user_id=gdpr_data_extract.user.id)
        assert response.status_code == 302

        response = authenticated_client.get(response.location)
        assert "Une extraction de données est déjà en cours pour cet utilisateur." in html_parser.extract_alert(
            response.data
        )

        assert 1 == users_models.GdprUserDataExtract.query.count()

    @override_features(WIP_BENEFICIARY_EXTRACT_TOOL=True)
    def test_extract_public_account_with_existing_extract_data_expired(self, authenticated_client, legit_user):
        expired_gdpr_data_extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=8)
        )

        with mock.patch("pcapi.routes.backoffice.accounts.blueprint.extract_beneficiary_data"):
            response = self.post_to_endpoint(authenticated_client, user_id=expired_gdpr_data_extract.user.id)
            assert response.status_code == 302

        expected_url = url_for(
            "backoffice_web.public_accounts.get_public_account",
            user_id=expired_gdpr_data_extract.user.id,
            _external=True,
        )
        assert response.location == expected_url

        extract_data = users_models.GdprUserDataExtract.query.all()
        assert len(extract_data) == 2
        assert extract_data[1].user.id == expired_gdpr_data_extract.user.id
        assert extract_data[1].authorUser == legit_user

        response = authenticated_client.get(response.location)
        assert (
            f"L'extraction des données de l'utilisateur {expired_gdpr_data_extract.user.full_name} a été demandée."
            in html_parser.extract_alert(response.data)
        )

    @override_features(WIP_BENEFICIARY_EXTRACT_TOOL=True)
    def test_extract_public_account_no_user_found(self, authenticated_client):

        response = self.post_to_endpoint(authenticated_client, user_id=42)
        assert response.status_code == 404
