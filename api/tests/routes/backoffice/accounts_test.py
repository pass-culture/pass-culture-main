import dataclasses
import datetime
import os
import re
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from flask import url_for
import pytest
import pytz

from pcapi import settings as pcapi_settings
from pcapi.connectors.dms import models as dms_models
from pcapi.core import token as token_utils
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription.models import SubscriptionItemStatus
from pcapi.core.subscription.models import SubscriptionStep
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.models import EligibilityType
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.feature import DisabledFeatureError
from pcapi.notifications.sms import testing as sms_testing
from pcapi.repository import repository
from pcapi.routes.backoffice.accounts.blueprint import RegistrationStep
from pcapi.routes.backoffice.accounts.blueprint import RegistrationStepStatus
from pcapi.routes.backoffice.accounts.blueprint import TunnelType
from pcapi.routes.backoffice.accounts.blueprint import _get_fraud_reviews_desc
from pcapi.routes.backoffice.accounts.blueprint import _get_id_check_histories_desc
from pcapi.routes.backoffice.accounts.blueprint import _get_progress
from pcapi.routes.backoffice.accounts.blueprint import _get_status
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_for_tunnel
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_age18
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_age18_old
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_underage
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_underage_age18
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_underage_age18_old
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_unspecified
from pcapi.routes.backoffice.accounts.blueprint import _get_subscription_item_status_by_eligibility
from pcapi.routes.backoffice.accounts.blueprint import _get_tunnel
from pcapi.routes.backoffice.accounts.blueprint import _get_tunnel_type
from pcapi.routes.backoffice.accounts.blueprint import _set_steps_with_active_and_disabled
from pcapi.routes.backoffice.accounts.blueprint import get_eligibility_history
from pcapi.routes.backoffice.accounts.blueprint import get_public_account_history
from pcapi.routes.backoffice.forms import search as search_forms
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


@pytest.fixture(name="storage_folder")
def storage_folder_fixture(settings):
    folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER
    os.makedirs(folder, exist_ok=True)
    try:
        yield folder
    finally:
        try:
            for child in folder.iterdir():
                if not child.is_file():
                    continue
                child.unlink()
        except FileNotFoundError:
            pass


