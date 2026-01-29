import dataclasses
import datetime
import decimal
import os
import re
from unittest.mock import patch

import pytest
import pytz
from dateutil.relativedelta import relativedelta
from flask import url_for

from pcapi import settings as pcapi_settings
from pcapi.connectors.dms import models as dms_models
from pcapi.core import token as token_utils
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.operations import factories as operations_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.core.users.models import EligibilityType
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.feature import DisabledFeatureError
from pcapi.notifications.sms import testing as sms_testing
from pcapi.routes.backoffice.accounts.blueprint import RegistrationStep
from pcapi.routes.backoffice.accounts.blueprint import RegistrationStepStatus
from pcapi.routes.backoffice.accounts.blueprint import TunnelType
from pcapi.routes.backoffice.accounts.blueprint import _get_id_check_histories_desc
from pcapi.routes.backoffice.accounts.blueprint import _get_progress
from pcapi.routes.backoffice.accounts.blueprint import _get_status
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_for_tunnel
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_age18
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_age18_old
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_tunnel_bonus_credit
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
from pcapi.utils import countries as countries_utils
from pcapi.utils import date as date_utils
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


def user_id_from_card(card_text: str) -> int | None:
    match = re.search(r"User ID : (?P<user_id>\d+)", card_text)
    return match.groupdict().get("user_id") if match else None