def create_bunch_of_accounts():
    underage = users_factories.BeneficiaryFactory(
        firstName="Gédéon",
        lastName="Groidanlabénoir",
        email="gg@example.net",
        phoneNumber="+33123456789",
        phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        age=17,
    )
    old_grant_18 = users_factories.BeneficiaryGrant18Factory(
        firstName="Abdel Yves Akhim",
        lastName="Flaille",
        email="ayaf@example.net",
        phoneNumber="+33756273849",
        phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        deposit__dateCreated=pcapi_settings.CREDIT_V3_DECREE_DATETIME - relativedelta(years=1),
    )
    new_grant_18 = users_factories.BeneficiaryFactory(
        firstName="Vincent",
        lastName="Auriol",
        email="quatrièmerépu@example.net",
        phoneNumber="+33138479387",
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
    offerers_factories.UserOffererFactory(user=old_grant_18)

    return underage, old_grant_18, new_grant_18, pro, random, no_address


# TODO (prouzet) tests in which cards are checked
def assert_user_equals(result_card_text: str, expected_user: users_models.User):
    assert f"{expected_user.firstName} {expected_user.lastName} " in result_card_text
    assert f"User ID : {expected_user.id} " in result_card_text
    assert f"Email : {expected_user.email} " in result_card_text
    if birth_date := expected_user.validatedBirthDate or expected_user.dateOfBirth:
        assert f"Date de naissance : {birth_date.strftime('%d/%m/%Y')} " in result_card_text
    if users_models.UserRole.BENEFICIARY in expected_user.roles:
        if expected_user.deposit.type == finance_models.DepositType.GRANT_17_18:
            assert "Pass 18 " in result_card_text
        else:
            assert "Ancien Pass 18 " in result_card_text
    if users_models.UserRole.UNDERAGE_BENEFICIARY in expected_user.roles:
        if expected_user.deposit.type == finance_models.DepositType.GRANT_17_18:
            assert "Pass 17 " in result_card_text
        else:
            assert "Ancien Pass 15-17 " in result_card_text
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

        with assert_num_queries(self.expected_num_queries_when_no_query + 1):  #  rollback
            response = authenticated_client.get(url)
            assert response.status_code == 400

    @pytest.mark.parametrize("query", ["", " ", "   ", " , ,,;"])
    def test_empty_query(self, authenticated_client, query):
        with assert_num_queries(self.expected_num_queries_when_no_query + 1):  #  rollback
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 400

    def test_can_search_public_account_by_id(self, authenticated_client):
        underage, _, _, _, _, _ = create_bunch_of_accounts()
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
        searched_user1, _, _, _, searched_user2, _ = create_bunch_of_accounts()
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
        with assert_num_queries(self.expected_num_queries_when_no_query + 1):  #  rollback
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
            ("Gérard", 3),  # Gérard
            ("Gerard", 3),  # Gérard
            ("Jean Luc", 5),  # Jean-Luc
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
        _, _, _, _, random, _ = create_bunch_of_accounts()

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
        _, _, _, _, random, _ = create_bunch_of_accounts()
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

    def test_can_search_public_account_by_multiple_emails(self, authenticated_client):
        searched_user1, _, _, _, searched_user2, _ = create_bunch_of_accounts()
        search_query = f" {searched_user1.email},   {searched_user2.email},"

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))
            assert response.status_code == 200

        cards_titles = html_parser.extract_cards_titles(response.data)
        assert set(cards_titles) == {searched_user1.full_name, searched_user2.full_name}

    def test_can_search_public_account_by_email_domain(self, authenticated_client):
        underage, old_grant_18, new_grant_18, _, random, _ = create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="@example.net"))
            assert response.status_code == 200

        cards_titles = html_parser.extract_cards_titles(response.data)
        assert set(cards_titles) == {
            underage.full_name,
            old_grant_18.full_name,
            new_grant_18.full_name,
            random.full_name,
        }

        cards_text = html_parser.extract_cards_text(response.data)
        assert_user_equals(cards_text[0], underage)
        assert_user_equals(cards_text[1], old_grant_18)
        assert_user_equals(cards_text[2], new_grant_18)
        assert_user_equals(cards_text[3], random)

    @pytest.mark.parametrize("query", ["+33756273849", "0756273849", "756273849"])
    def test_can_search_public_account_by_phone(self, authenticated_client, query):
        _, old_grant_18, _, _, _, _ = create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=old_grant_18.id,
            q=query,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_public_account_even_with_missing_city_address(self, authenticated_client):
        _, _, _, _, _, no_address = create_bunch_of_accounts()
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
        _, old_grant_18, _, _, _, _ = create_bunch_of_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=old_grant_18.id,
            q=query,
            search_rank=1,
            total_items=1,
        )

        redirected_response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(redirected_response.data, raise_if_not_found=False) is None

    def test_can_search_public_account_by_first_name_and_very_short_name(self, authenticated_client):
        create_bunch_of_accounts()
        user = users_factories.UserFactory(firstName="ANN", lastName="A", email="ann.a@example.com")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="Ann A"))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=user.id,
            q="Ann A",
            search_rank=1,
            total_items=1,
        )

        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Les termes étant très courts, la recherche n'a porté que sur le nom complet exact."
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

        with assert_num_queries(self.expected_num_queries_when_no_query + 1):  #  rollback
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

        with assert_num_queries(self.expected_num_queries_when_no_query + 1):  #  rollback
            response = authenticated_client.get(url_for(self.endpoint, q="%terms"))
            assert response.status_code == 400

        assert "Le caractère % n'est pas autorisé" in html_parser.extract_warnings(response.data)

    def test_can_search_public_account_young_but_also_pro(self, authenticated_client):
        # She has started subscription process, but is also hired by an offerer
        young_and_pro = users_factories.BeneficiaryFactory(
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
        underage, old_grant_18, _, _, _, _ = create_bunch_of_accounts()
        # we must have at least two results so that it does not redirect to details page and we can check cards content
        common_name = "Suspended-Family"
        underage.lastName = common_name
        underage.isActive = False
        old_grant_18.lastName = common_name
        old_grant_18.isActive = False
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
        assert_user_equals(cards_text[1], old_grant_18)

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
            (search_forms.AccountSearchFilter.PASS_17_V3.name, "underage_user"),
            (search_forms.AccountSearchFilter.PASS_18_V3.name, "beneficiary_user"),
            (search_forms.AccountSearchFilter.PASS_15_17.name, "old_underage_user"),
            (search_forms.AccountSearchFilter.PASS_18.name, "old_beneficiary_user"),
            (search_forms.AccountSearchFilter.PUBLIC.name, "public_user"),
            (search_forms.AccountSearchFilter.SUSPENDED.name, "suspended_user"),
        ],
    )
    def test_search_with_single_filter(
        self, authenticated_client, search_filter, expected_user
    ):  # pylint: disable=possibly-unused-variable
        common_name = "Last-Name"
        underage_user = users_factories.BeneficiaryFactory(
            lastName=common_name,
            age=17,
            deposit__type=finance_models.DepositType.GRANT_17_18,
        )
        beneficiary_user = users_factories.BeneficiaryFactory(
            lastName=common_name,
            deposit__type=finance_models.DepositType.GRANT_17_18,
        )
        old_underage_user = users_factories.UnderageBeneficiaryFactory(lastName=common_name)
        old_beneficiary_user = users_factories.BeneficiaryGrant18Factory(
            lastName=common_name, deposit__type=finance_models.DepositType.GRANT_18
        )
        public_user = users_factories.UserFactory(lastName=common_name)
        suspended_user = users_factories.BeneficiaryFactory(lastName=common_name, isActive=False)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=common_name, filter=search_filter))
            assert response.status_code == 303

        redirected_id = int(re.match(r".*/(\d+)\?.*", response.location).group(1))
        assert redirected_id == locals()[expected_user].id

    def test_search_with_several_filters(self, authenticated_client):
        common_name = "First-Name"
        common_last_name = "Last-Name"
        underage_user = users_factories.BeneficiaryFactory(firstName=common_name, lastName=common_last_name, age=17)
        users_factories.BeneficiaryFactory(
            firstName=common_name,
            lastName=common_last_name,
        )
        users_factories.UserFactory(
            firstName=common_name,
            lastName=common_last_name,
        )
        suspended_user = users_factories.BeneficiaryFactory(
            firstName=common_name, lastName=common_last_name, isActive=False
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q=common_name,
                    filter=[
                        search_forms.AccountSearchFilter.PASS_17_V3.name,
                        search_forms.AccountSearchFilter.SUSPENDED.name,
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
    # session
    # current user
    # user data
    # check if user is waiting to be anonymized
    # bookings
    expected_num_queries = 5
    expected_num_queries_with_ff = expected_num_queries + 1

    class ReviewButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.BENEFICIARY_MANUAL_REVIEW
        button_label = "Revue manuelle"

        @property
        def path(self):
            user = users_factories.UserFactory()
            return url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

    class InvalidatePasswordButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT
        button_label = "Invalider le mot de passe"

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

    @pytest.mark.parametrize("index,expected_badge", [(0, "Pass 17"), (1, "Ancien Pass 18"), (2, "Pass 18"), (3, None)])
    def test_get_public_account(self, authenticated_client, index, expected_badge):
        users = create_bunch_of_accounts()
        user = users[index]

        user_id = user.id
        with assert_num_queries(self.expected_num_queries_with_ff):
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
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Suspendu : Fraude hacking" in badges

        content = html_parser.content_as_text(response.data)
        assert "Date de suspension : 03/11/2023" in content

    def test_get_public_account_with_unconfirmed_modified_email(self, authenticated_client):
        user = users_factories.UserFactory()
        users_factories.EmailUpdateEntryFactory(user=user)
        users_factories.EmailConfirmationEntryFactory(user=user)
        users_factories.NewEmailSelectionEntryFactory(user=user)
        user_id = user.id

        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)
        assert parsed_html.find("i", class_="pc-email-changed-icon") is None

    def test_get_public_account_with_confirmed_modified_email(self, authenticated_client):
        user = users_factories.UserFactory()
        users_factories.EmailUpdateEntryFactory(user=user)
        users_factories.EmailConfirmationEntryFactory(user=user)
        users_factories.NewEmailSelectionEntryFactory(user=user)
        users_factories.EmailValidationEntryFactory(user=user)
        user_id = user.id

        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)
        assert parsed_html.find("i", class_="pc-email-changed-icon") is not None

    def test_get_public_account_with_admin_modified_email(self, authenticated_client):
        user = users_factories.UserFactory()
        users_factories.EmailAdminUpdateEntryFactory(user=user)
        user_id = user.id

        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)
        assert parsed_html.find("i", class_="pc-email-changed-icon") is not None

    @pytest.mark.parametrize(
        "reasonCodes,reason",
        (
            (
                [fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER],
                "La pièce d'identité n°{id_piece_number} est déjà prise par l'utilisateur {original_user_id}",
            ),
            ([fraud_models.FraudReasonCode.DUPLICATE_USER], "Duplicat de l'utilisateur {original_user_id}"),
        ),
    )
    def test_get_public_account_with_resolved_duplicate(self, authenticated_client, reasonCodes, reason):
        first_name = "Jack"
        last_name = "Sparrow"
        email = "jsparrow@pirate.mail"
        birth_date = datetime.datetime.utcnow() - relativedelta(years=18, days=15)
        id_piece_number = "1234243344533"

        original_user = users_factories.BeneficiaryFactory(
            dateCreated=birth_date + relativedelta(years=18, months=3),
            firstName=first_name,
            lastName=last_name,
            dateOfBirth=birth_date,
            validatedBirthDate=birth_date,
            email=email,
            idPieceNumber=id_piece_number,
        )

        reason = reason.format(id_piece_number=id_piece_number, original_user_id=original_user.id)

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
            eligibilityType=users_models.EligibilityType.AGE17_18,
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
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        duplicate_user_id = duplicate_user.id
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=duplicate_user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"User ID doublon : {original_user.id}" in content

    def test_get_public_account_birth_dates(self, authenticated_client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, days=15),
            validatedBirthDate=datetime.datetime.utcnow() - relativedelta(years=17, days=15),
        )
        user_id = user.id

        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"Date de naissance {user.validatedBirthDate.strftime('%d/%m/%Y')} " in content
        assert f"Date de naissance déclarée à l'inscription {user.dateOfBirth.strftime('%d/%m/%Y')} " in content

    @pytest.mark.parametrize(
        "user_factory,expected_remaining_text,expected_digital_remaining_text",
        [
            (
                users_factories.BeneficiaryFactory,
                "137,50 € Crédit restant 150,00 €",
                "87,50 € Crédit digital restant 100,00 €",
            ),
            (
                users_factories.CaledonianBeneficiaryFactory,
                "137,50 € (16408 CFP) Crédit restant 150,00 € (17900 CFP)",
                "87,50 € (10442 CFP) Crédit digital restant 100,00 € (11933 CFP)",
            ),
        ],
    )
    def test_get_beneficiary_credit(
        self, authenticated_client, user_factory, expected_remaining_text, expected_digital_remaining_text
    ):
        beneficiary = user_factory()

        bookings_factories.BookingFactory(
            user=beneficiary,
            stock__offer__subcategoryId=subcategories.VOD.id,
            stock__offer__url="http://example.com",
            amount=12.5,
            user__deposit__expirationDate=datetime.datetime(year=2031, month=12, day=31),
        )

        user_id = beneficiary.id
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        # Remaining credit + Title + Initial Credit
        assert expected_remaining_text in cards_text
        assert expected_digital_remaining_text in cards_text

    def test_get_non_beneficiary_credit(self, authenticated_client):
        _, _, _, _, random, _ = create_bunch_of_accounts()
        user_id = random.id

        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert "Crédit restant" not in html_parser.content_as_text(response.data)

    @pytest.mark.parametrize(
        "user_factory,expected_price_1,expected_price_2",
        [
            (users_factories.BeneficiaryFactory, "20,00 €", "12,50 €"),
            (users_factories.CaledonianBeneficiaryFactory, "20,00 € (2387 CFP)", "12,50 € (1492 CFP)"),
        ],
    )
    def test_get_beneficiary_bookings(self, authenticated_client, user_factory, expected_price_1, expected_price_2):
        user = user_factory()
        b1 = bookings_factories.CancelledBookingFactory(
            user=user,
            amount=12.5,
            dateCreated=datetime.date.today() - relativedelta(days=2),
            stock__offer__bookingContact="contact.offer@example.com",
            stock__offer__bookingEmail="booking.offer@example.com",
        )
        b2 = bookings_factories.UsedBookingFactory(user=user, amount=20)
        bookings_factories.UsedBookingFactory()

        user_id = user.id
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        bookings = html_parser.extract_table_rows(response.data, parent_class="bookings-tab-pane")
        assert len(bookings) == 2

        assert bookings[0]["Offreur"] == b2.offerer.name
        assert bookings[0]["Nom de l'offre"] == b2.stock.offer.name
        assert bookings[0]["Prix"] == expected_price_1
        assert bookings[0]["Date de résa"].startswith(datetime.date.today().strftime("Le %d/%m/%Y"))
        assert bookings[0]["État"] == "Le jeune a consommé l'offre"
        assert bookings[0]["Contremarque"] == b2.token

        assert bookings[1]["Offreur"] == b1.offerer.name
        assert bookings[1]["Nom de l'offre"] == b1.stock.offer.name
        assert bookings[1]["Prix"] == expected_price_2
        assert bookings[1]["Date de résa"].startswith(
            (datetime.date.today() - relativedelta(days=2)).strftime("Le %d/%m/%Y")
        )
        assert bookings[1]["État"] == "L'offre n'a pas eu lieu"
        assert bookings[1]["Contremarque"] == b1.token

        extra_rows = html_parser.extract(response.data, "tr", class_="accordion-collapse")
        assert len(extra_rows) == 2

        assert f"Utilisée le : {datetime.date.today().strftime('%d/%m/%Y')}" in extra_rows[0]
        assert "Annulée le" not in extra_rows[0]
        assert "Motif d'annulation" not in extra_rows[0]
        assert f"Contact du partenaire culturel : {b2.venue.contact.email}" in extra_rows[0]
        assert f"Notification du partenaire culturel : {b2.venue.bookingEmail}" in extra_rows[0]

        assert "Utilisée le" not in extra_rows[1]
        assert f"Annulée le : {datetime.date.today().strftime('%d/%m/%Y')}" in extra_rows[1]
        assert "Motif d'annulation : Annulée par le bénéficiaire" in extra_rows[1]
        assert f"Contact du partenaire culturel : {b1.venue.contact.email}" in extra_rows[1]
        assert "Contact pour cette offre : contact.offer@example.com" in extra_rows[1]
        assert f"Notification du partenaire culturel : {b1.venue.bookingEmail}" in extra_rows[1]
        assert "Notification pour cette offre : booking.offer@example.com" in extra_rows[1]

    def test_get_beneficiary_bookings_empty(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        bookings_factories.UsedBookingFactory()

        user_id = user.id
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert not html_parser.extract_table_rows(response.data, parent_class="bookings-tab-pane")
        assert "Aucune réservation à ce jour" in response.data.decode("utf-8")

    def test_fraud_check_link(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        # modifiy the date for clearer tests
        old_dms = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=datetime.datetime.utcnow() + datetime.timedelta(days=2),
        )

        user_id = user.id
        with assert_num_queries(self.expected_num_queries_with_ff):
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
            dateCreated=datetime.datetime.utcnow() + datetime.timedelta(days=3),
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
        user = users_factories.BeneficiaryFactory(dateCreated=datetime.datetime.utcnow() - relativedelta(days=40))
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
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert response.status_code == 200
        history_rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(history_rows) == 10

        assert history_rows[0]["Type"] == "Étape de vérification"
        assert history_rows[0]["Date/Heure"].startswith(datetime.date.today().strftime("Le %d/%m/%Y à"))
        assert history_rows[0]["Commentaire"] == "honor_statement, age-17-18, ok, [raison inconnue], None"
        assert not history_rows[0]["Auteur"]

        assert history_rows[1]["Type"] == "Étape de vérification"
        assert history_rows[1]["Date/Heure"].startswith(datetime.date.today().strftime("Le %d/%m/%Y à"))
        assert history_rows[1]["Commentaire"] == "ubble, age-17-18, ok, [raison inconnue], None"
        assert not history_rows[1]["Auteur"]

        assert history_rows[2]["Type"] == "Étape de vérification"
        assert history_rows[2]["Date/Heure"].startswith(datetime.date.today().strftime("Le %d/%m/%Y à"))
        assert history_rows[2]["Commentaire"] == "profile_completion, age-17-18, ok, [raison inconnue], None"
        assert not history_rows[2]["Auteur"]

        assert history_rows[3]["Type"] == "Étape de vérification"
        assert history_rows[3]["Date/Heure"].startswith(datetime.date.today().strftime("Le %d/%m/%Y à"))
        assert history_rows[3]["Commentaire"] == "phone_validation, age-17-18, ok, [raison inconnue], None"
        assert not history_rows[3]["Auteur"]

        assert history_rows[4]["Type"] == history_models.ActionType.INFO_MODIFIED.value
        assert history_rows[4]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=30)).strftime("Le %d/%m/%Y à ")
        )
        assert history_rows[4]["Commentaire"].startswith("Informations modifiées :")
        assert "Nom : Pignon → Leblanc" in history_rows[4]["Commentaire"]
        assert "Prénom : suppression de : François" in history_rows[4]["Commentaire"]
        assert "Date de naissance : 2001-04-14 → 2000-09-19" in history_rows[4]["Commentaire"]
        assert history_rows[4]["Auteur"] == admin.full_name

        assert history_rows[5]["Type"] == history_models.ActionType.USER_UNSUSPENDED.value
        assert history_rows[5]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=35)).strftime("Le %d/%m/%Y à ")
        )
        assert history_rows[5]["Commentaire"] == unsuspended.comment
        assert history_rows[5]["Auteur"] == admin.full_name

        assert history_rows[6]["Type"] == history_models.ActionType.USER_CREATED.value
        assert history_rows[6]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=40)).strftime("Le %d/%m/%Y à ")
        )
        assert not history_rows[6]["Commentaire"]
        assert history_rows[6]["Auteur"] == user.full_name

        assert history_rows[7]["Type"] == "Attribution d'un crédit"
        assert history_rows[7]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=40)).strftime("Le %d/%m/%Y à ")
        )
        assert history_rows[7]["Commentaire"] == "Attribution d'un crédit 17-18 de 150,00 €"

        assert history_rows[8]["Type"] == "Recrédit du compte"
        assert history_rows[8]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=40)).strftime("Le %d/%m/%Y à ")
        )
        assert history_rows[8]["Commentaire"] == "Recrédit à 18 ans de 150,00 € sur un crédit 17-18"

        assert history_rows[9]["Type"] == history_models.ActionType.USER_SUSPENDED.value
        assert not history_rows[9]["Date/Heure"]  # Empty date, at the end of the list
        assert history_rows[9]["Commentaire"].startswith("Fraude suspicion")
        assert history_rows[9]["Auteur"] == legit_user.full_name

    def test_get_public_account_anonymized_user(self, authenticated_client):
        user = users_factories.UserFactory(roles=[users_models.UserRole.ANONYMIZED])

        user_id = user.id
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"User ID : {user.id} " in content

        available_button = html_parser.extract(response.data, tag="button")
        assert "Anonymiser" not in available_button


class UpdatePublicAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.update_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_update_field(self, legit_user, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        old_email = user.email
        old_phone_number = user.phoneNumber
        old_postal_code = user.postalCode

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
        assert user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED
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
            "phoneNumber": {"new_info": "+33836656565", "old_info": old_phone_number},
            "postalCode": {"new_info": expected_new_postal_code, "old_info": old_postal_code},
        }

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "FIRSTNAME": user.firstName,
            "LASTNAME": user.lastName,
            "UPDATED_FIELD": "EMAIL,PHONE_NUMBER",
        }

    def test_update_all_fields(self, legit_user, authenticated_client):
        user = users_factories.BeneficiaryFactory(
            firstName="Edmond",
            lastName="Dantès",
            address="Château d'If",
            postalCode="13007",
            city="Marseille",
            email="ed@example.com",
            id_piece_number="123456654321",
            phoneNumber="+33601234567",
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
        assert user.dateOfBirth.date() != form_data["birth_date"]
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
                "old_info": user.dateOfBirth.date().isoformat(),
            },
            "idPieceNumber": {"new_info": "A123B456C", "old_info": "123456654321"},
            "phoneNumber": {"new_info": None, "old_info": "+33601234567"},
            "address": {"new_info": "Chemin du Haut des Ormes", "old_info": "Château d'If"},
            "postalCode": {"new_info": "78560", "old_info": "13007"},
            "city": {"new_info": "Port-Marly", "old_info": "Marseille"},
            "notificationSubscriptions.marketing_email": {"new_info": False, "old_info": True},
        }

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "FIRSTNAME": user.firstName,
            "LASTNAME": user.lastName,
            "UPDATED_FIELD": "EMAIL,FIRST_NAME,LAST_NAME",
        }

    def test_update_email_for_suspended_user(self, legit_user, authenticated_client):
        user = users_factories.UserFactory(isActive=False)

        form_data = {
            "first_name": user.firstName,
            "last_name": user.lastName,
            "email": "updated@example.com",
            "birth_date": user.birth_date,
            "phone_number": user.phoneNumber,
            "id_piece_number": user.idPieceNumber,
            "street": user.address,
            "postal_code": user.postalCode,
            "city": user.city,
            "marketing_email_subscription": "on",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form_data)
        assert response.status_code == 303

        user = users_models.User.query.filter_by(id=user.id).one()
        assert user.email == "updated@example.com"

        assert len(user.email_history) == 1
        assert len(mails_testing.outbox) == 0

    def test_unknown_field(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryFactory()
        base_form = {
            "first_name": user_to_edit.firstName,
            "unknown": "field",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=base_form)
        assert response.status_code == 400
        assert len(mails_testing.outbox) == 0

    def test_update_email_triggers_history_token_and_mail(self, authenticated_client):
        user, _, _, _, _, _ = create_bunch_of_accounts()

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
        user, _, _, _, _, _ = create_bunch_of_accounts()

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form={"email": "updated.example.com"})

        assert response.status_code == 400
        assert "Le formulaire n'est pas valide" in html_parser.extract_alert(response.data)

    def test_email_already_exists(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryFactory()
        other_user = users_factories.BeneficiaryFactory()

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
        user_to_edit = users_factories.BeneficiaryFactory()

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": user_to_edit.email,
            "postal_code": "7500",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=base_form)
        assert response.status_code == 400

    def test_id_piece_number_already_exists(self, legit_user, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        other_user = users_factories.BeneficiaryFactory()

        form_data = {
            "first_name": user.firstName,
            "last_name": user.lastName,
            "email": user.email,
            "birth_date": user.birth_date,
            "phone_number": user.phoneNumber,
            "id_piece_number": other_user.idPieceNumber,
            "street": user.address,
            "postal_code": user.postalCode,
            "city": user.city,
            "marketing_email_subscription": "on",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form_data)
        assert response.status_code == 400

        assert (
            html_parser.extract_alert(response.data)
            == f"Le numéro de pièce d'identité {other_user.idPieceNumber} est déja associé à un autre compte utilisateur."
        )

        assert user.idPieceNumber != other_user.idPieceNumber
        assert history_models.ActionHistory.query.count() == 0

    def test_empty_id_piece_number(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryFactory()

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
        user_to_edit = users_factories.BeneficiaryFactory()
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
        assert token_utils.Token.token_exists(token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, user.id)

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
        user = users_factories.BeneficiaryFactory(isEmailValidated=True)
        response = self.post_to_endpoint(authenticated_client, user_id=user.id)

        assert response.status_code == 303
        assert not mails_testing.outbox


class ManuallyValidatePhoneNumberTest(PostEndpointHelper):
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

    @pytest.mark.usefixtures("clean_database")
    def test_manually_validate_phone_number_exception(self, authenticated_client):
        user = users_factories.UserFactory(phoneValidationStatus=None, phoneNumber="+33601010203")

        token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, users_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
        )
        token_utils.Token.create(
            token_utils.TokenType.PHONE_VALIDATION, users_constants.PHONE_VALIDATION_TOKEN_LIFE_TIME, user.id
        )

        with patch(
            "pcapi.core.subscription.api.activate_beneficiary_if_no_missing_step",
            side_effect=subscription_exceptions.InvalidEligibilityTypeException("Test"),
        ):
            response = self.post_to_endpoint(authenticated_client, user_id=user.id, follow_redirects=True)

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == "Une erreur s'est produite : Test"

        db.session.refresh(user)
        assert not user.is_phone_validated
        assert not user.roles
        assert not user.deposits
        assert history_models.ActionHistory.query.count() == 0
        assert token_utils.Token.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)


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

        with patch("pcapi.core.fraud.phone_validation.sending_limit.is_SMS_sending_allowed") as limit_mock:
            limit_mock.return_value = False
            response = self.post_to_endpoint(authenticated_client, user_id=user.id)

        assert limit_mock.call_count == 0
        assert response.status_code == 303
        assert token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_nothing_sent_use_cases(self, authenticated_client):
        other_user = users_factories.BeneficiaryFactory(
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
            users_factories.BeneficiaryFactory(phoneNumber="+33601020304"),
            # email has not been validated
            users_factories.UserFactory(phoneNumber="+33601020304", isEmailValidated=False),
            # phone number is already used
            users_factories.UserFactory(phoneNumber=other_user.phoneNumber),
        ]

        for idx, user in enumerate(users):
            response = self.post_to_endpoint(authenticated_client, user_id=user.id)

            assert response.status_code == 303, f"[{idx}] found: {response.status_code}, expected: 303"
            assert not sms_testing.requests, f"[{idx}] {len(sms_testing.requests)} sms sent"


class ReviewPublicAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.review_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.BENEFICIARY_MANUAL_REVIEW

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

    def test_set_beneficiary_on_underage(self, authenticated_client, legit_user, settings):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        user = users_factories.BeneficiaryFactory(age=17, dateCreated=before_decree)

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
        user = users_factories.BeneficiaryFactory()

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

    def test_pre_decree_eligibility_from_v3_eligibility(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryFactory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            "Le compte est déjà bénéficiaire du Pass 17-18, il ne peut pas aussi être bénéficiaire de l'ancien Pass 18"
            in html_parser.extract_alert(response.data)
        )

    def test_unlocks_recredit_18(self, authenticated_client):
        user = users_factories.BeneficiaryFactory(age=17)
        eighteen_years_ago = datetime.datetime.utcnow() - relativedelta(years=18, months=1)
        user.validatedBirthDate = eighteen_years_ago

        base_form = {
            "status": fraud_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE17_18.name,
            "reason": "test",
        }
        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        user = users_models.User.query.filter_by(id=user.id).one()
        assert any(
            recredit.recreditType == finance_models.RecreditType.RECREDIT_18 for recredit in user.deposit.recredits
        )

    @pytest.mark.parametrize("exception_class", [finance_exceptions.UserCannotBeRecredited, DisabledFeatureError])
    def test_review_public_account_exception(self, authenticated_client, exception_class):
        user = users_factories.BeneficiaryFactory()

        form = {
            "status": fraud_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE17_18.name,
            "reason": "test",
        }

        with patch(
            "pcapi.core.subscription.api.activate_beneficiary_for_eligibility",
            side_effect=exception_class(),
        ):
            response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form, follow_redirects=True)

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == f"Une erreur s'est produite : {exception_class.__name__}"


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
            user=user,
            creationDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
            newUserEmail=None,
            newDomainEmail=None,
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
        assert history[2].comment == f"Lien envoyé à {email_request.oldEmail} pour choisir une nouvelle adresse email"

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
        assert history[1].authorUser == dms.author

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

    def test_history_contains_deposits_and_recredits(self):
        now = datetime.datetime.utcnow()
        user = users_factories.UserFactory(dateCreated=now - datetime.timedelta(days=10))
        recredit_17 = finance_factories.RecreditFactory(
            recreditType=finance_models.RecreditType.RECREDIT_17,
            amount=30,
            dateCreated=now - datetime.timedelta(days=8),
            deposit__user=user,
            deposit__type=finance_models.DepositType.GRANT_15_17,
            deposit__amount=30,
        )
        deposit_15_17 = user.deposit
        # a grant 17_18 deposit is created empty, then a recredit is added to fill it
        deposit_17_18 = users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_17_18,
            dateCreated=now - datetime.timedelta(days=5),
            amount=150,
        )
        recredit_18 = deposit_17_18.recredits[0]
        recredit_previous = finance_factories.RecreditFactory(
            recreditType=finance_models.RecreditType.PREVIOUS_DEPOSIT,
            amount=15,
            dateCreated=now - datetime.timedelta(days=4),
            deposit=deposit_17_18,
        )

        history = get_public_account_history(user)

        assert len(history) >= 5

        assert history[0].actionType == "Attribution d'un crédit"
        assert history[0].actionDate == deposit_15_17.dateCreated
        assert history[0].comment == "Attribution d'un ancien crédit 15-17 de 30,00 €"

        assert history[1].actionType == "Recrédit du compte"
        assert history[1].actionDate == recredit_previous.dateCreated
        assert history[1].comment == "Recrédit de l'argent restant du crédit précédent de 15,00 € sur un crédit 17-18"

        assert history[2].actionType == "Attribution d'un crédit"
        assert history[2].actionDate == deposit_17_18.dateCreated
        assert history[2].comment == "Attribution d'un crédit 17-18 de 150,00 €"

        assert history[3].actionType == "Recrédit du compte"
        assert history[3].actionDate == recredit_18.dateCreated
        assert history[3].comment == "Recrédit à 18 ans de 150,00 € sur un crédit 17-18"

        assert history[4].actionType == "Recrédit du compte"
        assert history[4].actionDate == recredit_17.dateCreated
        assert history[4].comment == "Recrédit à 17 ans de 30,00 € sur un ancien crédit 15-17"

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

    @pytest.mark.parametrize("signup_age", [15, 16])
    def test_registration_age_lt_17_decree_age_lt_17_current_age_lt_17(
        self, authenticated_client, settings, signup_age
    ):
        # Setup:
        # - Sign-up at 15 or 16
        # - At decree start → user is 15 or 16
        # - User is 15 or 16 years old now
        #
        # Expected registration timeline:
        #  1. Email validation ✓
        #  2. Complete profile ✓
        #  3. ID check ✓
        #  4. Honor statement ✓
        #  5. Pass 15-17 ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=signup_age, months=3)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=signup_age, months=1)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=signup_age, days=5),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=birth_date,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=30_00,
            type="GRANT_15_17",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage"]')
        assert len(step_icon_views) == 5
        assert len(step_icon_titles) == 5
        assert len(text_views) == 5

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Ancien Pass 15-17"

    @pytest.mark.parametrize("signup_age", [15, 16])
    def test_registration_age_lt_16_decree_age_lt_17_current_age_gte_18(
        self, authenticated_client, settings, signup_age
    ):
        # Setup:
        # - Sign-up at 15 or 16
        # - At decree start → user is 15 or 16
        # - User is over 18 years old now
        #
        # Expected registration timeline:
        #  1. Email validation ✓
        #  2. Complete profile ✓
        #  3. ID check ✓
        #  4. Honor statement ✓
        #  5. Pass 15-17 ✓
        #  6. Pass 17 ✓
        #  7. Phone validation ✓
        #  8. Complete profile ✓
        #  9. ID check ✓
        # 10. Honor statement ✓
        # 11. Pass 18 ✓
        now = datetime.datetime.utcnow()
        date_of_birth = now - relativedelta(years=18, months=3)
        settings.CREDIT_V3_DECREE_DATETIME = date_of_birth + relativedelta(years=16, months=3)
        user = users_factories.UserFactory(
            age=18,
            dateCreated=date_of_birth + relativedelta(years=signup_age, days=5),
            dateOfBirth=date_of_birth,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.BENEFICIARY],
            validatedBirthDate=date_of_birth,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=30_00,
            type="GRANT_15_17",
            expirationDate=settings.CREDIT_V3_DECREE_DATETIME,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=150_00,
            type="GRANT_17_18",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage+age-17-18"]')
        assert len(step_icon_views) == 11
        assert len(step_icon_titles) == 11
        assert len(text_views) == 11

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Ancien Pass 15-17"

        assert step_icon_titles[5] == SubscriptionItemStatus.OK.value
        assert text_views[5].text == "Pass 17"

        assert step_icon_titles[6] == SubscriptionItemStatus.OK.value
        assert text_views[6].text == "Validation N° téléphone"

        assert step_icon_titles[7] == SubscriptionItemStatus.OK.value
        assert text_views[7].text == "Profil Complet"

        assert step_icon_titles[8] == SubscriptionItemStatus.OK.value
        assert text_views[8].text == "ID Check"

        assert step_icon_titles[9] == SubscriptionItemStatus.OK.value
        assert text_views[9].text == "Attestation sur l'honneur"

        assert step_icon_titles[10] == SubscriptionItemStatus.OK.value
        assert text_views[10].text == "Pass 18"

    def test_registration_at_age16_and_becoming_17_before_decree_current_age17(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 16
        # - Decree starts 1 year later → User is 17 years old at that moment
        # - User is 17 years old now
        #
        # Expected registration timeline:
        #  1. Email validation ✓
        #  2. Complete profile ✓
        #  3. ID check ✓
        #  4. Honor statement ✓
        #  5. Pass 15-17 ✓
        #  6. ID check ✓
        #  7. Honor statement ✓
        #  8. Pass 17 ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=17, months=6, days=19)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=17, months=5)
        signup_date = birth_date + relativedelta(years=16, months=4)
        user = users_factories.UserFactory(
            dateCreated=signup_date,
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=birth_date,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=30_00,
            type="GRANT_15_17",
            expirationDate=settings.CREDIT_V3_DECREE_DATETIME,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=80_00,
            type="GRANT_17_18",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=signup_date,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.CANCELED,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=signup_date,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME + relativedelta(days=3),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME + relativedelta(days=3),
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage+age-17"]')
        assert len(step_icon_views) == 8
        assert len(step_icon_titles) == 8
        assert len(text_views) == 8

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Ancien Pass 15-17"

        assert step_icon_titles[5] == SubscriptionItemStatus.OK.value
        assert text_views[5].text == "ID Check"

        assert step_icon_titles[6] == SubscriptionItemStatus.OK.value
        assert text_views[6].text == "Attestation sur l'honneur"

        assert step_icon_titles[7] == SubscriptionItemStatus.OK.value
        assert text_views[7].text == "Pass 17"

    def test_registration_at_age15_and_becoming_16_before_decree_current_age17(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 15
        # - Decree starts 1 year later → User is 16 years old at that moment
        # - User is 17 years old now
        #
        # Expected registration timeline:
        #  1. Email validation ✓
        #  2. Complete profile ✓
        #  3. ID check ✓
        #  4. Honor statement ✓
        #  5. Pass 15-17 ✓
        #  6. ID check ✓
        #  7. Honor statement ✓
        #  8. Pass 17 ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=17, months=3)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=16, months=2)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=15, months=1),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=birth_date,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=150_00,
            type="GRANT_17_18",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage+age-17"]')
        assert len(step_icon_views) == 8
        assert len(step_icon_titles) == 8
        assert len(text_views) == 8

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.VOID.value
        assert text_views[4].text == "Ancien Pass 15-17"

        assert step_icon_titles[5] == SubscriptionItemStatus.OK.value
        assert text_views[5].text == "ID Check"

        assert step_icon_titles[6] == SubscriptionItemStatus.OK.value
        assert text_views[6].text == "Attestation sur l'honneur"

        assert step_icon_titles[7] == SubscriptionItemStatus.OK.value
        assert text_views[7].text == "Pass 17"

    def test_registration_at_age15_before_decree(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 15
        # - Decree starts 1 month later → User is 15 years old at that moment
        # - User is 15 years old now
        #
        # Expected registration timeline:
        # 1. Email Validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✓
        # 5. Pass 15-17 ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=15, months=7)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=15, months=1)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=15, days=1),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=birth_date,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=150_00,
            type="GRANT_15_17",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage"]')
        assert len(step_icon_views) == 5
        assert len(step_icon_titles) == 5
        assert len(text_views) == 5

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Ancien Pass 15-17"

    def test_registration_at_age15_after_decree(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 15
        # - Decree started 1 month earlier → User is 15 years old at that moment
        # - User is 15 years old now
        #
        # Expected registration timeline:
        # 1. Email Validation ✓
        # 2. Not Eligible ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=15, months=4, days=15)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=15, months=5)
        user = users_factories.UserFactory(
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME + relativedelta(days=5),
            dateOfBirth=birth_date,
            phoneValidationStatus=None,
            roles=[],
            validatedBirthDate=birth_date,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="not-eligible"]')
        assert len(step_icon_views) == 2
        assert len(step_icon_titles) == 2
        assert len(text_views) == 2

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Non éligible"

    def test_registration_at_age_17_on_birthdate_after_decree(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 17
        # - Decree starts on the same day → User is 17 years old at that moment
        # - User is 17 years old now
        #
        # Expected registration timeline:
        # 1. Email Validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✓
        # 5. Pass 15-17 ✓
        now = datetime.datetime.utcnow()
        birth_date = (now - relativedelta(years=17)).replace(hour=0, minute=0, second=0, microsecond=0)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=17) - relativedelta(days=1)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=17, hours=9),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=birth_date,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="age-17"]')
        assert len(step_icon_views) == 5
        assert len(step_icon_titles) == 5
        assert len(text_views) == 5

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.VOID.value
        assert text_views[4].text == "Pass 17"

    def test_registration_at_age17_before_decree(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 17
        # - Decree starts 1 month later → User is 17 years old at that moment
        # - User is 17 years old now
        #
        # Expected registration timeline:
        # 1. Email Validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✓
        # 5. Pass 15-17 ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=17, months=7)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=17, months=2)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=17, months=1),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=birth_date,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=150_00,
            type="GRANT_15_17",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage"]')
        assert len(step_icon_views) == 5
        assert len(step_icon_titles) == 5
        assert len(text_views) == 5

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Ancien Pass 15-17"

    def test_registration_at_age16_after_decree(self, authenticated_client, settings):
        # Setup
        # - Sign-up at 16 or 15 after the decree started
        #
        # Expected registration timeline:
        # 1. Email validation ✓
        # 2. Not Eligible ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=16, months=7)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=15)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=16, months=1),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[],
            validatedBirthDate=birth_date,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="not-eligible"]')
        assert len(step_icon_views) == 2
        assert len(step_icon_titles) == 2
        assert len(text_views) == 2

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Non éligible"

    def test_registration_age_17_after_decree(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 17 after the decree started
        # - User is 17 years old now
        #
        # Expected registration timeline:
        # 1. Email validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✓
        # 5. Pass 17 ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=17, months=7)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=17, months=3)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=17, months=4),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=birth_date,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=50_00,
            type="GRANT_17_18",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="age-17"]')
        assert len(step_icon_views) == 5
        assert len(step_icon_titles) == 5
        assert len(text_views) == 5

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Pass 17"

    def test_registration_age_16_after_decree_current_age_17(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 16 after the decree started
        # - User is 17 years old now
        #
        # Expected registration timeline:
        # 1. Email validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✓
        # 5. Pass 17 ✓
        now = datetime.datetime.utcnow()
        birthdate = now - relativedelta(years=17, days=4)
        settings.CREDIT_V3_DECREE_DATETIME = birthdate + relativedelta(years=16, months=11, days=26)
        user = users_factories.UserFactory(
            dateCreated=birthdate + relativedelta(years=16, months=11, days=27),
            dateOfBirth=birthdate,
            phoneValidationStatus=None,
            roles=[],
            validatedBirthDate=birthdate,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="age-17"]')
        assert len(step_icon_views) == 5
        assert len(step_icon_titles) == 5
        assert len(text_views) == 5

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.SUSPICIOUS.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.VOID.value
        assert text_views[4].text == "Pass 17"

    def test_registration_age_15_before_decree_current_age_18(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 15 before the decree started
        # - Decree starts one day before the user's 18th birthday
        # - User is 18 years old now

        # Expected registration timeline:
        # 1. Email validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✓
        # 5. Pass 15-17 ✓
        # 6. Phone validation ✗
        # 7. Complete profile ✓
        # 8. ID check ✓
        # 9. Honor statement ✓
        # 10. Pass 18 ✓
        now = datetime.datetime.utcnow()
        birthdate = now - relativedelta(years=18, days=15)
        birthdate = birthdate.replace(hour=0, minute=0, second=0)
        settings.CREDIT_V3_DECREE_DATETIME = birthdate + relativedelta(years=18) - relativedelta(days=1)
        user = users_factories.UserFactory(
            dateCreated=birthdate + relativedelta(years=15, months=9, days=4),
            dateOfBirth=birthdate,
            phoneValidationStatus=None,
            roles=[users_models.UserRole.BENEFICIARY],
            validatedBirthDate=birthdate,
        )
        users_factories.DepositGrantFactory(
            dateCreated=user.dateCreated,
            user=user,
            amount=80_00,
            type="GRANT_15_17",
            expirationDate=settings.CREDIT_V3_DECREE_DATETIME + relativedelta(days=5),
        )
        users_factories.DepositGrantFactory(user=user, amount=151_15, type="GRANT_17_18")

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            dateCreated=user.dateCreated,
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            dateCreated=user.dateCreated,
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            dateCreated=user.dateCreated,
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage+age-18"]')
        assert len(step_icon_views) == 10
        assert len(step_icon_titles) == 10
        assert len(text_views) == 10

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Ancien Pass 15-17"

        assert step_icon_titles[5] == SubscriptionItemStatus.VOID.value
        assert text_views[5].text == "Validation N° téléphone"

        assert step_icon_titles[6] == SubscriptionItemStatus.OK.value
        assert text_views[6].text == "Profil Complet"

        assert step_icon_titles[7] == SubscriptionItemStatus.OK.value
        assert text_views[7].text == "ID Check"

        assert step_icon_titles[8] == SubscriptionItemStatus.OK.value
        assert text_views[8].text == "Attestation sur l'honneur"

        assert step_icon_titles[9] == SubscriptionItemStatus.OK.value
        assert text_views[9].text == "Pass 18"

    def test_registration_age_17_after_decree_current_age_18(self, authenticated_client, settings):
        # Setup:
        # - Decree starts at age 16
        # - Sign-up at 17 after the decree started
        # - User is 18 years old now
        #
        # Expected registration timeline:
        # 1. Email validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✓
        # 5. Pass 17 ✓
        # 6. Phone validation ✓
        # 7. Complete profile ✓
        # 8. ID check ✓
        # 9. Honor statement ✓
        # 10. Pass 18 ✓
        now = datetime.datetime.utcnow()
        date_of_birth = now - relativedelta(years=18, months=3)
        settings.CREDIT_V3_DECREE_DATETIME = date_of_birth + relativedelta(years=16)
        user = users_factories.UserFactory(
            dateCreated=date_of_birth + relativedelta(years=17, days=5),
            dateOfBirth=date_of_birth,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.BENEFICIARY],
            validatedBirthDate=date_of_birth,
        )
        users_factories.DepositGrantFactory(user=user, amount=150_00, type="GRANT_17_18")

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="age-17-18"]')
        assert len(step_icon_views) == 10
        assert len(step_icon_titles) == 10
        assert len(text_views) == 10

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Pass 17"

        assert step_icon_titles[5] == SubscriptionItemStatus.OK.value
        assert text_views[5].text == "Validation N° téléphone"

        assert step_icon_titles[6] == SubscriptionItemStatus.OK.value
        assert text_views[6].text == "Profil Complet"

        assert step_icon_titles[7] == SubscriptionItemStatus.OK.value
        assert text_views[7].text == "ID Check"

        assert step_icon_titles[8] == SubscriptionItemStatus.OK.value
        assert text_views[8].text == "Attestation sur l'honneur"

        assert step_icon_titles[9] == SubscriptionItemStatus.OK.value
        assert text_views[9].text == "Pass 18"

    def test_registration_age_17_decree_age_17_current_age_18(self, authenticated_client, settings):
        # Setup:
        # - Decree start at age 17
        # - Sign-up at 17 after the decree started
        # - User is 18 years old now
        #
        # Expected registration timeline:
        # 1. Email validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✗
        # 5. Pass 17 ✗
        # 6. Phone validation ✗
        # 7. Complete profile ✗
        # 8. ID check ✓
        # 9. Honor statement ✗
        # 10. Pass 18 ✗
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=18, days=10)
        settings.CREDIT_V3_DECREE_DATETIME = now - relativedelta(days=17)
        user = users_factories.UserFactory(
            dateCreated=now - relativedelta(days=14),
            dateOfBirth=birth_date,
            phoneValidationStatus=None,
            roles=[],
            validatedBirthDate=birth_date,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            dateCreated=user.dateCreated,
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            dateCreated=user.dateCreated,
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="age-17-18"]')
        assert len(step_icon_views) == 10
        assert len(step_icon_titles) == 10
        assert len(text_views) == 10

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.TODO.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.TODO.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.VOID.value
        assert text_views[4].text == "Pass 17"

        assert step_icon_titles[5] == SubscriptionItemStatus.TODO.value
        assert text_views[5].text == "Validation N° téléphone"

        assert step_icon_titles[6] == SubscriptionItemStatus.TODO.value
        assert text_views[6].text == "Profil Complet"

        assert step_icon_titles[7] == SubscriptionItemStatus.OK.value
        assert text_views[7].text == "ID Check"

        assert step_icon_titles[8] == SubscriptionItemStatus.TODO.value
        assert text_views[8].text == "Attestation sur l'honneur"

        assert step_icon_titles[9] == SubscriptionItemStatus.VOID.value
        assert text_views[9].text == "Pass 18"

    def test_registration_age_18_after_decree(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 18 after the decree started
        # - User is 18 years old now
        #
        # Expected registration timeline:
        # 1. Email validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✓
        # 5. Phone validation ✓
        # 6. Pass 18 ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=18, months=3)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=18, months=1, days=10)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=18, months=1, days=11),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.BENEFICIARY],
            validatedBirthDate=birth_date,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=150_00,
            type="GRANT_17_18",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Phone check
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="age-18"]')
        assert len(step_icon_views) == 6
        assert len(step_icon_titles) == 6
        assert len(text_views) == 6

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Validation N° téléphone"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "Profil Complet"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "ID Check"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Attestation sur l'honneur"

        assert step_icon_titles[5] == SubscriptionItemStatus.OK.value
        assert text_views[5].text == "Pass 18"

    def test_registration_age_18_before_decree(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 18 before the decree started
        # - User is 18 years old now
        #
        # Expected registration timeline:
        # 1. Email validation ✓
        # 2. Complete profile ✓
        # 3. ID check ✓
        # 4. Honor statement ✓
        # 5. Phone validation ✓
        # 6. Pass 18 ✓
        now = datetime.datetime.utcnow()
        birth_date = now - relativedelta(years=18, months=6)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=18, months=3)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=18, months=2),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.BENEFICIARY],
            validatedBirthDate=birth_date,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=30_00,
            type="GRANT_18",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Phone check
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="age-18-old"]')
        assert len(step_icon_views) == 6
        assert len(step_icon_titles) == 6
        assert len(text_views) == 6

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Validation N° téléphone"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "Profil Complet"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "ID Check"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Attestation sur l'honneur"

        assert step_icon_titles[5] == SubscriptionItemStatus.OK.value
        assert text_views[5].text == "Ancien Pass 18"

    def test_registration_age_15_long_before_decree_start(self, settings, authenticated_client):
        # Setup:
        # - Sign-up at 15
        # - At decree start → user is 19
        # - User is 20 years old now
        #
        # Expected registration timeline:
        #  1. Email validation ✓
        #  2. Complete profile ✓
        #  3. ID check ✓
        #  4. Honor statement ✓
        #  5. Pass 15-17 ✓
        #  6. Pass 17 ✓
        #  7. Phone validation ✓
        #  8. Complete profile ✓
        #  9. ID check ✓
        # 10. Honor statement ✓
        # 11. Pass 18 ✓
        now = datetime.datetime.utcnow()
        date_of_birth = now - relativedelta(years=20, months=3)
        settings.CREDIT_V3_DECREE_DATETIME = date_of_birth + relativedelta(years=19)
        user = users_factories.UserFactory(
            age=18,
            dateCreated=date_of_birth + relativedelta(years=15, days=5),
            dateOfBirth=date_of_birth,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.BENEFICIARY],
            validatedBirthDate=date_of_birth,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=30_00,
            type="GRANT_15_17",
            expirationDate=settings.CREDIT_V3_DECREE_DATETIME,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=150_00,
            type="GRANT_18",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="underage+age-18-old"]')
        assert len(step_icon_views) == 10
        assert len(step_icon_titles) == 10
        assert len(text_views) == 10

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Profil Complet"

        assert step_icon_titles[2] == SubscriptionItemStatus.OK.value
        assert text_views[2].text == "ID Check"

        assert step_icon_titles[3] == SubscriptionItemStatus.OK.value
        assert text_views[3].text == "Attestation sur l'honneur"

        assert step_icon_titles[4] == SubscriptionItemStatus.OK.value
        assert text_views[4].text == "Ancien Pass 15-17"

        assert step_icon_titles[5] == SubscriptionItemStatus.OK.value
        assert text_views[5].text == "Validation N° téléphone"

        assert step_icon_titles[6] == SubscriptionItemStatus.OK.value
        assert text_views[6].text == "Profil Complet"

        assert step_icon_titles[7] == SubscriptionItemStatus.OK.value
        assert text_views[7].text == "ID Check"

        assert step_icon_titles[8] == SubscriptionItemStatus.OK.value
        assert text_views[8].text == "Attestation sur l'honneur"

        assert step_icon_titles[9] == SubscriptionItemStatus.OK.value
        assert text_views[9].text == "Ancien Pass 18"

    def test_registration_wrong_birthdate(self, settings, authenticated_client):
        # Setup:
        # - Sign-up at 15
        # - At decree start → user is 19
        # - User is 20 years old now
        # - User's birthdate is not correct
        #
        # Expected registration timeline:
        #  1. Email validation ✓
        #  2. Not eligible ✓
        now = datetime.datetime.utcnow()
        birthdate = now + relativedelta(years=2, months=3)
        settings.CREDIT_V3_DECREE_DATETIME = now - relativedelta(days=5)
        user = users_factories.UserFactory(
            age=18,
            dateCreated=now - relativedelta(years=5),
            dateOfBirth=birthdate,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.BENEFICIARY],
            validatedBirthDate=birthdate,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=30_00,
            type="GRANT_15_17",
            expirationDate=settings.CREDIT_V3_DECREE_DATETIME,
        )
        users_factories.DepositGrantFactory(
            user=user,
            amount=150_00,
            type="GRANT_18",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)

        step_icon_views = soup.select(".steps .step-status-icon-container i")
        step_icon_titles = [e.attrs.get("title") for e in step_icon_views]
        text_views = soup.select(".steps .step-text")

        assert soup.select('[data-registration-steps-id="not-eligible"]')
        assert len(step_icon_views) == 2
        assert len(step_icon_titles) == 2
        assert len(text_views) == 2

        assert step_icon_titles[0] == SubscriptionItemStatus.OK.value
        assert text_views[0].text == "Validation Email"

        assert step_icon_titles[1] == SubscriptionItemStatus.OK.value
        assert text_views[1].text == "Non éligible"


@pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + datetime.timedelta(days=30))
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

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + relativedelta(years=1))
    @pytest.mark.parametrize(
        "dateCreated,dateOfBirth,tunnel_type",
        [
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                TunnelType.AGE18_OLD,
            ),
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1),
                TunnelType.UNDERAGE,
            ),
            (
                datetime.datetime.utcnow() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                TunnelType.UNDERAGE_AGE18_OLD,
            ),
        ],
    )
    def test_get_tunnel_type(self, dateCreated, dateOfBirth, tunnel_type):
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, dateCreated=dateCreated
        )

        user.add_beneficiary_role()
        users_factories.DepositGrantFactory(user=user)
        assert _get_tunnel_type(user) == tunnel_type

    @pytest.mark.parametrize(
        "dateCreated,dateOfBirth",
        [
            (
                datetime.datetime.utcnow(),
                None,
            ),
            (
                datetime.datetime.utcnow(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18 + 1, days=1),
            ),
        ],
    )
    def test_get_tunnel_type_non_eligible(self, dateCreated, dateOfBirth):
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, dateCreated=dateCreated
        )
        assert _get_tunnel_type(user) == TunnelType.NOT_ELIGIBLE

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + datetime.timedelta(days=3000))
    def test_get_subscription_item_status_by_eligibility_age18_old(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        now = datetime.datetime.utcnow()
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        user.add_beneficiary_role()

        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        assert len(subscription_item_status[EligibilityType.UNDERAGE.value]) == 0
        assert len(subscription_item_status[EligibilityType.AGE18.value]) > 0
        assert (
            subscription_item_status[EligibilityType.AGE18.value][SubscriptionStep.EMAIL_VALIDATION.value]
            == SubscriptionItemStatus.OK.value
        )

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + datetime.timedelta(days=3000))
    def test_get_subscription_item_status_by_eligibility_underage(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        now = datetime.datetime.utcnow()
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        user.add_beneficiary_role()

        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        assert len(subscription_item_status[EligibilityType.AGE18.value]) == 0
        assert len(subscription_item_status[EligibilityType.UNDERAGE.value]) > 0
        assert (
            subscription_item_status[EligibilityType.UNDERAGE.value][SubscriptionStep.EMAIL_VALIDATION.value]
            == SubscriptionItemStatus.OK.value
        )

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + datetime.timedelta(days=3000))
    def test_get_subscription_item_status_by_eligibility_underage_age18(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        now = datetime.datetime.utcnow()
        creation_date = now - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2)
        user = users_factories.UserFactory(
            dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=creation_date
        )
        user.add_beneficiary_role()

        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
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

    @pytest.mark.parametrize(
        "item_status_15_17,item_status_18,item_status_17_18",
        [
            (
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
                {},
                {},
            ),
            (
                {},
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
                {},
            ),
            (
                {},
                {},
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
            ),
            (
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
                {},
            ),
            (
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
                {},
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
            ),
            (
                {},
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
                {SubscriptionStep.EMAIL_VALIDATION.value: SubscriptionItemStatus.OK.value},
            ),
        ],
    )
    def test_get_steps_tunnel_unspecified(self, item_status_15_17, item_status_18, item_status_17_18):
        steps = _get_steps_tunnel_unspecified(item_status_15_17, item_status_18, item_status_17_18)
        assert len(steps) == 2

        assert steps[0].step_id == 1
        assert steps[0].description == SubscriptionStep.EMAIL_VALIDATION.value
        assert steps[0].icon == "bi-envelope-fill"
        assert steps[0].subscription_item_status == SubscriptionItemStatus.OK.value

        assert steps[1].step_id == 2
        assert steps[1].description == TunnelType.NOT_ELIGIBLE.value
        assert steps[1].icon == "bi-question-circle-fill"
        assert steps[1].subscription_item_status == SubscriptionItemStatus.OK.value

    def test_get_steps_tunnel_unspecified_pending_email_validation(self):
        steps = _get_steps_tunnel_unspecified({}, {}, {})
        assert len(steps) == 2

        assert steps[0].step_id == 1
        assert steps[0].description == SubscriptionStep.EMAIL_VALIDATION.value
        assert steps[0].icon == "bi-envelope-fill"
        assert steps[0].subscription_item_status == SubscriptionItemStatus.PENDING.value

        assert steps[1].step_id == 2
        assert steps[1].description == TunnelType.NOT_ELIGIBLE.value
        assert steps[1].icon == "bi-question-circle-fill"
        assert steps[1].subscription_item_status == SubscriptionItemStatus.PENDING.value

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

    def test_get_steps_tunnel_age18_old(self):
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

        steps = _get_steps_tunnel_age18_old(user, id_check_histories, item_status_18, fraud_reviews_desc)
        assert len(steps) == 6

        assert steps[0].step_id == 1
        assert steps[0].description == SubscriptionStep.EMAIL_VALIDATION.value

        assert steps[1].step_id == 2
        assert steps[1].description == SubscriptionStep.PHONE_VALIDATION.value

        assert steps[2].step_id == 3
        assert steps[2].description == SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[3].step_id == 4
        assert steps[3].description == SubscriptionStep.IDENTITY_CHECK.value
        assert len(steps[3].fraud_actions_history) == 2

        assert steps[4].step_id == 5
        assert steps[4].description == SubscriptionStep.HONOR_STATEMENT.value

        assert steps[5].step_id == 6
        assert steps[5].description == "Ancien Pass 18"

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() - relativedelta(years=1))
    def test_get_steps_tunnel_age18(self):
        user = users_factories.BeneficiaryFactory()
        eligibility_history = get_eligibility_history(user)
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_17_18 = subscription_item_status[EligibilityType.AGE17_18.value]

        steps = _get_steps_tunnel_age18(user, id_check_histories, item_status_17_18, fraud_reviews_desc)
        assert len(steps) == 6
        assert steps[0].step_id == 1
        assert steps[0].description == SubscriptionStep.EMAIL_VALIDATION.value

        assert steps[1].step_id == 2
        assert steps[1].description == SubscriptionStep.PHONE_VALIDATION.value

        assert steps[2].step_id == 3
        assert steps[2].description == SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[3].step_id == 4
        assert steps[3].description == SubscriptionStep.IDENTITY_CHECK.value

        assert steps[4].step_id == 5
        assert steps[4].description == SubscriptionStep.HONOR_STATEMENT.value

        assert steps[5].step_id == 6
        assert steps[5].description == "Pass 18"

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
        assert len(steps) == 5

        assert steps[0].step_id == 1
        assert steps[0].description == SubscriptionStep.EMAIL_VALIDATION.value

        assert steps[1].step_id == 2
        assert steps[1].description == SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[2].step_id == 3
        assert steps[2].description == SubscriptionStep.IDENTITY_CHECK.value
        assert len(steps[2].fraud_actions_history) == 1

        assert steps[3].step_id == 4
        assert steps[3].description == SubscriptionStep.HONOR_STATEMENT.value

        assert steps[4].step_id == 5
        assert steps[4].description == "Ancien Pass 15-17"

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
        assert len(steps) == 10

        assert steps[0].step_id == 1
        assert steps[0].description == SubscriptionStep.EMAIL_VALIDATION.value

        assert steps[1].step_id == 2
        assert steps[1].description == SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[2].step_id == 3
        assert steps[2].description == SubscriptionStep.IDENTITY_CHECK.value
        assert len(steps[2].fraud_actions_history) == 1

        assert steps[3].step_id == 4
        assert steps[3].description == SubscriptionStep.HONOR_STATEMENT.value

        assert steps[4].step_id == 5
        assert steps[4].description == EligibilityType.UNDERAGE.value

        assert steps[5].step_id == 6
        assert steps[5].description == SubscriptionStep.PHONE_VALIDATION.value

        assert steps[6].step_id == 7
        assert steps[6].description == SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[7].step_id == 8
        assert steps[7].description == SubscriptionStep.IDENTITY_CHECK.value

        assert steps[8].step_id == 9
        assert steps[8].description == SubscriptionStep.HONOR_STATEMENT.value

        assert steps[9].step_id == 10
        assert steps[9].description == EligibilityType.AGE18.value

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + datetime.timedelta(days=3000))
    def test_get_steps_for_tunnel_not_eligible(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18 + 1, days=1)
        now = datetime.datetime.utcnow()
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
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
        steps_to_compare = _get_steps_tunnel_unspecified(item_status_15_17, item_status_18, {})
        assert steps == steps_to_compare

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + relativedelta(years=1))
    def test_get_steps_for_tunnel_underage_age18(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        creation_date = datetime.datetime.utcnow() - relativedelta(
            years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2
        )
        user = users_factories.UserFactory(
            dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=creation_date
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

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
        steps_to_compare = _get_steps_tunnel_underage_age18_old(
            user, id_check_histories, item_status_15_17, item_status_18, fraud_reviews_desc
        )
        _set_steps_with_active_and_disabled(steps_to_compare)
        assert steps == steps_to_compare

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + relativedelta(years=1))
    def test_get_steps_for_tunnel_underage(self):
        now = datetime.datetime.utcnow()
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

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
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
        tunnel_type = _get_tunnel_type(user)
        steps = _get_steps_for_tunnel(
            user, tunnel_type, subscription_item_status, id_check_histories, fraud_reviews_desc
        )
        steps_to_compare = _get_steps_tunnel_underage(user, id_check_histories, item_status_15_17, fraud_reviews_desc)
        _set_steps_with_active_and_disabled(steps_to_compare)
        assert steps == steps_to_compare

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + relativedelta(years=1))
    def test_get_steps_for_tunnel_age18_old(self):
        now = datetime.datetime.utcnow()
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
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
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
        tunnel_type = _get_tunnel_type(user)

        steps = _get_steps_for_tunnel(
            user, tunnel_type, subscription_item_status, id_check_histories, fraud_reviews_desc
        )
        steps_to_compare = _get_steps_tunnel_age18_old(user, id_check_histories, item_status_18, fraud_reviews_desc)
        _set_steps_with_active_and_disabled(steps_to_compare)
        assert steps == steps_to_compare

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

        pass18_status_item = next((step for step in steps if step.description == "Ancien Pass 18"))
        assert len(pass18_status_item.fraud_actions_history) == 1
        assert pass18_status_item.fraud_actions_history[0]["status"] == fraud_models.FraudReviewStatus.OK.value

    def test_set_steps_with_active_and_disabled_underage_age18(self):
        creation_date = datetime.datetime.utcnow() - relativedelta(
            years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2
        )
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(
            dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=creation_date
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

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

        steps = _get_steps_tunnel_underage_age18(
            user, id_check_histories, item_status_15_17, item_status_18, fraud_reviews_desc
        )
        assert steps[8].status["active"] is False
        assert steps[9].status["disabled"] is False

        _set_steps_with_active_and_disabled(steps)

        assert steps[8].status["active"] is True
        assert steps[9].status["disabled"] is True

    def test_set_steps_with_active_and_disabled_underage(self):
        now = datetime.datetime.utcnow()
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

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
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)

        steps = _get_steps_tunnel_underage(user, id_check_histories, item_status_15_17, fraud_reviews_desc)
        assert steps[3].status["active"] is False
        assert steps[4].status["disabled"] is False

        _set_steps_with_active_and_disabled(steps)

        assert steps[3].status["active"] is True
        assert steps[4].status["disabled"] is True

    def test_set_steps_with_active_and_disabled_age18_old(self):
        now = datetime.datetime.utcnow()
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

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
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]
        id_check_histories = _get_id_check_histories_desc(eligibility_history)
        fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)

        steps = _get_steps_tunnel_age18_old(user, id_check_histories, item_status_18, fraud_reviews_desc)
        assert steps[4].status["active"] is False
        assert steps[5].status["disabled"] is False

        _set_steps_with_active_and_disabled(steps)

        assert steps[4].status["active"] is True
        assert steps[5].status["disabled"] is True

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.datetime.utcnow() + relativedelta(years=1))
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

        users_factories.DepositGrantFactory(user=user, type=finance_models.DepositType.GRANT_15_17)
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

        response = authenticated_client.get(response.location)
        assert "Les informations de l'utilisateur ont été anonymisées" in html_parser.extract_alert(response.data)

    def test_anonymize_public_account_with_gdpr_extract(
        self,
        legit_user,
        authenticated_client,
        storage_folder,
    ):
        user = users_factories.UserFactory(
            gdprUserDataExtract=[
                users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.today())
            ]
        )

        with open(storage_folder / f"{user.gdprUserDataExtract[0].id}.zip", "wb"):
            pass

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        assert user.roles == [users_models.UserRole.ANONYMIZED]

        assert users_models.GdprUserDataExtract.query.count() == 0
        assert len(os.listdir(storage_folder)) == 0

        response = authenticated_client.get(response.location)
        assert "Les informations de l'utilisateur ont été anonymisées" in html_parser.extract_alert(response.data)

    def test_anonymize_public_account_with_unprocessed_gdpr_extract(
        self,
        legit_user,
        authenticated_client,
    ):
        user = users_factories.UserFactory(
            gdprUserDataExtract=[users_factories.GdprUserDataExtractBeneficiaryFactory()]
        )

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        assert user.roles != [users_models.UserRole.ANONYMIZED]

        response = authenticated_client.get(response.location)
        assert "Une extraction de données est en cours pour cet utilisateur." in html_parser.extract_alert(
            response.data
        )

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

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, follow_redirects=True)
        assert response.status_code == 200

        db.session.refresh(user)
        assert not user.isActive
        assert users_models.GdprUserAnonymization.query.filter_by(userId=user.id).count() == 1
        assert "L'utilisateur a été suspendu et sera anonymisé le jour de ses 21 ans" in html_parser.extract_alert(
            response.data
        )

    def test_anonymize_public_account_when_user_is_too_young_and_already_pending(self, authenticated_client):
        user = users_factories.BeneficiaryFactory(
            isActive=False, validatedBirthDate=datetime.datetime.today() - datetime.timedelta(days=365 * 21)
        )
        users_factories.GdprUserAnonymizationFactory(user=user)

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, follow_redirects=True)
        assert response.status_code == 200

        assert (
            "L'utilisateur est déjà en attente pour être anonymisé le jour de ses 21 ans"
            in html_parser.extract_alert(response.data)
        )

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
            users_factories.BeneficiaryFactory,
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

    def test_anonymize_public_is_suspended_for_fraud(self, authenticated_client):
        user = users_factories.BeneficiaryFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=datetime.datetime.utcnow(),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.FRAUD_RESELL_PASS,
            user=user,
        )

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, follow_redirects=True)
        assert response.status_code == 200

        db.session.refresh(user)
        assert not user.isActive
        assert users_models.GdprUserAnonymization.query.filter_by(userId=user.id).count() == 1
        assert (
            "L'utilisateur sera anonymisé quand il aura plus de 21 ans et 5 ans après sa suspension pour fraude"
            in html_parser.extract_alert(response.data)
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.archive_application", return_value={})
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.mark_without_continuation", return_value={})
    def test_anonymize_public_account_with_user_account_update_request(
        self,
        mocked_mark_without_continuation,
        mocked_archive_application,
        legit_user,
        authenticated_client,
    ):
        user = users_factories.UserFactory()
        users_factories.PhoneNumberUpdateRequestFactory(user=user, status=dms_models.GraphQLApplicationStates.accepted)
        users_factories.FirstNameUpdateRequestFactory(user=user)

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 302

        assert user.roles == [users_models.UserRole.ANONYMIZED]

        mocked_mark_without_continuation.assert_called_once()
        mocked_archive_application.assert_called()
        assert mocked_archive_application.call_count == 2

        assert users_models.UserAccountUpdateRequest.query.count() == 0

        response = authenticated_client.get(response.location)
        assert "Les informations de l'utilisateur ont été anonymisées" in html_parser.extract_alert(response.data)


class ExtractPublicAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.create_extract_user_gdpr_data"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT

    expected_queries = 4  # session + user + targeted user with joined data + gdpr insert

    def test_extract_public_account(self, authenticated_client, legit_user):

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

    def test_extract_public_account_extract_data_already_exists(self, authenticated_client):
        gdpr_data_extract = users_factories.GdprUserDataExtractBeneficiaryFactory()

        response = self.post_to_endpoint(authenticated_client, user_id=gdpr_data_extract.user.id)
        assert response.status_code == 302

        response = authenticated_client.get(response.location)
        assert "Une extraction de données est déjà en cours pour cet utilisateur." in html_parser.extract_alert(
            response.data
        )

        assert 1 == users_models.GdprUserDataExtract.query.count()

    def test_extract_public_account_with_existing_extract_data_expired(self, authenticated_client, legit_user):
        expired_gdpr_data_extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=8)
        )

        response = self.post_to_endpoint(authenticated_client, user_id=expired_gdpr_data_extract.user.id)

        expected_url = url_for(
            "backoffice_web.public_accounts.get_public_account",
            user_id=expired_gdpr_data_extract.user.id,
            _external=True,
        )

        assert response.status_code == 302
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

    def test_extract_public_account_no_user_found(self, authenticated_client):

        response = self.post_to_endpoint(authenticated_client, user_id=42)
        assert response.status_code == 404


class InvalidatePublicAccountPasswordTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.invalidate_public_account_password"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    # session
    # user
    # targeted user by id
    # validate user
    # UPDATE user
    # INSERT actionhistory
    expected_queries = 6

    def test_invalidate_public_account_password(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryFactory()
        user_password_before_response = user.password

        response = self.post_to_endpoint(
            authenticated_client, user_id=user.id, expected_num_queries=self.expected_queries
        )
        assert response.status_code == 303

        assert user_password_before_response != user.password

        action_history = history_models.ActionHistory.query.one()
        assert action_history.actionType == history_models.ActionType.USER_PASSWORD_INVALIDATED
        assert action_history.authorUser == legit_user
        assert action_history.user == user

        response = authenticated_client.get(response.location)
        assert "Le mot de passe du compte a bien été invalidé" in html_parser.extract_alert(response.data)

    def test_invalidate_public_account_password_user_not_found(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, user_id=0)
        assert response.status_code == 404

    def test_invalidate_public_account_password_with_non_beneficiary_user(self, authenticated_client, legit_user):
        user = users_factories.ProFactory()

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        response = authenticated_client.get(response.location)
        assert (
            "Seul le mot de passe d'un compte bénéficiaire ou grand public peut être invalidé"
            in html_parser.extract_alert(response.data)
        )


class SendPublicAccountPasswordResetEmailTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.send_public_account_reset_password_email"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    # authenticated user session
    # authenticated user
    # targeted user by id
    expected_queries = 3

    def test_send_public_account_reset_password_email(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryFactory()
        user_password_before_response = user.password

        response = self.post_to_endpoint(
            authenticated_client, user_id=user.id, expected_num_queries=self.expected_queries
        )
        assert response.status_code == 303

        assert user_password_before_response == user.password

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.NEW_PASSWORD_REQUEST.value.__dict__
        assert "2Fmot-de-passe-perdu%3Ftoken%3" in mails_testing.outbox[0]["params"]["RESET_PASSWORD_LINK"]

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == "L'envoi du mail de changement de mot de passe a été initié"

    def test_user_not_found(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, user_id=0)
        assert response.status_code == 404

    def test_with_non_beneficiary_user(self, authenticated_client, legit_user):
        user = users_factories.ProFactory()

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "La fonctionnalité n'est disponible que pour un compte bénéficiaire ou grand public"
        )