class SearchPublicAccountsTest(search_helpers.SearchHelper, GetEndpointHelper):
    endpoint = "backoffice_web.public_accounts.search_public_accounts"
    needed_permission = perm_models.Permissions.READ_PUBLIC_ACCOUNT

    # session + user tags
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

    def test_can_search_public_account_by_credit_type_only(self, authenticated_client, settings):
        users_factories.BeneficiaryGrant18Factory(
            deposit__dateCreated=settings.CREDIT_V3_DECREE_DATETIME - relativedelta(years=1),
        )
        new_grant_18 = users_factories.BeneficiaryFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, filter="PASS_18_V3"))
            assert response.status_code == 303

        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=new_grant_18.id,
            filter="PASS_18_V3",
            search_rank=1,
            total_items=1,
        )

    def test_can_search_public_account_by_tag(self, authenticated_client):
        tag = users_factories.UserTagFactory(name="ambassador")
        tag_id = tag.id
        user_with_tag = users_factories.BeneficiaryGrant18Factory(tags=[tag])
        users_factories.BeneficiaryFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, tag=tag_id))
            assert response.status_code == 303

        assert_response_location(
            response,
            "backoffice_web.public_accounts.get_public_account",
            user_id=user_with_tag.id,
            tag=tag_id,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_public_account_by_mulitple_tags(self, authenticated_client):
        tag1, tag2, tag3 = users_factories.UserTagFactory.create_batch(3)
        tag1_id = tag1.id
        tag2_id = tag2.id
        user_with_tag1 = users_factories.BeneficiaryGrant18Factory(tags=[tag1])
        user_with_tag1_and_tag2 = users_factories.BeneficiaryGrant18Factory(tags=[tag1, tag2])
        user_with_tag2 = users_factories.BeneficiaryGrant18Factory(tags=[tag2])
        users_factories.BeneficiaryGrant18Factory(tags=[tag3])  # user with tag3
        users_factories.BeneficiaryGrant18Factory(tags=[])  # user with no tags

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, tag=[tag1_id, tag2_id]))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 3
        user_ids = {user_id_from_card(card_text) for card_text in cards_text}
        assert user_ids == {str(user_with_tag1.id), str(user_with_tag1_and_tag2.id), str(user_with_tag2.id)}

    def test_can_search_public_account_having_mulitple_tags(self, authenticated_client):
        tag1, tag2, tag3 = users_factories.UserTagFactory.create_batch(3)
        tag1_id = tag1.id
        user_with_tag1 = users_factories.BeneficiaryGrant18Factory(tags=[tag1])
        user_with_tag1_and_tag2 = users_factories.BeneficiaryGrant18Factory(tags=[tag1, tag2])
        users_factories.BeneficiaryGrant18Factory(tags=[tag2])  # user with tag2
        users_factories.BeneficiaryGrant18Factory(tags=[tag3])  # user with tag3
        users_factories.BeneficiaryGrant18Factory(tags=[])  # user with no tags

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, tag=tag1_id))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2
        user_ids = {user_id_from_card(card_text) for card_text in cards_text}
        assert user_ids == {str(user_with_tag1.id), str(user_with_tag1_and_tag2.id)}

    def test_can_search_public_account_by_tags_and_query(self, authenticated_client):
        tag1, tag2, tag3 = users_factories.UserTagFactory.create_batch(3)
        tag2_id = tag2.id
        users_factories.BeneficiaryGrant18Factory(tags=[tag1], firstName="jean")  # user1
        user2 = users_factories.BeneficiaryGrant18Factory(tags=[tag1, tag2], firstName="jean")
        users_factories.BeneficiaryGrant18Factory(tags=[tag2], firstName="jacques")  # user3
        user4 = users_factories.BeneficiaryGrant18Factory(tags=[tag2], firstName="jean")
        users_factories.BeneficiaryGrant18Factory(tags=[], firstName="jean")  # user5

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, tag=tag2_id, q="jean"))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2
        user_ids = {user_id_from_card(card_text) for card_text in cards_text}
        assert user_ids == {str(user2.id), str(user4.id)}

    def test_display_accounts_tags(self, authenticated_client):
        tag1 = users_factories.UserTagFactory(label="Tag 1")
        tag2 = users_factories.UserTagFactory(name="tag-2")
        tag3 = users_factories.UserTagFactory(label="Tag 3")
        user1 = users_factories.UserFactory(tags=[tag1, tag2], firstName="jean", lastName="un")
        user2 = users_factories.UserFactory(tags=[tag3], firstName="jean", lastName="deux")
        users_factories.UserFactory(tags=[], firstName="robert", lastName="trois")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="jean"))
            assert response.status_code == 200

        soup = html_parser.get_soup(response.data)
        cards = soup.find_all(class_="card")
        assert len(cards) == 2

        user_ids = {user_id_from_card(html_parser.filter_whitespaces(card.text)) for card in cards}
        assert user_ids == {str(user1.id), str(user2.id)}
        card1 = [c for c in cards if user_id_from_card(html_parser.filter_whitespaces(c.text)) == str(user1.id)][0]
        card2 = [c for c in cards if user_id_from_card(html_parser.filter_whitespaces(c.text)) == str(user2.id)][0]

        card1_badges = html_parser.extract_badges(card1.encode())
        card2_badges = html_parser.extract_badges(card2.encode())
        assert set(card1_badges) == {"Tag 1", "tag-2"}
        assert set(card2_badges) == {"Tag 3"}

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
        now = date_utils.get_naive_utc_now()
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
    def test_search_with_single_filter(self, authenticated_client, search_filter, expected_user):
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
    # user session
    # user and joinedload data
    # 8 x subqueryload for additional user data
    # check if user is waiting to be anonymized
    # user tags (for tag account form display)
    expected_num_queries = 12

    class ReviewButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.BENEFICIARY_MANUAL_REVIEW
        button_label = "Revue manuelle"

        @property
        def path(self):
            user = users_factories.UserFactory()
            return url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

    class BonusCreditButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.REQUEST_BENEFICIARY_BONUS_CREDIT
        button_label = "Demander la bonification"

        @property
        def path(self):
            user = users_factories.BeneficiaryFactory()
            return url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

        @pytest.mark.parametrize(
            "user_factory",
            [
                users_factories.UnderageBeneficiaryFactory,
                users_factories.FreeBeneficiaryFactory,
                users_factories.UserFactory,
                users_factories.ProFactory,
            ],
        )
        def test_no_button_when_not_eligible(self, authenticated_client, user_factory):
            user = user_factory()

            response = authenticated_client.get(
                url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
            )

            assert response.status_code == 200
            assert self.button_label not in response.data.decode("utf-8")

        def test_no_button_when_bonus_granted(self, authenticated_client):
            user = users_factories.BeneficiaryFactory()
            subscription_factories.BonusFraudCheckFactory(user=user)
            finance_factories.RecreditFactory(
                deposit=user.deposit, recreditType=finance_models.RecreditType.BONUS_CREDIT
            )

            response = authenticated_client.get(
                url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
            )

            assert response.status_code == 200
            assert self.button_label not in response.data.decode("utf-8")

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

    class TagPublicAccountButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_TAGS
        button_label = "Taguer"

        @property
        def path(self):
            user = users_factories.UserFactory()
            return url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

    @pytest.mark.parametrize("index,expected_badge", [(0, "Pass 17"), (1, "Ancien Pass 18"), (2, "Pass 18"), (3, None)])
    def test_get_public_account(self, authenticated_client, index, expected_badge):
        users = create_bunch_of_accounts()
        user = users[index]

        user_id = user.id
        expected_num_queries = self.expected_num_queries
        if index != 3:
            # check if user should update their account
            expected_num_queries += 1
        with assert_num_queries(expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"User ID : {user.id} " in content
        assert f"Email : {user.email} " in content
        assert f"Tél : {user.phoneNumber} " in content
        if user.dateOfBirth:
            assert f"Date de naissance : {user.dateOfBirth.strftime('%d/%m/%Y')}" in content
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

    def test_get_public_account_with_unconfirmed_modified_email(self, authenticated_client):
        user = users_factories.UserFactory()
        users_factories.EmailUpdateEntryFactory(user=user)
        users_factories.EmailConfirmationEntryFactory(user=user)
        users_factories.NewEmailSelectionEntryFactory(user=user)
        user_id = user.id

        with assert_num_queries(self.expected_num_queries):
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

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)
        assert parsed_html.find("i", class_="pc-email-changed-icon") is not None

    def test_get_public_account_with_admin_modified_email(self, authenticated_client):
        user = users_factories.UserFactory()
        users_factories.EmailAdminUpdateEntryFactory(user=user)
        user_id = user.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)
        assert parsed_html.find("i", class_="pc-email-changed-icon") is not None

    @pytest.mark.parametrize(
        "reasonCodes,reason",
        (
            (
                [subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER],
                "La pièce d'identité n°{id_piece_number} est déjà prise par l'utilisateur {original_user_id}",
            ),
            ([subscription_models.FraudReasonCode.DUPLICATE_USER], "Duplicat de l'utilisateur {original_user_id}"),
        ),
    )
    def test_get_public_account_with_resolved_duplicate(self, authenticated_client, reasonCodes, reason):
        first_name = "Jack"
        last_name = "Sparrow"
        email = "jsparrow@pirate.mail"
        birth_date = date_utils.get_naive_utc_now() - relativedelta(years=18, days=15)
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

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=reasonCodes,
            reason=reason,
            resultContent=subscription_factories.UbbleContentFactory(
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date.date().isoformat(),
                id_document_number=id_piece_number,
            ),
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=duplicate_user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        duplicate_user_id = duplicate_user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=duplicate_user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"User ID doublon : {original_user.id}" in content

    def test_get_public_account_birth_dates(self, authenticated_client):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=15),
            validatedBirthDate=date_utils.get_naive_utc_now() - relativedelta(years=17, days=15),
        )
        user_id = user.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"Date de naissance : {user.validatedBirthDate.strftime('%d/%m/%Y')} " in content
        assert f"Date de naissance déclarée à l'inscription : {user.dateOfBirth.strftime('%d/%m/%Y')} " in content

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
                "137,50 € (16410 CFP) Crédit restant 150,00 € (17900 CFP)",
                "87,50 € (10440 CFP) Crédit digital restant 100,00 € (11935 CFP)",
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
        # check if user should update their account
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        # Remaining credit + Title + Initial Credit
        assert expected_remaining_text in cards_text
        assert expected_digital_remaining_text in cards_text

    @pytest.mark.parametrize(
        "postal_code,expected_text",
        [
            ("97200", "0,00 € Crédit restant 0,00 €"),
            ("98800", "0,00 € (0 CFP) Crédit restant 0,00 € (0 CFP)"),
        ],
    )
    def test_get_grant_free_credit_does_not_divide_by_zero(self, authenticated_client, postal_code, expected_text):
        free_beneficiary = users_factories.UserFactory(
            roles=[users_models.UserRole.FREE_BENEFICIARY], postalCode=postal_code
        )
        users_factories.DepositGrantFactory(
            user=free_beneficiary, type=finance_models.DepositType.GRANT_FREE, amount=decimal.Decimal("0")
        )

        user_id = free_beneficiary.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))

        assert response.status_code == 200
        assert expected_text in html_parser.extract_cards_text(response.data)

    def test_get_non_beneficiary_credit(self, authenticated_client):
        _, _, _, _, random, _ = create_bunch_of_accounts()
        user_id = random.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert "Crédit restant" not in html_parser.content_as_text(response.data)

    @pytest.mark.parametrize(
        "user_factory,expected_price_1,expected_price_2",
        [
            (users_factories.BeneficiaryFactory, "20,00 €", "12,50 €"),
            (users_factories.CaledonianBeneficiaryFactory, "20,00 € (2385 CFP)", "12,50 € (1490 CFP)"),
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
            stock__offer__withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        b2 = bookings_factories.UsedBookingFactory(user=user, amount=20)
        bookings_factories.FraudulentBookingTagFactory(booking=b2)
        bookings_factories.UsedBookingFactory()

        user_id = user.id
        # check if user should update their account
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        bookings = html_parser.extract_table_rows(response.data, parent_class="bookings-tab-pane")
        assert len(bookings) == 2

        assert bookings[0]["Offreur"] == b2.offerer.name
        assert bookings[0]["Nom de l'offre"] == b2.stock.offer.name
        assert bookings[0]["Prix"] == expected_price_1
        assert bookings[0]["Date de résa"].startswith(datetime.date.today().strftime("%d/%m/%Y"))
        assert bookings[0]["État"] == "Le jeune a consommé l'offre"
        assert bookings[0]["Contremarque"] == b2.token
        assert bookings[0]["Fraude"] == "Frauduleuse"
        assert bookings[0]["Modalités de retrait"] == ""

        assert bookings[1]["Offreur"] == b1.offerer.name
        assert bookings[1]["Nom de l'offre"] == b1.stock.offer.name
        assert bookings[1]["Prix"] == expected_price_2
        assert bookings[1]["Date de résa"].startswith(
            (datetime.date.today() - relativedelta(days=2)).strftime("%d/%m/%Y")
        )
        assert bookings[1]["État"] == "L'offre n'a pas eu lieu"
        assert bookings[1]["Contremarque"] == b1.token
        assert bookings[1]["Fraude"] == ""
        assert bookings[1]["Modalités de retrait"] == "Dans l'app"

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
        # check if user should update their account
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert not html_parser.extract_table_rows(response.data, parent_class="bookings-tab-pane")
        assert "Aucune réservation à ce jour" in response.data.decode("utf-8")

    def test_fraud_check_link(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        # modifiy the date for clearer tests
        old_dms = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.DMS,
            dateCreated=date_utils.get_naive_utc_now() + datetime.timedelta(days=2),
        )

        user_id = user.id
        # check if user should update their account
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)

        main_dossier_card = str(
            parsed_html.find("div", class_="pc-script-user-accounts-additional-data-main-fraud-check")
        )
        assert (
            f"https://demarche.numerique.gouv.fr/procedures/{old_dms.source_data().procedure_number}/dossiers/{old_dms.thirdPartyId}"
            in main_dossier_card
        )

        new_dms = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.DMS,
            dateCreated=date_utils.get_naive_utc_now() + datetime.timedelta(days=3),
        )

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))

        parsed_html = html_parser.get_soup(response.data)
        main_dossier_card = str(
            parsed_html.find("div", class_="pc-script-user-accounts-additional-data-main-fraud-check")
        )
        assert (
            f"https://demarche.numerique.gouv.fr/procedures/{new_dms.source_data().procedure_number}/dossiers/{new_dms.thirdPartyId}"
            in main_dossier_card
        )

    def test_get_public_account_history(self, legit_user, authenticated_client):
        # More than 30 days ago to have deterministic order because "Import ubble" is generated randomly between
        # -30 days and -1 day in BeneficiaryImportStatusFactory
        user = users_factories.BeneficiaryFactory(dateCreated=date_utils.get_naive_utc_now() - relativedelta(days=40))
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
            actionDate=date_utils.get_naive_utc_now() - relativedelta(days=35),
            user=user,
            authorUser=admin,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.INFO_MODIFIED,
            actionDate=date_utils.get_naive_utc_now() - relativedelta(days=30),
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
        db.session.add(no_date_action)
        db.session.commit()

        user_id = user.id
        # check if user should update their account
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert response.status_code == 200
        history_rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(history_rows) == 9

        assert history_rows[0]["Type"] == "Étape de vérification"
        assert history_rows[0]["Date/Heure"].startswith(datetime.date.today().strftime("%d/%m/%Y à"))
        assert history_rows[0]["Commentaire"] == "honor_statement, age-17-18, ok, raison inconnue, None"
        assert not history_rows[0]["Auteur"]

        assert history_rows[1]["Type"] == "Étape de vérification"
        assert history_rows[1]["Date/Heure"].startswith(datetime.date.today().strftime("%d/%m/%Y à"))
        assert history_rows[1]["Commentaire"] == "ubble, age-17-18, ok, raison inconnue, None"
        assert not history_rows[1]["Auteur"]

        assert history_rows[2]["Type"] == "Étape de vérification"
        assert history_rows[2]["Date/Heure"].startswith(datetime.date.today().strftime("%d/%m/%Y à"))
        assert history_rows[2]["Commentaire"] == "profile_completion, age-17-18, ok, raison inconnue, None"
        assert not history_rows[2]["Auteur"]

        assert history_rows[3]["Type"] == "Étape de vérification"
        assert history_rows[3]["Date/Heure"].startswith(datetime.date.today().strftime("%d/%m/%Y à"))
        assert history_rows[3]["Commentaire"] == "phone_validation, age-17-18, ok, raison inconnue, None"
        assert not history_rows[3]["Auteur"]

        assert history_rows[4]["Type"] == "Modification des informations"
        assert history_rows[4]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=30)).strftime("%d/%m/%Y à ")
        )
        assert history_rows[4]["Commentaire"].startswith("Informations modifiées :")
        assert "Nom : Pignon → Leblanc" in history_rows[4]["Commentaire"]
        assert "Prénom : suppression de : François" in history_rows[4]["Commentaire"]
        assert "Date de naissance : 2001-04-14 → 2000-09-19" in history_rows[4]["Commentaire"]
        assert history_rows[4]["Auteur"] == admin.full_name

        assert history_rows[5]["Type"] == "Compte réactivé"
        assert history_rows[5]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=35)).strftime("%d/%m/%Y à ")
        )
        assert history_rows[5]["Commentaire"] == unsuspended.comment
        assert history_rows[5]["Auteur"] == admin.full_name

        assert history_rows[6]["Type"] == "Création du compte"
        assert history_rows[6]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=40)).strftime("%d/%m/%Y à ")
        )
        assert not history_rows[6]["Commentaire"]
        assert history_rows[6]["Auteur"] == user.full_name

        assert history_rows[7]["Type"] == "Attribution d'un crédit"
        assert history_rows[7]["Date/Heure"].startswith(
            (datetime.date.today() - relativedelta(days=40)).strftime("%d/%m/%Y à ")
        )
        assert history_rows[7]["Commentaire"] == "Attribution d'un crédit 17-18 de 150,00 €"

        assert history_rows[8]["Type"] == "Compte suspendu"
        assert not history_rows[8]["Date/Heure"]  # Empty date, at the end of the list
        assert history_rows[8]["Commentaire"].startswith("Fraude suspicion")
        assert history_rows[8]["Auteur"] == legit_user.full_name

    @pytest.mark.parametrize(
        "bo_role, expected_bonus_code, has_bonus_details",
        [
            (perm_models.Roles.SUPPORT_N2, subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH.value, True),
            (perm_models.Roles.SUPPORT_N1, "", False),
            (perm_models.Roles.LECTURE_SEULE, "", False),
        ],
    )
    def test_get_public_account_subscription_table(
        self, legit_user, client, bo_role, expected_bonus_code, has_bonus_details
    ):
        bo_user = users_factories.AdminFactory()
        backoffice_api.upsert_roles(bo_user, [bo_role])

        user = users_factories.BeneficiaryFactory(dateCreated=date_utils.get_naive_utc_now() - relativedelta(days=40))
        subscription_factories.BonusFraudCheckFactory(
            user=user,
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=[subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH],
        )
        user_id = user.id

        client = client.with_bo_session_auth(bo_user)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data, parent_class="registration-workflow-tab-pane")
        assert len(rows) == 5

        assert rows[0]["Type"] == subscription_models.FraudCheckType.QF_BONUS_CREDIT.value
        assert rows[0]["Statut"] == "KO"
        assert rows[0]["Explication"] == ""
        assert rows[0]["Code d'erreur"] == expected_bonus_code
        assert bool(rows[0]["Détails techniques"]) is has_bonus_details

        assert rows[2]["Type"] == subscription_models.FraudCheckType.UBBLE.value
        assert rows[2]["Statut"] == "OK"
        assert "reference_data_check_score" in rows[2]["Détails techniques"]

    def test_get_public_account_anonymized_user(self, authenticated_client):
        user = users_factories.UserFactory(roles=[users_models.UserRole.ANONYMIZED])

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert f"User ID : {user.id} " in content

        available_button = html_parser.extract(response.data, tag="button")
        assert "Anonymiser" not in available_button

    def test_get_pulic_account_tags(self, authenticated_client):
        tag1 = users_factories.UserTagFactory(label="Ambassadeur A")
        tag2 = users_factories.UserTagFactory(label="Ambassadeur B")
        user = users_factories.UserFactory(tags=[tag1, tag2])
        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        badges = html_parser.extract_badges(response.data)
        assert {"Ambassadeur A", "Ambassadeur B"}.intersection(badges) == {"Ambassadeur A", "Ambassadeur B"}

    def test_get_beneficiary_with_expired_address(self, authenticated_client):
        campaign_date = date_utils.get_naive_utc_now() + relativedelta(days=30)
        users_factories.UserProfileRefreshCampaignFactory(campaignDate=campaign_date)
        before_profile_expiry_date = campaign_date - relativedelta(days=1)
        user = users_factories.BeneficiaryFactory.create(beneficiaryFraudChecks__dateCreated=before_profile_expiry_date)

        user_id = user.id
        # check if user should update their account
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert "Informations expirées".encode("utf-8") in response.data


class GetUserActivityTest(GetEndpointHelper):
    endpoint = "backoffice_web.public_accounts.get_public_account_activity"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PUBLIC_ACCOUNT

    # - session + authenticated user (1 queries)
    # - special events (1 query)
    # - chronicles (1 query)
    expected_num_queries = 3

    def test_get_beneficiary_activity(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        first_chronicle = chronicles_factories.ChronicleFactory(
            user=user,
            productIdentifier="9782370730541",
            isSocialMediaDiffusible=False,
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=3),
            products=[offers_factories.ProductFactory(ean="9782370730541", name="Le Backoffice pour les nuls")],
        )

        special_event_response = operations_factories.SpecialEventResponseFactory(
            user=user,
            dateSubmitted=date_utils.get_naive_utc_now() - datetime.timedelta(days=2),
            event__title="Jeu concours",
        )
        last_chronicle = chronicles_factories.ChronicleFactory(
            user=user,
            productIdentifier="12345678954321",
            isActive=True,
            isSocialMediaDiffusible=True,
            dateCreated=date_utils.get_naive_utc_now(),
        )

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        activity = html_parser.extract_table_rows(response.data)
        assert len(activity) == 3

        assert activity[0]["Type d'activité"] == "Chronique"
        assert activity[0]["Date"].startswith(last_chronicle.dateCreated.strftime("%d/%m/%Y"))
        assert activity[0]["Commentaire"] == "Rédaction d'une chronique sur 12345678954321 : publiée"

        assert activity[1]["Type d'activité"] == "Opération spéciale"
        assert activity[1]["Date"].startswith(special_event_response.dateSubmitted.strftime("%d/%m/%Y"))
        assert activity[1]["Commentaire"] == "Candidature à l'opération spéciale Jeu concours : Nouvelle"

        assert activity[2]["Type d'activité"] == "Chronique"
        assert activity[2]["Date"].startswith(first_chronicle.dateCreated.strftime("%d/%m/%Y"))
        assert activity[2]["Commentaire"] == "Rédaction d'une chronique sur Le Backoffice pour les nuls : non publiée"

    def test_get_beneficiary_activity_empty(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert not html_parser.extract_table_rows(response.data)
        assert "Aucune activité à ce jour" in response.data.decode("utf-8")


class UpdatePublicAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.update_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_update_field(self, legit_user, authenticated_client):
        user = users_factories.BeneficiaryFactory(postalCode="29000")
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
            "backoffice_web.public_accounts.get_public_account", user_id=user.id, active_tab="history"
        )
        assert response.location == expected_url

        user = db.session.query(users_models.User).filter_by(id=user.id).one()
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

        action = db.session.query(history_models.ActionHistory).one()
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
            "backoffice_web.public_accounts.get_public_account", user_id=user.id, active_tab="history"
        )
        assert response.location == expected_url

        user = db.session.query(users_models.User).filter_by(id=user.id).one()
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

        action = db.session.query(history_models.ActionHistory).one()
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

        user = db.session.query(users_models.User).filter_by(id=user.id).one()
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
        email_history: list[users_models.UserEmailHistory] = (
            db.session.query(users_models.UserEmailHistory)
            .filter(users_models.UserEmailHistory.userId == user.id)
            .all()
        )
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

        user_to_edit = db.session.query(users_models.User).filter_by(id=user_to_edit.id).one()
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
            == f"Le numéro de pièce d'identité {other_user.idPieceNumber} est déjà associé à un autre compte utilisateur."
        )

        assert user.idPieceNumber != other_user.idPieceNumber
        assert db.session.query(history_models.ActionHistory).count() == 0

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

        user_to_edit = db.session.query(users_models.User).filter_by(id=user_to_edit.id).one()
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

        user_to_edit = db.session.query(users_models.User).filter_by(id=user_to_edit.id).one()
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
        updated_user: users_models.User = db.session.query(users_models.User).filter_by(id=user.id).one()
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
        assert (
            db.session.query(history_models.ActionHistory).filter(history_models.ActionHistory.user == user).count()
            == 1
        )
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
            side_effect=users_exceptions.InvalidEligibilityTypeException("Test"),
        ):
            response = self.post_to_endpoint(authenticated_client, user_id=user.id, follow_redirects=True)

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == "Une erreur s'est produite : Test"

        db.session.refresh(user)
        assert not user.is_phone_validated
        assert not user.roles
        assert not user.deposits
        assert db.session.query(history_models.ActionHistory).count() == 0
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
            (date_utils.get_naive_utc_now() + users_constants.PHONE_VALIDATION_TOKEN_LIFE_TIME).timestamp(),
            1,
        )

    def test_phone_validation_code_sending_ignores_limit(self, authenticated_client):
        user = users_factories.UserFactory(phoneValidationStatus=None, phoneNumber="+33612345678")

        with patch("pcapi.core.subscription.phone_validation.sending_limit.is_SMS_sending_allowed") as limit_mock:
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
            "status": subscription_models.FraudReviewStatus.KO.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert response.location == expected_url

        user = db.session.query(users_models.User).filter_by(id=user.id).one()

        assert len(user.beneficiaryFraudReviews) == 1
        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.author == legit_user
        assert fraud_review.review == subscription_models.FraudReviewStatus.KO
        assert fraud_review.reason == "test"

        assert user.has_beneficiary_role is False

    def test_set_beneficiary_on_underage(self, authenticated_client, legit_user, settings):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        user = users_factories.BeneficiaryFactory(age=16, dateCreated=before_decree)

        base_form = {
            "status": subscription_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert response.location == expected_url

        user = db.session.query(users_models.User).filter_by(id=user.id).one()

        assert len(user.beneficiaryFraudReviews) == 1
        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.author == legit_user
        assert fraud_review.review == subscription_models.FraudReviewStatus.OK
        assert fraud_review.reason == "test"

        assert user.has_beneficiary_role is True

        deposits = (
            db.session.query(finance_models.Deposit)
            .filter(finance_models.Deposit.userId == user.id)
            .order_by(finance_models.Deposit.dateCreated)
            .all()
        )

        assert len(deposits) == 2
        assert deposits[0].expirationDate < date_utils.get_naive_utc_now()
        assert deposits[0].amount < 300
        assert deposits[1].expirationDate > date_utils.get_naive_utc_now()
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

        user = db.session.query(users_models.User).filter_by(id=user.id).one()
        assert not user.deposits

    def test_reason_not_compulsory(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()

        base_form = {
            "status": subscription_models.FraudReviewStatus.KO.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert response.location == expected_url

        user = db.session.query(users_models.User).filter_by(id=user.id).one()

        assert len(user.deposits) == 1
        assert len(user.beneficiaryFraudReviews) == 1

        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.reason is None

    def test_missing_identity_fraud_check_filled(self, authenticated_client):
        # not a beneficiary, does not have any identity fraud check
        # filled by default.
        user_id = users_factories.UserFactory().id

        base_form = {
            "status": subscription_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=base_form)
        assert response.status_code == 303

        user = db.session.query(users_models.User).filter_by(id=user_id).one()
        assert not user.deposits

    def test_accepte_underage_beneficiary_already_beneficiary(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()

        base_form = {
            "status": subscription_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.UNDERAGE.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303
        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert response.location == expected_url

        user = db.session.query(users_models.User).filter_by(id=user.id).one()
        assert len(user.beneficiaryFraudReviews) == 0
        assert user.roles == [users_models.UserRole.BENEFICIARY]

        response = authenticated_client.get(response.location)
        assert (
            "Le compte est déjà majeur (18+) il ne peut pas aussi être bénéficiaire (15-17)"
            in html_parser.extract_alert(response.data)
        )

    def test_underage_eligibility_when_eighteen(self, authenticated_client):
        user = users_factories.IdentityValidatedUserFactory(age=18)

        base_form = {
            "status": subscription_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.UNDERAGE.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303
        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert response.location == expected_url

        user = db.session.query(users_models.User).filter_by(id=user.id).one()
        assert len(user.beneficiaryFraudReviews) == 0
        assert user.roles == []

        response = authenticated_client.get(response.location)
        assert (
            "Le compte est déjà majeur (18+) il ne peut pas aussi être bénéficiaire (15-17)"
            in html_parser.extract_alert(response.data)
        )

    def test_pre_decree_eligibility_when_beneficiary_of_post_decree_credit(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()

        base_form = {
            "status": subscription_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            "Le compte est déjà bénéficiaire du Pass 17-18, il ne peut pas aussi être bénéficiaire de l'ancien Pass 15-17 ou 18"
            in html_parser.extract_alert(response.data)
        )

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now())
    def test_post_decree_eligibility_when_beneficiary_of_pre_decree_credit(self, authenticated_client):
        year_when_user_was_eighteen = date_utils.get_naive_utc_now() - relativedelta(years=1)
        user = users_factories.HonorStatementValidatedUserFactory(
            age=19,
            beneficiaryFraudChecks__eligibilityType=users_models.EligibilityType.AGE18,
            beneficiaryFraudChecks__dateCreated=year_when_user_was_eighteen,
        )

        base_form = {
            "status": subscription_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE17_18.name,
            "reason": "test",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            "Le compte a commencé le parcours d'activation de l'ancien crédit. Il est éligible à l'ancien Pass 18."
            in html_parser.extract_alert(response.data)
        )

    def test_unlocks_recredit_18(self, authenticated_client):
        user = users_factories.BeneficiaryFactory(age=17)
        eighteen_years_ago = date_utils.get_naive_utc_now() - relativedelta(years=18, months=1)
        user.validatedBirthDate = eighteen_years_ago

        base_form = {
            "status": subscription_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE17_18.name,
            "reason": "test",
        }
        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=base_form)
        assert response.status_code == 303

        user = db.session.query(users_models.User).filter_by(id=user.id).one()
        assert any(
            recredit.recreditType == finance_models.RecreditType.RECREDIT_18 for recredit in user.deposit.recredits
        )

    @pytest.mark.parametrize("exception_class", [finance_exceptions.UserCannotBeRecredited, DisabledFeatureError])
    def test_review_public_account_exception(self, authenticated_client, exception_class):
        user = users_factories.BeneficiaryFactory()

        form = {
            "status": subscription_models.FraudReviewStatus.OK.name,
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

    def test_uses_most_recent_id_number(self, authenticated_client):
        first_beneficiary = users_factories.BeneficiaryFactory()
        would_be_beneficiary = users_factories.ProfileCompletedUserFactory()
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=would_be_beneficiary,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=[
                subscription_models.FraudReasonCode.ID_CHECK_DATA_MATCH,
                subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER,
            ],
            resultContent=subscription_factories.UbbleContentFactory(
                id_document_number=first_beneficiary.idPieceNumber
            ),
        )
        admin_user = users_factories.AdminFactory()
        new_id_piece_number = "123456789012"
        users_api.update_user_info(would_be_beneficiary, author=admin_user, id_piece_number=new_id_piece_number)

        form = {
            "status": subscription_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE17_18.name,
            "reason": "test",
        }
        response = self.post_to_endpoint(authenticated_client, user_id=would_be_beneficiary.id, form=form)

        assert response.status_code == 303
        assert would_be_beneficiary.is_beneficiary


class GetBonusCreditRequestFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.public_accounts.get_request_bonus_credit_form"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.REQUEST_BENEFICIARY_BONUS_CREDIT

    # - authenticated user and session (1 query)
    # - user and joined deposits and recredis (1 query)
    expected_num_queries = 2
    # - beneficiary fraud checks (1 query: lazyload)
    expected_num_queries_when_eligible = expected_num_queries + 1

    def test_get_bonus_credit_request_form(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        user_id = user.id

        with assert_num_queries(self.expected_num_queries_when_eligible):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert "Vous pouvez demander la bonification" in html_parser.content_as_text(response.data)

    @pytest.mark.parametrize("num_fraud_checks", [1, users_constants.MAX_QF_BONUS_RETRIES])
    def test_get_bonus_credit_request_form_already_tried(self, authenticated_client, num_fraud_checks):
        user = users_factories.BeneficiaryFactory()
        subscription_factories.BonusFraudCheckFactory.create_batch(
            size=num_fraud_checks - 1, user=user, status=subscription_models.FraudCheckStatus.KO
        )
        subscription_factories.BonusFraudCheckFactory(
            user=user,
            status=subscription_models.FraudCheckStatus.KO,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                custodian=subscription_factories.QuotientFamilialCustodianFactory(
                    gender=users_models.GenderEnum.F,
                    first_names=["Augustine", "Pauline", "Henriette"],
                    last_name="Lansot",
                    common_name="Pagnol",
                    birth_date="1973-09-11",
                    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
                    birth_city_cog_code="13055",
                )
            ).model_dump(),
        )
        user_id = user.id

        with assert_num_queries(self.expected_num_queries_when_eligible):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert "Vous pouvez demander la bonification" in html_parser.content_as_text(response.data)

        assert html_parser.extract_select_options(response.data, "civility", selected_only=True) == {
            users_models.GenderEnum.F.name: "Madame"
        }
        assert html_parser.extract_input_value(response.data, "first_names") == "Augustine, Pauline, Henriette"
        assert html_parser.extract_input_value(response.data, "last_name") == "Lansot"
        assert html_parser.extract_input_value(response.data, "common_name") == "Pagnol"
        assert html_parser.extract_input_value(response.data, "birth_date") == "1973-09-11"
        assert html_parser.extract_select_options(response.data, "birth_country", selected_only=True) == {
            countries_utils.FRANCE_INSEE_CODE: "France"
        }
        assert html_parser.extract_tom_select_options(response.data, "birth_city", selected_only=True) == {
            "13055": "Ville (13)"
        }

    @pytest.mark.parametrize(
        "user_factory",
        [
            users_factories.UserFactory,
            users_factories.UnderageBeneficiaryFactory,
            users_factories.FreeBeneficiaryFactory,
            users_factories.ProFactory,
        ],
    )
    def test_not_eligible_to_bonus(self, authenticated_client, user_factory):
        user_id = user_factory().id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        assert (
            html_parser.content_as_text(response.data)
            == "Demande de bonification Ce compte n'est pas éligible à une bonification. Annuler"
        )

    def test_user_does_not_exist(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, user_id=99999))
        assert response.status_code == 404


class BonusCreditRequestTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.request_bonus_credit"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.REQUEST_BENEFICIARY_BONUS_CREDIT

    form_data = {
        "civility": users_models.GenderEnum.M.name,
        "first_names": "Joseph, André",
        "last_name": "Pagnol",
        "common_name": "",
        "birth_date": "1969-10-25",
        "birth_country": countries_utils.FRANCE_INSEE_CODE,
        "birth_city": ["84137"],
    }

    def test_request_bonus_credit(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        user_id = user.id

        response = self.post_to_endpoint(
            authenticated_client,
            user_id=user_id,
            form=self.form_data,
            follow_redirects=False,
            # - select authenticated user and session (1 query)
            # - select user and joined deposits and recredis (1 query)
            # - select beneficiary fraud checks (1 query: lazyload)
            # - insert beneficiary fraud check (1 query)
            expected_num_queries=4,
        )
        assert response.status_code == 303

        qf_fraud_checks = users_api.get_qf_bonus_credit_fraud_checks(user)
        assert len(qf_fraud_checks) == 1
        qf_fraud_check = qf_fraud_checks[0]
        assert qf_fraud_check.type == subscription_models.FraudCheckType.QF_BONUS_CREDIT
        assert qf_fraud_check.status == subscription_models.FraudCheckStatus.STARTED
        assert qf_fraud_check.resultContent
        custodian = qf_fraud_check.resultContent["custodian"]
        assert custodian["gender"] == "M."
        assert custodian["first_names"] == ["Joseph", "André"]
        assert custodian["last_name"] == "Pagnol"
        assert custodian["common_name"] is None
        assert custodian["birth_date"] == "1969-10-25"
        assert custodian["birth_country_cog_code"] == countries_utils.FRANCE_INSEE_CODE
        assert custodian["birth_city_cog_code"] == "84137"

        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "La demande de bonification est en cours."
        )

    def test_birth_country_is_not_france(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        user_id = user.id

        form_data = self.form_data.copy()
        form_data["birth_country"] = "99101"
        form_data["birth_city"] = ""

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form_data, follow_redirects=True)
        assert response.status_code == 200

        assert html_parser.extract_alert(response.data) == "La demande de bonification est en cours."

        qf_fraud_checks = users_api.get_qf_bonus_credit_fraud_checks(user)
        assert len(qf_fraud_checks) == 1
        qf_fraud_check = qf_fraud_checks[0]
        assert qf_fraud_check.type == subscription_models.FraudCheckType.QF_BONUS_CREDIT
        assert qf_fraud_check.status == subscription_models.FraudCheckStatus.STARTED
        assert qf_fraud_check.resultContent
        custodian = qf_fraud_check.resultContent["custodian"]
        assert custodian["birth_country_cog_code"] == "99101"
        assert custodian["birth_city_cog_code"] is None

    def test_city_is_missing(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        user_id = user.id

        form_data = self.form_data.copy()
        form_data["birth_city"] = ""

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form_data, follow_redirects=True)
        assert response.status_code == 200

        assert html_parser.extract_alert(response.data) == (
            "Les données envoyées comportent des erreurs. Ville de naissance du représentant légal (s'il est né en France) : "
            "obligatoire lorsque le représentant légal est né en France ;"
        )
        assert not users_api.get_qf_bonus_credit_fraud_checks(user)

    def test_city_is_set_but_country_is_not_france(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        user_id = user.id

        form_data = self.form_data.copy()
        form_data["birth_country"] = "99101"

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form_data, follow_redirects=True)
        assert response.status_code == 200

        assert html_parser.extract_alert(response.data) == (
            "Les données envoyées comportent des erreurs. Ville de naissance du représentant légal (s'il est né en France) : "
            "doit rester vide lorsque le représentant légal n'est pas né en France ;"
        )
        assert not users_api.get_qf_bonus_credit_fraud_checks(user)

    @pytest.mark.parametrize(
        "user_factory",
        [users_factories.UserFactory, users_factories.UnderageBeneficiaryFactory, users_factories.ProFactory],
    )
    def test_not_eligible_to_bonus(self, authenticated_client, user_factory):
        user_id = user_factory().id

        response = self.post_to_endpoint(
            authenticated_client, user_id=user_id, form=self.form_data, follow_redirects=True
        )
        assert response.status_code == 200

        assert html_parser.extract_alert(response.data) == "Ce compte n'est pas éligible à une bonification"

    def test_user_does_not_exist(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client, user_id=99999, form=self.form_data, follow_redirects=True
        )
        assert response.status_code == 404


class GetPublicAccountHistoryTest:
    def test_history_contains_creation_date(self):
        user = users_factories.UserFactory()

        history = get_public_account_history(user)

        assert len(history) == 1
        assert history[0].actionType == history_models.ActionType.USER_CREATED
        assert history[0].actionDate == user.dateCreated
        assert history[0].authorUser == user

    def test_history_contains_email_changes(self):
        user = users_factories.UserFactory(dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=1))
        email_request = users_factories.EmailUpdateEntryFactory(
            user=user,
            creationDate=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=10),
            newUserEmail=None,
            newDomainEmail=None,
        )
        email_confirmation = users_factories.EmailConfirmationEntryFactory(
            user=user, creationDate=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=5)
        )
        email_validation = users_factories.EmailValidationEntryFactory(
            user=user, creationDate=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=5)
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
        user = users_factories.UserFactory(dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=3))
        author = users_factories.UserFactory()
        suspension_action = history_factories.SuspendedUserActionHistoryFactory(
            user=user,
            authorUser=author,
            actionDate=date_utils.get_naive_utc_now() - relativedelta(days=2),
            reason=users_constants.SuspensionReason.FRAUD_SUSPICION,
        )
        unsuspension_action = history_factories.UnsuspendedUserActionHistoryFactory(
            user=user,
            authorUser=author,
            actionDate=date_utils.get_naive_utc_now() - relativedelta(days=1),
        )

        history = get_public_account_history(user)

        assert len(history) >= 2
        assert history[0] == unsuspension_action
        assert history[1] == suspension_action

    @pytest.mark.parametrize(
        "bo_role, expected_bonus_reason",
        [
            (perm_models.Roles.SUPPORT_N2, subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD.value),
            (perm_models.Roles.SUPPORT_N1, "raison confidentielle"),
            (perm_models.Roles.SUPPORT_PRO, "raison confidentielle"),
        ],
    )
    def test_history_contains_fraud_checks(self, roles_with_permissions, bo_role, expected_bonus_reason):
        bo_user = users_factories.AdminFactory()
        backoffice_api.upsert_roles(bo_user, [bo_role])

        now = date_utils.get_naive_utc_now()
        user = users_factories.UserFactory(dateCreated=now - datetime.timedelta(days=1))
        dms = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.DMS,
            dateCreated=now - datetime.timedelta(minutes=20),
        )
        phone = subscription_factories.PhoneValidationFraudCheckFactory(
            user=user,
            dateCreated=now - datetime.timedelta(minutes=15),
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=[subscription_models.FraudReasonCode.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED],
        )
        honor = subscription_factories.HonorStatementFraudCheckFactory(
            user=user,
            dateCreated=now - datetime.timedelta(minutes=10),
            status=None,
        )
        bonus = subscription_factories.BonusFraudCheckFactory(
            user=user,
            dateCreated=now - datetime.timedelta(minutes=5),
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=[subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD],
        )

        history = get_public_account_history(user, bo_user)

        assert len(history) >= 4

        assert history[3].actionType == "Étape de vérification"
        assert history[3].actionDate == dms.dateCreated
        assert (
            history[3].comment
            == f"{dms.type.value}, {dms.eligibilityType.value}, {dms.status.value}, raison inconnue, {dms.reason}"
        )

        assert history[2].actionType == "Étape de vérification"
        assert history[2].actionDate == phone.dateCreated
        assert (
            history[2].comment
            == f"{phone.type.value}, {phone.eligibilityType.value}, {phone.status.value}, {subscription_models.FraudReasonCode.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED.value}, {phone.reason}"
        )

        assert history[1].actionType == "Étape de vérification"
        assert history[1].actionDate == honor.dateCreated
        assert (
            history[1].comment
            == f"{honor.type.value}, {honor.eligibilityType.value}, Statut inconnu, raison inconnue, {honor.reason}"
        )

        assert history[0].actionType == "Étape de vérification"
        assert history[0].actionDate == bonus.dateCreated
        assert (
            history[0].comment
            == f"{bonus.type.value}, {honor.eligibilityType.value}, ko, {expected_bonus_reason}, {bonus.reason}"
        )

    def test_history_contains_reviews(self):
        user = users_factories.UserFactory(dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=1))
        author_user = users_factories.UserFactory()
        ko = subscription_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=author_user,
            dateReviewed=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=10),
            review=subscription_models.FraudReviewStatus.KO,
            reason="pas glop",
        )
        dms = subscription_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=author_user,
            dateReviewed=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=15),
            review=subscription_models.FraudReviewStatus.REDIRECTED_TO_DMS,
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
        now = date_utils.get_naive_utc_now()
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
        now = date_utils.get_naive_utc_now()
        user = users_factories.UserFactory(dateCreated=now - datetime.timedelta(days=365 + 10), postalCode="29280")
        recredit_16 = finance_factories.RecreditFactory(
            recreditType=finance_models.RecreditType.RECREDIT_16,
            amount=30,
            dateCreated=now - datetime.timedelta(days=365 + 8),
            deposit__user=user,
            deposit__type=finance_models.DepositType.GRANT_15_17,
            deposit__amount=80,
        )
        deposit_15_17 = user.deposit
        recredit_17 = finance_factories.RecreditFactory(
            recreditType=finance_models.RecreditType.RECREDIT_17,
            amount=30,
            dateCreated=now - datetime.timedelta(days=8),
            deposit=deposit_15_17,
        )
        # a grant 17_18 deposit is created empty, then a recredit is added to fill it
        deposit_17_18 = users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_17_18,
            dateCreated=now - datetime.timedelta(days=5),
            amount=150,
        )
        recredit_previous = finance_factories.RecreditFactory(
            recreditType=finance_models.RecreditType.PREVIOUS_DEPOSIT,
            amount=15,
            dateCreated=now - datetime.timedelta(days=4),
            deposit=deposit_17_18,
        )
        deposit_17_18.amount += recredit_previous.amount

        history = get_public_account_history(user)

        assert len(history) >= 5

        assert history[0].actionType == "Attribution d'un crédit"
        assert history[0].actionDate == deposit_15_17.dateCreated
        assert history[0].comment == "Attribution d'un ancien crédit 15-17 de 20,00 €"

        assert history[1].actionType == "Recrédit du compte"
        assert history[1].actionDate == recredit_previous.dateCreated
        assert history[1].comment == "Recrédit de l'argent restant du crédit précédent de 15,00 € sur un crédit 17-18"

        assert history[2].actionType == "Attribution d'un crédit"
        assert history[2].actionDate == deposit_17_18.dateCreated
        assert history[2].comment == "Attribution d'un crédit 17-18 de 150,00 €"

        assert history[3].actionType == "Recrédit du compte"
        assert history[3].actionDate == recredit_17.dateCreated
        assert history[3].comment == "Recrédit à 17 ans de 30,00 € sur un ancien crédit 15-17"

        assert history[4].actionType == "Recrédit du compte"
        assert history[4].actionDate == recredit_16.dateCreated
        assert history[4].comment == "Recrédit à 16 ans de 30,00 € sur un ancien crédit 15-17"

    def test_history_is_sorted_antichronologically(self):
        now = date_utils.get_naive_utc_now()
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
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            dateCreated=now - datetime.timedelta(minutes=35),
        )
        users_factories.EmailUpdateEntryFactory(user=user, creationDate=now - datetime.timedelta(minutes=30))
        users_factories.EmailValidationEntryFactory(user=user, creationDate=now - datetime.timedelta(minutes=15))
        subscription_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=author_user,
            dateReviewed=now - datetime.timedelta(minutes=5),
            review=subscription_models.FraudReviewStatus.OK,
        )

        history = get_public_account_history(user)

        assert len(history) == 8
        datetimes = [item.actionDate for item in history]
        assert datetimes == sorted(datetimes, reverse=True)


class GetUserRegistrationStepTest(GetEndpointHelper):
    endpoint = "backoffice_web.public_accounts.get_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PUBLIC_ACCOUNT

    def _check_steps(self, authenticated_client, user_id, expected_steps_id, expected_texts_and_icons):
        response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
        assert response.status_code == 200

        soup = html_parser.get_soup(response.data)
        assert soup.select(f'[data-registration-steps-id="{expected_steps_id}"]')
        steps = soup.select(".steps")
        assert len(steps) == len(expected_texts_and_icons)

        for step, expected_text_and_icon in zip(steps, expected_texts_and_icons):
            step_text = step.find(class_="step-text")
            assert step_text.text == expected_text_and_icon[0]
            step_icon_view = step.select(".step-status-icon-container i")
            if expected_text_and_icon[1]:
                assert len(step_icon_view) == 1
                step_icon_title = step_icon_view[0].attrs.get("title")
                assert step_icon_title == expected_text_and_icon[1]
            else:
                assert not step_icon_view

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "underage",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 15-17", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "underage+age-17-18",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 15-17", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 17", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Num. téléphone", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 18", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=signup_date,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.CANCELED,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=signup_date,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME + relativedelta(days=3),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME + relativedelta(days=3),
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "underage+age-17",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 15-17", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 17", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "underage+age-17",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 15-17", None),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 17", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "underage",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 15-17", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

    def test_registration_at_age15_after_decree(self, authenticated_client, settings):
        # Setup:
        # - Sign-up at 15
        # - Decree started 1 month earlier → User is 15 years old at that moment
        # - User is 15 years old now
        #
        # Expected registration timeline:
        # 1. Email Validation ✓
        # 2. Not Eligible ✓
        now = date_utils.get_naive_utc_now()
        birth_date = now - relativedelta(years=15, months=4, days=15)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=15, months=5)
        user = users_factories.UserFactory(
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME + relativedelta(days=5),
            dateOfBirth=birth_date,
            phoneValidationStatus=None,
            roles=[],
            validatedBirthDate=birth_date,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "not-eligible",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Non éligible", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
        birth_date = (now - relativedelta(years=17)).replace(hour=0, minute=0, second=0, microsecond=0)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=17) - relativedelta(days=1)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=17, hours=9),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
            validatedBirthDate=birth_date,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "age-17",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 17", None),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "underage",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 15-17", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

    def test_registration_at_age16_after_decree(self, authenticated_client, settings):
        # Setup
        # - Sign-up at 16 or 15 after the decree started
        #
        # Expected registration timeline:
        # 1. Email validation ✓
        # 2. Not Eligible ✓
        now = date_utils.get_naive_utc_now()
        birth_date = now - relativedelta(years=16, months=7)
        settings.CREDIT_V3_DECREE_DATETIME = birth_date + relativedelta(years=15)
        user = users_factories.UserFactory(
            dateCreated=birth_date + relativedelta(years=16, months=1),
            dateOfBirth=birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[],
            validatedBirthDate=birth_date,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "not-eligible",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Non éligible", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "age-17",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 17", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
        birthdate = now - relativedelta(years=17, days=4)
        settings.CREDIT_V3_DECREE_DATETIME = birthdate + relativedelta(years=16, months=11, days=26)
        user = users_factories.UserFactory(
            dateCreated=birthdate + relativedelta(years=16, months=11, days=27),
            dateOfBirth=birthdate,
            phoneValidationStatus=None,
            roles=[],
            validatedBirthDate=birthdate,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "age-17",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.SUSPICIOUS.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 17", None),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            dateCreated=user.dateCreated,
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            dateCreated=user.dateCreated,
            user=user,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            dateCreated=user.dateCreated,
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "underage+age-18",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 15-17", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Num. téléphone", None),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 18", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "age-17-18",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 17", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Num. téléphone", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 18", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
        birth_date = now - relativedelta(years=18, days=10)
        settings.CREDIT_V3_DECREE_DATETIME = now - relativedelta(days=17)
        user = users_factories.UserFactory(
            dateCreated=now - relativedelta(days=14),
            dateOfBirth=birth_date,
            phoneValidationStatus=None,
            roles=[],
            validatedBirthDate=birth_date,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            dateCreated=user.dateCreated,
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            dateCreated=user.dateCreated,
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "age-17-18",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", None),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", None),
                ("Pass 17", None),
                ("Num. téléphone", None),
                ("Profil complet", None),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", None),
                ("Pass 18", None),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Phone check
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "age-18",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Num. téléphone", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Pass 18", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Phone check
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "age-18-old",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Num. téléphone", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 18", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "underage+age-18-old",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 15-17", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Num. téléphone", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Profil complet", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("ID check", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Attestation sur l'honneur", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Ancien Pass 18", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )

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
        now = date_utils.get_naive_utc_now()
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

        subscription_factories.BeneficiaryFraudCheckFactory(  # Complete profile
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # ID check
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(  # Honor statement
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        self._check_steps(
            authenticated_client,
            user.id,
            "not-eligible",
            (
                ("Email", subscription_schemas.SubscriptionItemStatus.OK.value),
                ("Non éligible", subscription_schemas.SubscriptionItemStatus.OK.value),
            ),
        )


@pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + datetime.timedelta(days=30))
class RegistrationStepTest:
    @pytest.mark.parametrize(
        "steps,expected_progress",
        [
            (
                [
                    RegistrationStep(
                        step_id=1,
                        description="Test 1",
                        subscription_item_status=subscription_schemas.SubscriptionItemStatus.SUSPICIOUS.value,
                        icon="bi-test",
                        is_active=True,
                    ),
                    RegistrationStep(
                        step_id=2,
                        description="Test 2",
                        subscription_item_status=subscription_schemas.SubscriptionItemStatus.VOID.value,
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
                        subscription_item_status=subscription_schemas.SubscriptionItemStatus.OK.value,
                        icon="bi-test",
                    ),
                    RegistrationStep(
                        step_id=2,
                        description="Test 2",
                        subscription_item_status=subscription_schemas.SubscriptionItemStatus.TODO.value,
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
                        subscription_item_status=subscription_schemas.SubscriptionItemStatus.OK.value,
                        icon="bi-test",
                    ),
                    RegistrationStep(
                        step_id=2,
                        description="Test 2",
                        subscription_item_status=subscription_schemas.SubscriptionItemStatus.TODO.value,
                        icon="bi-test",
                        is_active=True,
                    ),
                    RegistrationStep(
                        step_id=3,
                        description="Test 3",
                        subscription_item_status=subscription_schemas.SubscriptionItemStatus.VOID.value,
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
            (subscription_schemas.SubscriptionItemStatus.OK, RegistrationStepStatus.SUCCESS),
            (subscription_schemas.SubscriptionItemStatus.NOT_APPLICABLE, RegistrationStepStatus.SUCCESS),
            (subscription_schemas.SubscriptionItemStatus.NOT_ENABLED, RegistrationStepStatus.SUCCESS),
            (subscription_schemas.SubscriptionItemStatus.SKIPPED, RegistrationStepStatus.SUCCESS),
            (subscription_schemas.SubscriptionItemStatus.KO, RegistrationStepStatus.ERROR),
            (subscription_schemas.SubscriptionItemStatus.PENDING, RegistrationStepStatus.WARNING),
            (subscription_schemas.SubscriptionItemStatus.SUSPICIOUS, RegistrationStepStatus.WARNING),
            (subscription_schemas.SubscriptionItemStatus.TODO, None),
            (subscription_schemas.SubscriptionItemStatus.VOID, None),
        ],
    )
    def test_get_status(self, subscription_item_status, registration_step_status):
        assert _get_status(subscription_item_status.value) == registration_step_status

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + relativedelta(years=1))
    @pytest.mark.parametrize(
        "dateCreated,dateOfBirth,tunnel_type",
        [
            (
                date_utils.get_naive_utc_now(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1),
                TunnelType.AGE18_OLD,
            ),
            (
                date_utils.get_naive_utc_now(),
                datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1),
                TunnelType.UNDERAGE,
            ),
            (
                date_utils.get_naive_utc_now()
                - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2),
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
                date_utils.get_naive_utc_now(),
                None,
            ),
            (
                date_utils.get_naive_utc_now(),
                datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18 + 1, days=1),
            ),
        ],
    )
    def test_get_tunnel_type_non_eligible(self, dateCreated, dateOfBirth):
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, dateCreated=dateCreated
        )
        assert _get_tunnel_type(user) == TunnelType.NOT_ELIGIBLE

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + datetime.timedelta(days=3000))
    def test_get_subscription_item_status_by_eligibility_age18_old(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        now = date_utils.get_naive_utc_now()
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        user.add_beneficiary_role()

        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        assert len(subscription_item_status[EligibilityType.UNDERAGE.value]) == 0
        assert len(subscription_item_status[EligibilityType.AGE18.value]) > 0
        assert (
            subscription_item_status[EligibilityType.AGE18.value][
                subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value
            ]
            == subscription_schemas.SubscriptionItemStatus.OK.value
        )

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + datetime.timedelta(days=3000))
    def test_get_subscription_item_status_by_eligibility_underage(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        now = date_utils.get_naive_utc_now()
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        user.add_beneficiary_role()

        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        assert len(subscription_item_status[EligibilityType.AGE18.value]) == 0
        assert len(subscription_item_status[EligibilityType.UNDERAGE.value]) > 0
        assert (
            subscription_item_status[EligibilityType.UNDERAGE.value][
                subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value
            ]
            == subscription_schemas.SubscriptionItemStatus.OK.value
        )

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + datetime.timedelta(days=3000))
    def test_get_subscription_item_status_by_eligibility_underage_age18(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        now = date_utils.get_naive_utc_now()
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
            subscription_item_status[EligibilityType.AGE18.value][
                subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value
            ]
            == subscription_schemas.SubscriptionItemStatus.OK.value
        )
        assert (
            subscription_item_status[EligibilityType.UNDERAGE.value][
                subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value
            ]
            == subscription_schemas.SubscriptionItemStatus.OK.value
        )

    @pytest.mark.parametrize(
        "item_status_15_17,item_status_18,item_status_17_18",
        [
            (
                {
                    subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value: subscription_schemas.SubscriptionItemStatus.OK.value
                },
                {},
                {},
            ),
            (
                {},
                {
                    subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value: subscription_schemas.SubscriptionItemStatus.OK.value
                },
                {},
            ),
            (
                {},
                {},
                {
                    subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value: subscription_schemas.SubscriptionItemStatus.OK.value
                },
            ),
            (
                {
                    subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value: subscription_schemas.SubscriptionItemStatus.OK.value
                },
                {
                    subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value: subscription_schemas.SubscriptionItemStatus.OK.value
                },
                {},
            ),
            (
                {
                    subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value: subscription_schemas.SubscriptionItemStatus.OK.value
                },
                {},
                {
                    subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value: subscription_schemas.SubscriptionItemStatus.OK.value
                },
            ),
            (
                {},
                {
                    subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value: subscription_schemas.SubscriptionItemStatus.OK.value
                },
                {
                    subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value: subscription_schemas.SubscriptionItemStatus.OK.value
                },
            ),
        ],
    )
    def test_get_steps_tunnel_unspecified(self, item_status_15_17, item_status_18, item_status_17_18):
        steps = _get_steps_tunnel_unspecified(item_status_15_17, item_status_18, item_status_17_18)
        assert len(steps) == 2

        assert steps[0].step_id == 1
        assert steps[0].description == subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value
        assert steps[0].icon == "bi-envelope"
        assert steps[0].subscription_item_status == subscription_schemas.SubscriptionItemStatus.OK.value

        assert steps[1].step_id == 2
        assert steps[1].description == TunnelType.NOT_ELIGIBLE.value
        assert steps[1].icon == "bi-question-circle"
        assert steps[1].subscription_item_status == subscription_schemas.SubscriptionItemStatus.OK.value

    def test_get_steps_tunnel_unspecified_pending_email_validation(self):
        steps = _get_steps_tunnel_unspecified({}, {}, {})
        assert len(steps) == 2

        assert steps[0].step_id == 1
        assert steps[0].description == subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value
        assert steps[0].icon == "bi-envelope"
        assert steps[0].subscription_item_status == subscription_schemas.SubscriptionItemStatus.PENDING.value

        assert steps[1].step_id == 2
        assert steps[1].description == TunnelType.NOT_ELIGIBLE.value
        assert steps[1].icon == "bi-question-circle"
        assert steps[1].subscription_item_status == subscription_schemas.SubscriptionItemStatus.PENDING.value

    def test_get_id_check_histories_desc(self):
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth)
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
            resultContent=subscription_factories.UbbleContentFactory(),
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
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
        subscription_factories.BeneficiaryFraudCheckFactory(user=user, eligibilityType=None)
        subscription_factories.BeneficiaryFraudCheckFactory(user=user)
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]

        steps = _get_steps_tunnel_age18_old(user, item_status_18)
        assert len(steps) == 6

        assert steps[0].step_id == 1
        assert steps[0].description == subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value

        assert steps[1].step_id == 2
        assert steps[1].description == subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value

        assert steps[2].step_id == 3
        assert steps[2].description == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[3].step_id == 4
        assert steps[3].description == subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value

        assert steps[4].step_id == 5
        assert steps[4].description == subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value

        assert steps[5].step_id == 6
        assert steps[5].description == "Ancien Pass 18"

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() - relativedelta(years=1))
    def test_get_steps_tunnel_age18(self):
        user = users_factories.BeneficiaryFactory()
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_17_18 = subscription_item_status[EligibilityType.AGE17_18.value]

        steps = _get_steps_tunnel_age18(user, item_status_17_18)
        assert len(steps) == 6
        assert steps[0].step_id == 1
        assert steps[0].description == subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value

        assert steps[1].step_id == 2
        assert steps[1].description == subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value

        assert steps[2].step_id == 3
        assert steps[2].description == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[3].step_id == 4
        assert steps[3].description == subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value

        assert steps[4].step_id == 5
        assert steps[4].description == subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value

        assert steps[5].step_id == 6
        assert steps[5].description == "Pass 18"

    def test_get_steps_tunnel_underage(self):
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth)
        user.add_beneficiary_role()
        users_factories.DepositGrantFactory(user=user)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=None, dateCreated=dateOfBirth + relativedelta(years=15)
        )
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]

        steps = _get_steps_tunnel_underage(user, item_status_15_17)
        assert len(steps) == 5

        assert steps[0].step_id == 1
        assert steps[0].description == subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value

        assert steps[1].step_id == 2
        assert steps[1].description == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[2].step_id == 3
        assert steps[2].description == subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value

        assert steps[3].step_id == 4
        assert steps[3].description == subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value

        assert steps[4].step_id == 5
        assert steps[4].description == "Ancien Pass 15-17"

    def test_get_steps_tunnel_underage_age18(self):
        now = date_utils.get_naive_utc_now()
        dateCreated = now - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2)
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, dateCreated=dateCreated
        )
        user.add_beneficiary_role()
        users_factories.DepositGrantFactory(user=user)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=None, dateCreated=dateOfBirth + relativedelta(years=15)
        )
        subscription_factories.BeneficiaryFraudCheckFactory(user=user, eligibilityType=None)
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]

        steps = _get_steps_tunnel_underage_age18(user, item_status_15_17, item_status_18)
        assert len(steps) == 10

        assert steps[0].step_id == 1
        assert steps[0].description == subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value

        assert steps[1].step_id == 2
        assert steps[1].description == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[2].step_id == 3
        assert steps[2].description == subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value

        assert steps[3].step_id == 4
        assert steps[3].description == subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value

        assert steps[4].step_id == 5
        assert steps[4].description == EligibilityType.UNDERAGE.value

        assert steps[5].step_id == 6
        assert steps[5].description == subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value

        assert steps[6].step_id == 7
        assert steps[6].description == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value

        assert steps[7].step_id == 8
        assert steps[7].description == subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value

        assert steps[8].step_id == 9
        assert steps[8].description == subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value

        assert steps[9].step_id == 10
        assert steps[9].description == EligibilityType.AGE18.value

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + datetime.timedelta(days=3000))
    def test_get_steps_for_tunnel_not_eligible(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18 + 1, days=1)
        now = date_utils.get_naive_utc_now()
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]
        tunnel_type = _get_tunnel_type(user)
        steps = _get_steps_for_tunnel(user, tunnel_type, subscription_item_status)
        steps_to_compare = _get_steps_tunnel_unspecified(item_status_15_17, item_status_18, {})
        assert steps == steps_to_compare

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + relativedelta(years=1))
    def test_get_steps_for_tunnel_underage_age18(self):
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        creation_date = date_utils.get_naive_utc_now() - relativedelta(
            years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2
        )
        user = users_factories.UserFactory(
            dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=creation_date
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
            resultContent=subscription_factories.UbbleContentFactory(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
            resultContent=subscription_factories.UbbleContentFactory(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]
        tunnel_type = _get_tunnel_type(user)
        steps = _get_steps_for_tunnel(user, tunnel_type, subscription_item_status)
        steps_to_compare = _get_steps_tunnel_underage_age18_old(user, item_status_15_17, item_status_18)
        _set_steps_with_active_and_disabled(steps_to_compare)
        assert steps == steps_to_compare

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + relativedelta(years=1))
    def test_get_steps_for_tunnel_underage(self):
        now = date_utils.get_naive_utc_now()
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
            resultContent=subscription_factories.UbbleContentFactory(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        tunnel_type = _get_tunnel_type(user)
        steps = _get_steps_for_tunnel(user, tunnel_type, subscription_item_status)
        steps_to_compare = _get_steps_tunnel_underage(user, item_status_15_17)
        _set_steps_with_active_and_disabled(steps_to_compare)
        assert steps == steps_to_compare

    def test_get_steps_for_tunnel_bonus_credit_not_started(self):
        user = users_factories.BeneficiaryFactory()
        bonus_steps = _get_steps_tunnel_bonus_credit(user)
        assert bonus_steps == []

    def test_get_steps_for_tunnel_bonus_credit_ok(self):
        user = users_factories.BeneficiaryFactory(deposit__type=finance_models.DepositType.GRANT_17_18)
        subscription_factories.BonusFraudCheckFactory(user=user)
        finance_factories.RecreditFactory(deposit=user.deposit, recreditType=finance_models.RecreditType.BONUS_CREDIT)
        bonus_steps = _get_steps_tunnel_bonus_credit(user)
        assert len(bonus_steps) == 2
        assert bonus_steps[0].subscription_item_status == subscription_schemas.SubscriptionItemStatus.OK.value
        assert bonus_steps[1].subscription_item_status == subscription_schemas.SubscriptionItemStatus.OK.value

    def test_get_steps_for_tunnel_bonus_credit_ko(self):
        user = users_factories.BeneficiaryFactory(deposit__type=finance_models.DepositType.GRANT_17_18)
        subscription_factories.BonusFraudCheckFactory(user=user, status=subscription_models.FraudCheckStatus.KO)
        bonus_steps = _get_steps_tunnel_bonus_credit(user)
        assert len(bonus_steps) == 2
        assert bonus_steps[0].subscription_item_status == subscription_schemas.SubscriptionItemStatus.KO.value
        assert bonus_steps[1].subscription_item_status == subscription_schemas.SubscriptionItemStatus.VOID.value

    def test_get_steps_for_tunnel_bonus_credit_ko_then_started(self):
        user = users_factories.BeneficiaryFactory(deposit__type=finance_models.DepositType.GRANT_17_18)
        subscription_factories.BonusFraudCheckFactory(user=user, status=subscription_models.FraudCheckStatus.KO)
        subscription_factories.BonusFraudCheckFactory(user=user, status=subscription_models.FraudCheckStatus.STARTED)
        bonus_steps = _get_steps_tunnel_bonus_credit(user)
        assert len(bonus_steps) == 2
        assert bonus_steps[0].subscription_item_status == subscription_schemas.SubscriptionItemStatus.PENDING.value
        assert bonus_steps[1].subscription_item_status == subscription_schemas.SubscriptionItemStatus.VOID.value

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + relativedelta(years=1))
    def test_get_steps_for_tunnel_age18_old(self):
        now = date_utils.get_naive_utc_now()
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
            resultContent=subscription_factories.UbbleContentFactory(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]
        tunnel_type = _get_tunnel_type(user)

        steps = _get_steps_for_tunnel(user, tunnel_type, subscription_item_status)
        steps_to_compare = _get_steps_tunnel_age18_old(user, item_status_18)
        _set_steps_with_active_and_disabled(steps_to_compare)
        assert steps == steps_to_compare

    def test_set_steps_with_active_and_disabled_underage_age18(self):
        creation_date = date_utils.get_naive_utc_now() - relativedelta(
            years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=2
        )
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(
            dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=creation_date
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
            resultContent=subscription_factories.UbbleContentFactory(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
            resultContent=subscription_factories.UbbleContentFactory(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]

        steps = _get_steps_tunnel_underage_age18(user, item_status_15_17, item_status_18)
        assert steps[8].status["active"] is False
        assert steps[9].status["disabled"] is False

        _set_steps_with_active_and_disabled(steps)

        assert steps[8].status["active"] is True
        assert steps[9].status["disabled"] is True

    def test_set_steps_with_active_and_disabled_underage(self):
        now = date_utils.get_naive_utc_now()
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
            resultContent=subscription_factories.UbbleContentFactory(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]

        steps = _get_steps_tunnel_underage(user, item_status_15_17)
        assert steps[3].status["active"] is False
        assert steps[4].status["disabled"] is False

        _set_steps_with_active_and_disabled(steps)

        assert steps[3].status["active"] is True
        assert steps[4].status["disabled"] is True

    def test_set_steps_with_active_and_disabled_age18_old(self):
        now = date_utils.get_naive_utc_now()
        birth_date = datetime.date.today() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18, days=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date, validatedBirthDate=birth_date, dateCreated=now)
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
            resultContent=subscription_factories.UbbleContentFactory(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        eligibility_history = get_eligibility_history(user)
        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        item_status_18 = subscription_item_status[EligibilityType.AGE18.value]

        steps = _get_steps_tunnel_age18_old(user, item_status_18)
        assert steps[4].status["active"] is False
        assert steps[5].status["disabled"] is False

        _set_steps_with_active_and_disabled(steps)

        assert steps[4].status["active"] is True
        assert steps[5].status["disabled"] is True

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=date_utils.get_naive_utc_now() + relativedelta(years=1))
    def test_get_tunnel(self):
        dateOfBirth = datetime.date.today() - relativedelta(years=users_constants.ACCOUNT_CREATION_MINIMUM_AGE, days=1)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth, isEmailValidated=True
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        eligibility_history = get_eligibility_history(user)
        tunnel = _get_tunnel(user, eligibility_history)
        assert tunnel["type"] == TunnelType.UNDERAGE
        assert tunnel["progress"] == 75

        users_factories.DepositGrantFactory(user=user, type=finance_models.DepositType.GRANT_15_17)
        tunnel_end = _get_tunnel(user, eligibility_history)
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

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert response.location == expected_url

        assert user.firstName is None
        assert user.lastName is None
        assert user.roles == [users_models.UserRole.ANONYMIZED]
        history = db.session.query(history_models.ActionHistory).one_or_none()
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
            gdprUserDataExtracts=[
                users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.today())
            ]
        )

        with open(storage_folder / f"{user.gdprUserDataExtracts[0].id}.zip", "wb"):
            pass

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert response.location == expected_url

        assert user.roles == [users_models.UserRole.ANONYMIZED]

        assert db.session.query(users_models.GdprUserDataExtract).count() == 0
        assert len(os.listdir(storage_folder)) == 0

        response = authenticated_client.get(response.location)
        assert "Les informations de l'utilisateur ont été anonymisées" in html_parser.extract_alert(response.data)

    def test_anonymize_public_account_with_unprocessed_gdpr_extract(
        self,
        legit_user,
        authenticated_client,
    ):
        user = users_factories.UserFactory(
            gdprUserDataExtracts=[users_factories.GdprUserDataExtractBeneficiaryFactory()]
        )

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
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
        assert db.session.query(users_models.GdprUserAnonymization).filter_by(userId=user.id).count() == 1
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

        db.session.query(finance_models.Deposit).filter(finance_models.Deposit.user == user).delete()

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
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

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert response.location == expected_url

        assert user.roles == [users_models.UserRole.ANONYMIZED]

    def test_anonymize_public_is_suspended_for_fraud(self, authenticated_client):
        user = users_factories.BeneficiaryFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now(),
            actionType=history_models.ActionType.USER_SUSPENDED,
            reason=users_constants.SuspensionReason.FRAUD_RESELL_PASS,
            user=user,
        )

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, follow_redirects=True)
        assert response.status_code == 200

        db.session.refresh(user)
        assert not user.isActive
        assert db.session.query(users_models.GdprUserAnonymization).filter_by(userId=user.id).count() == 1
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

        assert db.session.query(users_models.UserAccountUpdateRequest).count() == 0

        response = authenticated_client.get(response.location)
        assert "Les informations de l'utilisateur ont été anonymisées" in html_parser.extract_alert(response.data)


class ExtractPublicAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.create_extract_user_gdpr_data"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT

    expected_queries = 3  # session + targeted user with joined data + gdpr insert

    def test_extract_public_account(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(
            authenticated_client, user_id=user.id, expected_num_queries=self.expected_queries
        )
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert response.location == expected_url

        extract_data = db.session.query(users_models.GdprUserDataExtract).one()
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

        assert 1 == db.session.query(users_models.GdprUserDataExtract).count()

    def test_extract_public_account_with_existing_extract_data_expired(self, authenticated_client, legit_user):
        expired_gdpr_data_extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=8)
        )

        response = self.post_to_endpoint(authenticated_client, user_id=expired_gdpr_data_extract.user.id)

        expected_url = url_for(
            "backoffice_web.public_accounts.get_public_account",
            user_id=expired_gdpr_data_extract.user.id,
        )

        assert response.status_code == 302
        assert response.location == expected_url
        extract_data = db.session.query(users_models.GdprUserDataExtract).all()
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
    # targeted user by id
    # UPDATE user
    # INSERT actionhistory
    expected_queries = 4

    def test_invalidate_public_account_password(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryFactory()
        user_password_before_response = user.password

        response = self.post_to_endpoint(
            authenticated_client, user_id=user.id, expected_num_queries=self.expected_queries
        )
        assert response.status_code == 303

        assert user_password_before_response != user.password

        action_history = db.session.query(history_models.ActionHistory).one()
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
    # targeted user by id
    expected_queries = 2

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
        assert "mot-de-passe-perdu" in mails_testing.outbox[0]["params"]["RESET_PASSWORD_LINK"]

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


class ListAccountTagsTest(GetEndpointHelper):
    endpoint = "backoffice_web.account_tag.list_account_tags"
    needed_permission = perm_models.Permissions.READ_TAGS

    # - fetch session + user (1 query)
    # - fetch categories and tags (2 queries)
    expected_num_queries = 3

    def test_list_account_tags(self, authenticated_client):
        category = users_factories.UserTagCategoryFactory(label="tagjeune")
        user_tag = users_factories.UserTagFactory(
            name="tag1",
            label="Tag 1",
            description="Jeune Tag 1",
            categories=[category],
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="tags-tab-pane")
        assert len(rows) == 1
        assert rows[0]["ID"] == str(user_tag.id)
        assert rows[0]["Nom"] == user_tag.name
        assert rows[0]["Libellé"] == user_tag.label
        assert rows[0]["Description"] == user_tag.description
        assert rows[0]["Catégories"] == category.label

    def test_list_account_tag_categories(self, authenticated_client):
        category1 = users_factories.UserTagCategoryFactory(name="tagcat1", label="Tag catégorie 1")
        category2 = users_factories.UserTagCategoryFactory(name="tagcat2", label="Tag catégorie 2")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="categories-tab-pane")
        assert len(rows) == 2
        assert {str(category1.id), str(category2.id)} == {e["ID"] for e in rows}
        row1 = [e for e in rows if e["ID"] == str(category1.id)][0]
        row2 = [e for e in rows if e["ID"] == str(category2.id)][0]
        assert row1["Nom"] == "tagcat1"
        assert row1["Libellé"] == "Tag catégorie 1"
        assert row2["Nom"] == "tagcat2"
        assert row2["Libellé"] == "Tag catégorie 2"


class CreateTagButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_TAGS
    button_label = "Créer un tag"

    @property
    def path(self):
        return url_for("backoffice_web.account_tag.list_account_tags")


class CreateTagCategoryButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_TAGS_N2
    button_label = "Créer une catégorie"

    @property
    def path(self):
        return url_for("backoffice_web.account_tag.list_account_tags")


class UpdateAccountTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.account_tag.update_account_tag"
    endpoint_kwargs = {"user_tag_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_TAGS

    def test_update_account_tag(self, authenticated_client):
        tag_not_to_edit = users_factories.UserTagFactory(name="zzzzzzzz-end-of-the-list")
        category_to_keep = users_factories.UserTagCategoryFactory(label="AAA")
        category_to_remove = users_factories.UserTagCategoryFactory(label="BBB")
        category_to_add = users_factories.UserTagCategoryFactory(label="ZZZ")
        tag_to_edit = users_factories.UserTagFactory(
            name="tag-you-are-it",
            label="C'est toi le loup",
            description="Le jeu du loup c'est le 'tag' en anglais hihi",
            categories=[category_to_keep, category_to_remove],
        )

        new_name = "very-serious-tag"
        new_label = "Tag très sérieux"
        new_description = "Pas le temps de jouer"
        new_categories = [category_to_keep.id, category_to_add.id]

        base_form = {
            "name": new_name,
            "label": new_label,
            "description": new_description,
            "categories": new_categories,
        }
        response = self.post_to_endpoint(
            authenticated_client,
            user_tag_id=tag_to_edit.id,
            form=base_form,
            follow_redirects=True,
        )
        assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert html_parser.count_table_rows(response.data) == 2
        assert {e["ID"] for e in rows} == {str(tag_to_edit.id), str(tag_not_to_edit.id)}
        row1 = [e for e in rows if e["ID"] == str(tag_to_edit.id)][0]
        assert row1["Nom"] == new_name
        assert row1["Libellé"] == new_label
        assert row1["Description"] == new_description
        assert set(row1["Catégories"].split()) == {
            category_to_keep.label,
            category_to_add.label,
        }

        row2 = [e for e in rows if e["ID"] == str(tag_not_to_edit.id)][0]
        assert row2["Nom"] == tag_not_to_edit.name

    def test_update_with_wrong_data(self, authenticated_client):
        tag_to_edit = users_factories.UserTagFactory(
            name="tag-alog",
            label="Le tagalog c'est du philippin",
        )
        base_form = {
            "name": "",
            "label": "Le tagalog c'est du philippin",
        }
        response = self.post_to_endpoint(
            authenticated_client,
            user_tag_id=tag_to_edit.id,
            form=base_form,
            follow_redirects=True,
        )
        assert response.status_code == 200

        assert "Les données envoyées comportent des erreurs" in html_parser.extract_alert(response.data)
        assert tag_to_edit.name != ""

    def test_update_with_already_existing_tag(self, authenticated_client):
        users_factories.UserTagFactory(name="i-was-here-first")
        tag_to_edit = users_factories.UserTagFactory(name="a-silly-name")
        base_form = {
            "name": "i-was-here-first",
            "label": "",
            "description": "",
            "categories": [],
        }

        response = self.post_to_endpoint(
            authenticated_client,
            user_tag_id=tag_to_edit.id,
            form=base_form,
            follow_redirects=True,
        )
        assert response.status_code == 200

        assert html_parser.extract_alert(response.data) == "Ce nom de tag existe déjà"
        assert tag_to_edit.name == "a-silly-name"


class CreateAccountTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.account_tag.create_account_tag"
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_TAGS

    def test_create_account_tag(self, authenticated_client):
        category = users_factories.UserTagCategoryFactory(label="La catégorie des sucreries")

        name = "tag-ada"
        label = "Fraise Tag-ada"
        description = "Un tag délicieux mais dangereux"
        categories = [category.id]

        base_form = {
            "name": name,
            "label": label,
            "description": description,
            "categories": categories,
        }
        response = self.post_to_endpoint(authenticated_client, form=base_form)
        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.account_tag.list_account_tags")

        created_tag = db.session.query(users_models.UserTag).one()
        assert created_tag.name == name
        assert created_tag.label == label
        assert created_tag.description == description
        assert created_tag.categories == [category]

    def test_create_with_wrong_data(self, authenticated_client):
        base_form = {
            "name": "",
            "label": "Mon nom est Personne",
        }
        response = self.post_to_endpoint(authenticated_client, form=base_form)
        assert response.status_code == 303
        assert "Les données envoyées comportent des erreurs" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )
        assert db.session.query(users_models.UserTag).count() == 0

    def test_create_with_already_existing_tag(self, authenticated_client):
        users_factories.UserTagFactory(name="i-was-here-first")
        base_form = {
            "name": "i-was-here-first",
        }
        response = self.post_to_endpoint(authenticated_client, form=base_form)
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Ce tag existe déjà"
        assert db.session.query(users_models.UserTag).count() == 1


class DeleteAccountTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.account_tag.delete_account_tag"
    endpoint_kwargs = {"user_tag_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_TAGS_N2

    def test_delete_offerer_tag(self, authenticated_client):
        tags = users_factories.UserTagFactory.create_batch(3)
        user = users_factories.UserFactory(tags=tags[1:])

        response = self.post_to_endpoint(authenticated_client, user_tag_id=tags[1].id)

        assert response.status_code == 303
        assert set(db.session.query(users_models.UserTag).all()) == {tags[0], tags[2]}
        assert db.session.query(users_models.User).filter_by(id=user.id).one().tags == [tags[2]]

    def test_delete_non_existing_tag(self, authenticated_client):
        tag = users_factories.UserTagFactory()

        response = self.post_to_endpoint(authenticated_client, user_tag_id=tag.id + 1)

        assert response.status_code == 404
        assert db.session.query(users_models.UserTag).count() == 1


class CreateAccountTagCategoryTest(PostEndpointHelper):
    endpoint = "backoffice_web.account_tag.create_account_tag_category"
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_TAGS_N2

    def test_create_account_tag_category(self, authenticated_client):
        form_data = {
            "name": "nouvelle-categorie",
            "label": "Nouvelle catégorie",
        }
        response = self.post_to_endpoint(authenticated_client, form=form_data)

        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_web.account_tag.list_account_tags",
            active_tab="categories",
        )

        created_category = db.session.query(users_models.UserTagCategory).one()
        assert created_category.name == form_data["name"]
        assert created_category.label == form_data["label"]

    def test_create_with_already_existing_category(self, authenticated_client):
        category = users_factories.UserTagCategoryFactory(name="homologation", label="Homologation")

        form_data = {"name": category.name, "label": "Duplicate category"}
        response = self.post_to_endpoint(authenticated_client, form=form_data)

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data) == "Cette catégorie existe déjà"
        )

        assert db.session.query(users_models.UserTagCategory).count() == 1


class TagPublicAccountTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.tag_public_account"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ACCOUNT_TAGS

    def test_update_tag_public_account(self, authenticated_client):
        tag1 = users_factories.UserTagFactory(label="Ambassadeur A")
        tag2 = users_factories.UserTagFactory(label="Ambassadeur B")
        tag3 = users_factories.UserTagFactory(label="Ambassadeur C")
        user = users_factories.UserFactory(tags=[tag1, tag2])
        form_data = {"tags": [tag2.id, tag3.id]}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form_data, follow_redirects=True)
        assert response.status_code == 200
        assert {t.id for t in user.tags} == {tag2.id, tag3.id}
        assert html_parser.extract_alert(response.data) == "Tags mis à jour avec succès"

    def test_remove_public_account_tags(self, authenticated_client):
        tag1 = users_factories.UserTagFactory(label="Ambassadeur A")
        tag2 = users_factories.UserTagFactory(label="Ambassadeur B")
        user = users_factories.UserFactory(tags=[tag1, tag2])
        form_data = {"tags": []}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form_data, follow_redirects=True)
        assert response.status_code == 200
        assert user.tags == []
        assert html_parser.extract_alert(response.data) == "Tags mis à jour avec succès"

    def test_add_public_account_tags(self, authenticated_client):
        tag1 = users_factories.UserTagFactory(label="Ambassadeur A")
        tag2 = users_factories.UserTagFactory(label="Ambassadeur B")
        user = users_factories.UserFactory(tags=[])
        form_data = {"tags": [tag1.id, tag2.id]}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form_data, follow_redirects=True)
        assert response.status_code == 200
        assert set(user.tags) == {tag1, tag2}
        assert html_parser.extract_alert(response.data) == "Tags mis à jour avec succès"

    def test_tag_public_account_action_history_add_tag(self, authenticated_client, legit_user):
        tag_A = users_factories.UserTagFactory(label="Ambassadeur A")
        tag_B = users_factories.UserTagFactory(label="Ambassadeur B")
        user = users_factories.UserFactory(tags=[tag_A])
        form_data = {"tags": [tag_A.id, tag_B.id]}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form_data, follow_redirects=True)
        assert response.status_code == 200
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId is None
        assert action.venueId is None
        assert action.extraData["modified_info"] == {"tags": {"old_info": None, "new_info": ["Ambassadeur B"]}}

    def test_tag_public_account_action_history_remove_tag(self, authenticated_client, legit_user):
        tag_A = users_factories.UserTagFactory(label="Ambassadeur A")
        tag_B = users_factories.UserTagFactory(label="Ambassadeur B")
        user = users_factories.UserFactory(tags=[tag_A, tag_B])
        form_data = {"tags": [tag_B.id]}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form_data, follow_redirects=True)
        assert response.status_code == 200
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId is None
        assert action.venueId is None
        assert action.extraData["modified_info"] == {"tags": {"old_info": ["Ambassadeur A"], "new_info": None}}


class MarkBookingAsFraudulentTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.mark_booking_as_fraudulent"
    endpoint_kwargs = {"booking_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_FRAUDULENT_BOOKING_INFO

    def test_mark_as_fraudulent(self, authenticated_client):
        booking = bookings_factories.BookingFactory()

        response = self.post_to_endpoint(authenticated_client, form={}, booking_id=booking.id)
        assert response.status_code == 200

        fraudulent_tags = db.session.query(bookings_models.FraudulentBookingTag).all()
        assert len(fraudulent_tags) == 1
        assert fraudulent_tags[0].bookingId == booking.id


class MarkBookingAsNotFraudulentTest(PostEndpointHelper):
    endpoint = "backoffice_web.public_accounts.mark_booking_as_not_fraudulent"
    endpoint_kwargs = {"booking_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_FRAUDULENT_BOOKING_INFO

    def test_mark_as_not_fraudulent(self, authenticated_client):
        fraudulent_tag = bookings_factories.FraudulentBookingTagFactory()

        response = self.post_to_endpoint(authenticated_client, form={}, booking_id=fraudulent_tag.bookingId)
        assert response.status_code == 200

        assert db.session.query(bookings_models.FraudulentBookingTag).count() == 0
