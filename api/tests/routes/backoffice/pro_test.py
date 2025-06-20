import datetime
import logging
import re
import typing
from decimal import Decimal

import pytest
from flask import url_for

from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.geography import models as geography_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.token import SecureToken
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.backoffice.pro.forms import TypeOptions
from pcapi.utils import regions as regions_utils
from pcapi.utils import urls
from pcapi.utils.human_ids import humanize

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


class SearchProTest(search_helpers.SearchHelper, GetEndpointHelper):
    # This class performs basic search tests by inheritance
    endpoint = "backoffice_web.pro.search_pro"
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    def test_default_options(self, legit_user, authenticated_client):
        legit_user.backoffice_profile.preferences = {"departments": ["04", "05", "06"]}
        db.session.flush()

        response = authenticated_client.get(self.search_path)
        assert response.status_code == 200

        selected_departments = html_parser.extract_select_options(response.data, "departments", selected_only=True)
        assert set(selected_departments.keys()) == {"04", "05", "06"}


def assert_user_equals(result_card_text: str, expected_user: users_models.User):
    assert f"{expected_user.firstName} {expected_user.lastName} " in result_card_text
    assert f"User ID : {expected_user.id} " in result_card_text
    assert f"Email : {expected_user.email} " in result_card_text
    if expected_user.phoneNumber:
        assert f"Tél : {expected_user.phoneNumber} " in result_card_text
    assert "Pro " in result_card_text
    if not expected_user.isActive:
        assert "Suspendu " in result_card_text


def assert_offerer_equals(result_card_text: str, expected_offerer: offerers_models.Offerer):
    assert f"{expected_offerer.name.upper()} " in result_card_text
    assert f"Offerer ID : {expected_offerer.id} " in result_card_text
    assert f"SIREN : {expected_offerer.siren} " in result_card_text
    assert f"Ville : {expected_offerer.city}" in result_card_text
    assert f"Code postal : {expected_offerer.postalCode}" in result_card_text
    assert "Entité juridique " in result_card_text
    if expected_offerer.isValidated:
        assert " Validée " in result_card_text
    if expected_offerer.isRejected:
        assert " Rejetée " in result_card_text
    if not expected_offerer.isActive:
        assert " Suspendue " in result_card_text


def assert_venue_equals(result_card_text: str, expected_venue: offerers_models.Venue):
    assert f"{expected_venue.name.upper()} " in result_card_text
    assert f"Venue ID : {expected_venue.id} " in result_card_text
    assert f"SIRET : {expected_venue.siret} " in result_card_text
    assert f"Entité juridique : {expected_venue.managingOfferer.name} " in result_card_text
    assert f"Email : {expected_venue.bookingEmail} " in result_card_text
    if expected_venue.contact:
        assert f"Tél : {expected_venue.contact.phone_number} " in result_card_text
    if expected_venue.isPermanent:
        assert "Partenaire culturel permanent " in result_card_text
    else:
        assert "Partenaire culturel " in result_card_text
        assert "Partenaire culturel permanent " not in result_card_text
    if not expected_venue.managingOfferer.isActive:
        assert " Suspendu " in result_card_text


class SearchProUserTest:
    endpoint = "backoffice_web.pro.search_pro"

    # - fetch session
    # - fetch authenticated user
    expected_num_queries_when_no_query = 2
    # - fetch results
    # - fetch count for pagination
    expected_num_queries = expected_num_queries_when_no_query + 2

    def _create_accounts(
        self,
        number: int = 12,
        first_names: list[str] = ("Alice", "Bob", "Oscar"),
        last_names: list[str] = ("Martin", "Bernard", "Durand", "Dubois"),
    ):
        self.pro_accounts = []
        for i in range(number):
            first_name = first_names[i % len(first_names)]
            last_name = last_names[i % len(last_names)]

            if i % 2 == 0:
                user = users_factories.ProFactory(
                    firstName=first_name,
                    lastName=last_name,
                    email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                )
                # Associate with two offerers, this helps to check that account is returned only once
                offerers_factories.UserOffererFactory(user=user)
                offerers_factories.UserOffererFactory(user=user)
            else:
                user = users_factories.NonAttachedProFactory(
                    firstName=first_name,
                    lastName=last_name,
                    email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                )
                offerers_factories.NewUserOffererFactory(user=user)

            self.pro_accounts.append(user)

    def test_can_search_pro_by_id(self, authenticated_client):
        self._create_accounts()

        search_query = self.pro_accounts[5].id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query, pro_type=TypeOptions.USER.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.pro_user.get",
            user_id=self.pro_accounts[5].id,
            q=self.pro_accounts[5].id,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_pro_by_multiple_ids(self, authenticated_client):
        self._create_accounts()

        search_query = f" {self.pro_accounts[2].id},{self.pro_accounts[4].id}, \t{self.pro_accounts[7].id}\n"
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query, pro_type=TypeOptions.USER.name))
            assert response.status_code == 200

        cards_titles = html_parser.extract_cards_titles(response.data)
        assert set(cards_titles) == {
            self.pro_accounts[2].full_name,
            self.pro_accounts[4].full_name,
            self.pro_accounts[7].full_name,
        }

    def test_can_search_pro_by_email(self, authenticated_client):
        self._create_accounts()

        search_query = self.pro_accounts[2].email
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query, pro_type=TypeOptions.USER.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.pro_user.get",
            user_id=self.pro_accounts[2].id,
            q=self.pro_accounts[2].email,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_pro_by_last_name(self, authenticated_client):
        self._create_accounts()
        users_factories.AdminFactory(firstName="Admin", lastName="Dubois")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="Dubois", pro_type=TypeOptions.USER.name))
            assert response.status_code == 200

        cards_titles = html_parser.extract_cards_titles(response.data)
        assert set(cards_titles) == {"Alice Dubois", "Bob Dubois", "Oscar Dubois"}

    def test_can_search_pro_by_first_and_last_name(self, authenticated_client):
        self._create_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="Alice Dubois", pro_type=TypeOptions.USER.name)
            )
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.pro_user.get",
            user_id=self.pro_accounts[3].id,
            q="Alice Dubois",
            search_rank=1,
            total_items=1,
        )

    @pytest.mark.parametrize("query", ["'", '""', "*", "([{#/="])
    def test_can_search_pro_unexpected(self, authenticated_client, query):
        self._create_accounts()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query, pro_type=TypeOptions.USER.name))
            assert response.status_code == 200

        assert len(html_parser.extract_cards_text(response.data)) == 0

    def test_search_pro_with_percent_is_forbidden(self, authenticated_client):
        self._create_accounts()

        with assert_num_queries(self.expected_num_queries_when_no_query + 1):  #  rollback
            response = authenticated_client.get(url_for(self.endpoint, q="%terms", pro_type=TypeOptions.USER.name))
            assert response.status_code == 400

    def test_can_search_pro_also_beneficiary(self, authenticated_client):
        pro_beneficiary = users_factories.BeneficiaryFactory(
            firstName="Paul",
            lastName="Ochon",
            email="po@example.net",
            phoneNumber="+33740506070",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.BENEFICIARY, users_models.UserRole.PRO],
        )
        offerers_factories.UserOffererFactory(user=pro_beneficiary)

        search_query = pro_beneficiary.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query, pro_type=TypeOptions.USER.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.pro_user.get",
            user_id=pro_beneficiary.id,
            q=search_query,
            search_rank=1,
            total_items=1,
        )

    def test_search_suspended_public_account_data(self, authenticated_client):
        common_name = "Pro"
        users_factories.ProFactory(firstName=common_name)
        suspended_user = users_factories.ProFactory(firstName=common_name, isActive=False)
        now = datetime.datetime.utcnow()
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=now - datetime.timedelta(days=4),
            user=suspended_user,
            extraData={"reason": users_constants.SuspensionReason.FRAUD_USURPATION_PRO},
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_UNSUSPENDED,
            actionDate=now - datetime.timedelta(days=3),
            user=suspended_user,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=now - datetime.timedelta(days=2),
            user=suspended_user,
            extraData={"reason": users_constants.SuspensionReason.FRAUD_USURPATION_PRO},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=common_name, pro_type=TypeOptions.USER.name))
            assert response.status_code == 200

        assert "2 résultats" in html_parser.content_as_text(response.data)  # no multiple join

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2

        assert "Suspendu" not in cards_text[0]
        assert "Raison de suspension" not in cards_text[0]

        assert "Suspendu" in cards_text[1]
        assert (
            f"Raison de suspension : Fraude PRO usurpation le {suspended_user.suspension_date.strftime('%d/%m/%Y')}"
            in cards_text[1]
        )

    @pytest.mark.parametrize(
        "pro_type",
        [TypeOptions.OFFERER.name, TypeOptions.VENUE.name, TypeOptions.USER.name, TypeOptions.BANK_ACCOUNT.name],
    )
    def test_search_pro_with_empty_content(self, authenticated_client, pro_type):
        self._create_accounts()

        with assert_num_queries(self.expected_num_queries_when_no_query + 1):  #  rollback
            response = authenticated_client.get(url_for(self.endpoint, q=" ", pro_type=pro_type))
            assert response.status_code == 400


class SearchOffererTest:
    endpoint = "backoffice_web.pro.search_pro"

    # - fetch session
    # - fetch authenticated user
    # - fetch results
    # - fetch count for pagination
    expected_num_queries = 4

    def _create_offerers(
        self,
        number: int = 12,
        name_part1: list[str] = ("Librairie", "Cinéma", "Théâtre"),
        name_part2: list[str] = ("de la Gare", "de la Plage", "du Centre", "du Centaure"),
        postal_codes: list[str] = ("03000", "55000", "97100", "60000"),
    ):
        validation_statuses = list(ValidationStatus)
        self.offerers = []
        for i in range(number):
            offerer = offerers_factories.OffererFactory(
                name=f"{name_part1[i % len(name_part1)]} {name_part2[i % len(name_part2)]}",
                siren=str(123456000 + i),
                validationStatus=validation_statuses[i % len(validation_statuses)],
                isActive=bool(i % 4),
                postalCode=postal_codes[i % len(postal_codes)],
            )
            self.offerers.append(offerer)

    def test_can_search_offerer_by_id(self, authenticated_client):
        self._create_offerers()
        offerer_id = self.offerers[2].id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=offerer_id, pro_type=TypeOptions.OFFERER.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.offerer.get",
            offerer_id=offerer_id,
            q=offerer_id,
            search_rank=1,
            total_items=1,
        )

    @pytest.mark.parametrize("siren", ["123456003", "123 456 003 "])
    def test_can_search_offerer_by_siren(self, authenticated_client, siren):
        self._create_offerers()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=siren, pro_type=TypeOptions.OFFERER.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.offerer.get",
            offerer_id=self.offerers[3].id,
            q=self.offerers[3].siren,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_offerer_by_name_without_similarity(self, authenticated_client):
        self._create_offerers()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="Librairie du C", pro_type=TypeOptions.OFFERER.name)
            )
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2
        assert_offerer_equals(cards_text[0], self.offerers[6])
        assert_offerer_equals(cards_text[1], self.offerers[3])

    def test_can_search_offerer_by_words_in_name_without_similarity(self, authenticated_client):
        self._create_offerers()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="cine de plage", pro_type=TypeOptions.OFFERER.name)
            )
            assert response.status_code == 303

        assert_response_location(
            response,
            "backoffice_web.offerer.get",
            offerer_id=self.offerers[1].id,  # Cinéma de la plage
            q="cine de plage",
            search_rank=1,
            total_items=1,
        )

    def test_can_search_offerer_by_name_and_department(self, authenticated_client):
        self._create_offerers()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="Librairie", pro_type=TypeOptions.OFFERER.name, departments=["03", "971"])
            )
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2
        assert_offerer_equals(cards_text[0], self.offerers[0])  # Librairie de la Gare
        assert_offerer_equals(cards_text[1], self.offerers[6])  # Librairie du Centre

    @pytest.mark.parametrize(
        "query,departments",
        [
            ("987654321", []),
            ("festival@example.com", []),
            ("Festival de la Montagne", []),
            ("Librairie", ["62"]),
            ("Plage", ["03"]),
        ],
    )
    def test_can_search_offerer_no_result(self, authenticated_client, query, departments):
        self._create_offerers()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q=query, pro_type=TypeOptions.OFFERER.name, departments=departments)
            )
            assert response.status_code == 200

        assert len(html_parser.extract_cards_text(response.data)) == 0

    def test_can_search_caledonian_offerer_by_rid7(self, authenticated_client):
        nc_offerer = offerers_factories.CaledonianOffererFactory(siren="NC1020304")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="1020304", pro_type=TypeOptions.OFFERER.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response, "backoffice_web.offerer.get", offerer_id=nc_offerer.id, q="1020304", search_rank=1, total_items=1
        )

    def test_search_caledonian_offerer_shows_rid7(self, authenticated_client):
        offerer_1 = offerers_factories.CaledonianOffererFactory()
        offerer_2 = offerers_factories.CaledonianOffererFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="calédonienne", pro_type=TypeOptions.OFFERER.name)
            )
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2

        assert f"Offerer ID : {offerer_1.id} " in cards_text[0]
        assert "SIREN" not in cards_text[0]
        assert f"RID7 : {offerer_1.rid7} " in cards_text[0]

        assert f"Offerer ID : {offerer_2.id} " in cards_text[1]
        assert "SIREN" not in cards_text[1]
        assert f"RID7 : {offerer_2.rid7} " in cards_text[1]


class SearchVenueTest:
    endpoint = "backoffice_web.pro.search_pro"

    # - fetch session
    # - fetch authenticated user
    # - fetch results
    # - fetch count for pagination
    expected_num_queries = 4

    def _create_venues(
        self,
        number: int = 12,
        name_part1: list[str] = ("Librairie", "Cinéma", "Théâtre"),
        name_part2_admin: list[str] = ("Alpha", "Beta", "Gamma", "Delta"),
        name_part2_public: list[str] = ("de la Gare", "de la Plage", "du Centre", "du Centaure"),
        domains: list[str] = ("librairie.fr", "cinema.com", "theatre.net"),
        postal_codes: list[str] = ("74000", "97400", "98000", "80000"),
    ):
        validation_statuses = list(ValidationStatus)
        self.venues = []
        for i in range(number):
            venue = offerers_factories.VenueFactory(
                name=f"{name_part1[i % len(name_part1)]} {name_part2_admin[i % len(name_part2_admin)]}",
                publicName=f"{name_part1[i % len(name_part1)]} {name_part2_public[i % len(name_part2_public)]}",
                siret=f"123456{i:03}{i:05}",
                offererAddress=offerers_factories.OffererAddressFactory(
                    address__postalCode=postal_codes[i % len(postal_codes)],
                    address__departmentCode=regions_utils.get_department_code_from_city_code(
                        postal_codes[i % len(postal_codes)]
                    ),
                ),
                isPermanent=bool(i % 2 == 0),
                contact=None,
                managingOfferer__validationStatus=validation_statuses[i % len(validation_statuses)],
                managingOfferer__isActive=bool(i % 3),
            )
            if i % 2:
                offerers_factories.VenueContactFactory(
                    venue=venue,
                    email=f"contact{venue.id}@{domains[i % len(domains)]}",
                    phone_number=f"+331020304{i:02}",
                )
            self.venues.append(venue)

    def test_can_search_venue_by_id(self, authenticated_client):
        self._create_venues()

        venue_id = self.venues[2].id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=venue_id, pro_type=TypeOptions.VENUE.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response, "backoffice_web.venue.get", venue_id=venue_id, q=venue_id, search_rank=1, total_items=1
        )

    @pytest.mark.parametrize("siret", ["12345600300003", "123 456 003 00003"])
    def test_can_search_venue_by_siret(self, authenticated_client, siret):
        self._create_venues()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=siret, pro_type=TypeOptions.VENUE.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.venue.get",
            venue_id=self.venues[3].id,
            q=self.venues[3].siret,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_venue_by_booking_email(self, authenticated_client):
        self._create_venues()

        email = self.venues[1].bookingEmail
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=email, pro_type=TypeOptions.VENUE.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response, "backoffice_web.venue.get", venue_id=self.venues[1].id, q=email, search_rank=1, total_items=1
        )

    def test_can_search_venue_by_booking_email_domain(self, authenticated_client):
        self._create_venues()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="@librairie.fr", pro_type=TypeOptions.VENUE.name)
            )
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2  # 4 * Librairie but only odd indexes in venues have contact email
        sorted_cards_text = sorted(cards_text, key=lambda text: int(re.findall(r"Venue ID : (\d+) ", text)[0]))
        assert_venue_equals(sorted_cards_text[0], self.venues[3])  # Librairie Delta / du Centaure
        assert_venue_equals(sorted_cards_text[1], self.venues[9])  # Librairie Beta / de la Plage

    def test_can_search_venue_by_contact_email(self, authenticated_client):
        self._create_venues()

        email = self.venues[1].contact.email
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=email, pro_type=TypeOptions.VENUE.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response, "backoffice_web.venue.get", venue_id=self.venues[1].id, q=email, search_rank=1, total_items=1
        )

    def test_can_search_venue_by_name(self, authenticated_client):
        self._create_venues()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="Alpha", pro_type=TypeOptions.VENUE.name))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 3
        sorted_cards_text = sorted(cards_text, key=lambda text: int(re.findall(r"Venue ID : (\d+) ", text)[0]))
        assert_venue_equals(sorted_cards_text[0], self.venues[0])  # Librairie Alpha
        assert_venue_equals(sorted_cards_text[1], self.venues[4])  # Cinéma Alpha
        assert_venue_equals(sorted_cards_text[2], self.venues[8])  # Théâtre Alpha

    def test_can_search_venue_by_name_and_department(self, authenticated_client):
        self._create_venues()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="cinema", pro_type=TypeOptions.VENUE.name, departments=["974", "80"])
            )

        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2
        sorted_cards_text = sorted(cards_text, key=lambda text: int(re.findall(r"Venue ID : (\d+) ", text)[0]))
        assert_venue_equals(sorted_cards_text[0], self.venues[1])  # Cinéma Beta
        assert_venue_equals(sorted_cards_text[1], self.venues[7])  # Cinéma Delta

    def test_can_search_venue_by_public_name(self, authenticated_client):
        self._create_venues()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="du Centre", pro_type=TypeOptions.VENUE.name))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 3
        assert_venue_equals(cards_text[0], self.venues[2])

    def test_can_search_venue_by_words_in_public_name(self, authenticated_client):
        self._create_venues()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="Librairie Centre", pro_type=TypeOptions.VENUE.name)
            )
            assert response.status_code == 303

        assert_response_location(
            response,
            "backoffice_web.venue.get",
            venue_id=self.venues[6].id,  # Librairie du Centre
            q="Librairie Centre",
            search_rank=1,
            total_items=1,
        )

    @pytest.mark.parametrize(
        "query,expected_venue_index",
        [
            ("123a456b789c", 0),
            ("123A456B789C", 0),
            ("PRO-123a456b789c", 0),
            ("124578235689", 1),
            ("PRO-124578235689", 1),
        ],
    )
    def test_can_search_venue_by_dms_token(self, authenticated_client, query, expected_venue_index):
        self._create_venues()
        venue_ids = [
            offerers_factories.VenueFactory(dmsToken="123a456b789c").id,
            offerers_factories.VenueFactory(name="ONLY_NUM", publicName="ONLY_NUM", dmsToken="124578235689").id,
        ]

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=query, pro_type=TypeOptions.VENUE.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response,
            "backoffice_web.venue.get",
            venue_id=venue_ids[expected_venue_index],
            q=query,
            search_rank=1,
            total_items=1,
        )

    def test_can_search_caledonian_venue_by_ridet(self, authenticated_client):
        nc_venue = offerers_factories.CaledonianVenueFactory(siret="NC1020304001XX")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="1020304001", pro_type=TypeOptions.VENUE.name))
            assert response.status_code == 303

        # Redirected to single result
        assert_response_location(
            response, "backoffice_web.venue.get", venue_id=nc_venue.id, q="1020304001", search_rank=1, total_items=1
        )

    def test_search_caledonian_venue_shows_ridet(self, authenticated_client):
        venue_1 = offerers_factories.CaledonianVenueFactory()
        venue_2 = offerers_factories.CaledonianVenueFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="calédonien", pro_type=TypeOptions.VENUE.name))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2

        assert f"Venue ID : {venue_1.id} " in cards_text[0]
        assert "SIRET" not in cards_text[0]
        assert f"RIDET : {venue_1.ridet} " in cards_text[0]

        assert f"Venue ID : {venue_2.id} " in cards_text[1]
        assert "SIRET" not in cards_text[1]
        assert f"RIDET : {venue_2.ridet} " in cards_text[1]

    @pytest.mark.parametrize(
        "query,departments",
        [
            ("987654321", []),
            ("festival@example.com", []),
            ("Festival de la Montagne", []),
            ("Plage", ["74", "77"]),
        ],
    )
    def test_can_search_venue_no_result(self, authenticated_client, query, departments):
        self._create_venues()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q=query, pro_type=TypeOptions.VENUE.name, departments=departments)
            )
            assert response.status_code == 200

        assert len(html_parser.extract_cards_text(response.data)) == 0


class SearchBankAccountTest:
    endpoint = "backoffice_web.pro.search_pro"

    # session + current user (2 queries)
    # results + count in .paginate (2 queries)
    expected_num_queries = 4

    def _search_for_one(self, authenticated_client, search_query: typing.Any, expected_id: int):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q=str(search_query), pro_type=TypeOptions.BANK_ACCOUNT.name)
            )
            assert response.status_code == 303

        assert response.location == url_for(
            "backoffice_web.bank_account.get", bank_account_id=expected_id, q=str(search_query), _external=True
        )

    def test_search_bank_account_by_humanized_id(self, authenticated_client):
        bank_accounts = finance_factories.BankAccountFactory.create_batch(3)
        self._search_for_one(authenticated_client, humanize(bank_accounts[2].id), bank_accounts[2].id)

    def test_search_bank_account_by_id(self, authenticated_client):
        bank_accounts = finance_factories.BankAccountFactory.create_batch(3)
        self._search_for_one(authenticated_client, bank_accounts[2].id, bank_accounts[2].id)

    @pytest.mark.parametrize("search_query", ["FR7612345000000123456789008", "FR76 1234 5000 0001 2345 6789 008"])
    def test_search_bank_account_by_iban(self, authenticated_client, search_query):
        bank_account = finance_factories.BankAccountFactory(label="Expected", iban="FR7612345000000123456789008")
        finance_factories.BankAccountFactory(label="Other")
        self._search_for_one(authenticated_client, search_query, bank_account.id)

    def test_search_bank_account_by_invoice_reference(self, authenticated_client):
        expected_invoice = finance_factories.InvoiceFactory(
            bankAccount=finance_factories.BankAccountFactory(), reference="F250000550"
        )
        finance_factories.InvoiceFactory(bankAccount=finance_factories.BankAccountFactory(), reference="F250000551")
        self._search_for_one(authenticated_client, "F250000550", expected_invoice.bankAccountId)

    @pytest.mark.parametrize("search_query", ["123", "FR76123450000001234567890", "Mon compte", "F250000553"])
    def test_search_bank_account_no_result(self, authenticated_client, search_query):
        bank_account = finance_factories.BankAccountFactory(label="Mon compte", iban="FR7612345000000123456789008")
        finance_factories.InvoiceFactory(bankAccount=bank_account, reference="F250000550")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q=search_query, pro_type=TypeOptions.BANK_ACCOUNT.name)
            )
            assert response.status_code == 200

        assert len(html_parser.extract_cards_text(response.data)) == 0


class LogsTest:
    endpoint = "backoffice_web.pro.search_pro"

    def test_log_pro_search(self, authenticated_client, caplog):
        offerers_factories.OffererFactory(name="Log à rythme", postalCode="02302")

        with caplog.at_level(logging.INFO):
            response = authenticated_client.get(
                url_for(self.endpoint, q="rythme", pro_type=TypeOptions.OFFERER.name, departments=["02", "30"])
            )

        assert response.status_code == 303
        assert caplog.records[0].message == "PerformSearch"
        assert caplog.records[0].extra == {
            "analyticsSource": "backoffice",
            "searchType": "ProSearch",
            "searchQuery": "rythme",
            "searchDepartments": "02,30",
            "searchNbResults": 1,
            "searchProType": "offerer",
        }


class CreateOffererButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.CREATE_PRO_ENTITY
    button_label = "Créer un partenaire culturel"

    @property
    def path(self):
        return url_for("backoffice_web.pro.search_pro")


class GetCreateOffererFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.pro.get_create_offerer_form"
    needed_permission = perm_models.Permissions.CREATE_PRO_ENTITY

    def test_get_create_offerer_form(self, authenticated_client):
        url = url_for(self.endpoint)

        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(url)
            assert response.status_code == 200


@pytest.fixture(name="non_diffusible_tag")
def non_diffusible_tag_fixture():
    return offerers_factories.OffererTagFactory(name="non-diffusible", label="Non-diffusible")


class CreateOffererTest(PostEndpointHelper):
    """
    Create non-diffusible offerer and venue.
    TestingBackend is used in pcapi.connectors.entreprise => Any SIREN/SIRET starting with '9' is non-diffusible
    """

    endpoint = "backoffice_web.pro.create_offerer"
    needed_permission = perm_models.Permissions.CREATE_PRO_ENTITY

    def test_create_offerer(self, legit_user, authenticated_client, non_diffusible_tag):
        user = users_factories.NonAttachedProFactory()

        form_data = {
            "email": user.email,
            "siret": "90000000100017",
            "public_name": "Le Masque de Fer",
            "venue_type_code": offerers_models.VenueTypeCode.PERFORMING_ARTS.name,
            "web_presence": "https://www.example.com, https://offers.example.com",
            "target": offerers_models.Target.INDIVIDUAL.name,
            "ds_id": "12345",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 303

        new_offerer: offerers_models.Offerer = db.session.query(offerers_models.Offerer).one()
        assert new_offerer.siren == "900000001"
        assert new_offerer.name == form_data["public_name"]
        assert new_offerer.street == "[ND]"
        assert new_offerer.postalCode == "06400"
        assert new_offerer.city == "CANNES"
        assert new_offerer.isActive
        assert new_offerer.isNew
        assert new_offerer.tags == [non_diffusible_tag]

        new_user_offerer: offerers_models.UserOfferer = db.session.query(offerers_models.UserOfferer).one()
        assert new_user_offerer.user == user
        assert new_user_offerer.offerer == new_offerer
        assert new_user_offerer.isValidated

        new_venue: offerers_models.Venue = (
            db.session.query(offerers_models.Venue).filter_by(siret=form_data["siret"]).one()
        )
        assert new_venue.name == form_data["public_name"]
        assert new_venue.publicName == form_data["public_name"]
        assert new_venue.venueTypeCode == offerers_models.VenueTypeCode.PERFORMING_ARTS
        assert new_venue.street == "[ND]"
        assert new_venue.departementCode == "06"
        assert new_venue.postalCode == "06400"
        assert new_venue.city == "CANNES"
        assert new_venue.latitude == Decimal("43.55547")  # centroid
        assert new_venue.longitude == Decimal("7.00459")  # centroid

        new_address: geography_models.Address = db.session.query(geography_models.Address).one()
        assert new_address.street == new_venue.street == regions_utils.NON_DIFFUSIBLE_TAG
        assert new_address.city.lower() == new_venue.city.lower()
        assert new_address.postalCode == new_venue.postalCode
        assert new_address.inseeCode.startswith(new_address.departmentCode)
        assert new_address.departmentCode == "06"
        assert new_address.timezone == "Europe/Paris"

        new_offerer_address: offerers_models.OffererAddress = db.session.query(offerers_models.OffererAddress).one()
        assert new_offerer_address.addressId == new_address.id
        assert new_venue.offererAddressId == new_offerer_address.id

        venue_registration: offerers_models.VenueRegistration = db.session.query(
            offerers_models.VenueRegistration
        ).one()
        assert venue_registration.venueId == new_venue.id
        assert venue_registration.target == offerers_models.Target.INDIVIDUAL
        assert venue_registration.webPresence == form_data["web_presence"]

        assert db.session.query(history_models.ActionHistory).count() == 2

        new_offerer_action: history_models.ActionHistory = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.OFFERER_NEW)
            .one()
        )
        assert new_offerer_action.offererId == new_offerer.id
        assert new_offerer_action.userId == user.id
        assert new_offerer_action.authorUserId == legit_user.id
        assert new_offerer_action.comment == "Entité juridique créée depuis le backoffice"
        assert new_offerer_action.extraData == {
            "target": form_data["target"],
            "venue_type_code": form_data["venue_type_code"],
            "web_presence": form_data["web_presence"],
            "ds_dossier_id": int(form_data["ds_id"]),
            "sirene_info": {
                "active": True,
                "address": {"city": "CANNES", "insee_code": "06029", "postal_code": "[ND]", "street": "[ND]"},
                "ape_code": "90.01Z",
                "ape_label": "Arts du spectacle vivant",
                "creation_date": f"{datetime.date.today().year}-01-01",
                "closure_date": None,
                "diffusible": False,
                "head_office_siret": "90000000100017",
                "legal_category_code": "1000",
                "name": "[ND]",
                "siren": "900000001",
            },
        }

        new_venue_action: history_models.ActionHistory = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.VENUE_CREATED)
            .one()
        )
        assert new_venue_action.venueId == new_venue.id
        assert new_venue_action.authorUserId == legit_user.id

        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=new_offerer.id, _external=True)

    def test_cant_create_offerer_because_email_does_not_exist(self, authenticated_client):
        email = "unknown@example.com"

        form_data = {
            "email": email,
            "siret": "90000000100001",
            "public_name": "Le Masque de Fer",
            "venue_type_code": offerers_models.VenueTypeCode.PERFORMING_ARTS.name,
            "web_presence": "https://www.example.com",
            "target": offerers_models.Target.INDIVIDUAL_AND_EDUCATIONAL.name,
            "ds_id": "12345",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == [f"Aucun compte pro n'existe avec l'adresse {email}"]

    def test_cant_create_offerer_because_email_is_not_pro(self, authenticated_client):
        user = users_factories.UserFactory()

        form_data = {
            "email": user.email,
            "siret": "90000000100001",
            "public_name": "Le Masque de Fer",
            "venue_type_code": offerers_models.VenueTypeCode.PERFORMING_ARTS.name,
            "web_presence": "https://www.example.com",
            "target": offerers_models.Target.EDUCATIONAL.name,
            "ds_id": "12345",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == [f"Aucun compte pro n'existe avec l'adresse {user.email}"]

    def test_cant_create_offerer_which_already_exists(self, authenticated_client):
        offerers_factories.OffererFactory(siren="900000001")

        form_data = {
            "email": users_factories.NonAttachedProFactory().email,
            "siret": "90000000100001",
            "public_name": "Le Masque de Fer",
            "venue_type_code": offerers_models.VenueTypeCode.PERFORMING_ARTS.name,
            "web_presence": "https://www.example.com",
            "target": offerers_models.Target.INDIVIDUAL.name,
            "ds_id": "12345",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == [
            "Une entité juridique existe déjà avec le SIREN 900000001"
        ]

    @pytest.mark.parametrize(
        "siret,expected_warning",
        [
            ("00000000000001", "Le SIRET 00000000000001 n'existe pas"),
            ("90009900000001", "L'établissement portant le SIRET 90009900000001 est fermé"),
            (
                "12345678900001",
                "L'établissement portant le SIRET 12345678900001 est diffusible, l'acteur culturel peut créer l'entité juridique sur PC Pro",
            ),
        ],
    )
    def test_cant_create_offerer_because_of_insee_status(self, authenticated_client, siret, expected_warning):
        user = users_factories.NonAttachedProFactory()

        form_data = {
            "email": user.email,
            "siret": siret,
            "public_name": "Le Masque de Fer",
            "venue_type_code": offerers_models.VenueTypeCode.PERFORMING_ARTS.name,
            "web_presence": "https://www.example.com, https://offers.example.com",
            "target": offerers_models.Target.INDIVIDUAL.name,
            "ds_id": "12345",
        }

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == [expected_warning]

        assert db.session.query(offerers_models.Offerer).count() == 0
        assert db.session.query(offerers_models.Venue).count() == 0
        assert db.session.query(offerers_models.VenueRegistration).count() == 0
        assert db.session.query(history_models.ActionHistory).count() == 0

    @pytest.mark.parametrize("missing_field", ["public_name", "venue_type_code", "target", "ds_id"])
    def test_cant_create_offerer_because_of_missing_field(self, authenticated_client, missing_field):
        form_data = {
            "email": users_factories.NonAttachedProFactory().email,
            "siret": "90000000100001",
            "public_name": "Le Masque de Fer",
            "venue_type_code": offerers_models.VenueTypeCode.PERFORMING_ARTS.name,
            "web_presence": "https://www.example.com",
            "target": offerers_models.Target.EDUCATIONAL.name,
            "ds_id": "12345",
        }
        form_data[missing_field] = ""

        response = self.post_to_endpoint(authenticated_client, form=form_data)
        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == ["Information obligatoire"]


class ConnectAsProUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.pro.connect_as"
    needed_permission = perm_models.Permissions.CONNECT_AS_PRO
    # session
    # current user
    # pro user data
    expected_num_queries = 3

    @pytest.mark.parametrize("roles", [[users_models.UserRole.PRO], [users_models.UserRole.NON_ATTACHED_PRO]])
    def test_connect_as_user(self, authenticated_client, legit_user, roles):
        user = users_factories.ProFactory(roles=roles)

        form_data = {"object_type": "user", "object_id": user.id, "redirect": "/"}
        expected_token_data = {
            "user_id": user.id,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        # check url form
        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_user_invalid_redirect(self, authenticated_client, legit_user):
        user = users_factories.ProFactory()

        form_data = {"object_type": "user", "object_id": user.id, "redirect": "http://example.com/pouet"}

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        # check url form
        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Échec de la validation de sécurité, veuillez réessayer"
        )

    def test_connect_as_user_invalid_object_type(self, authenticated_client, legit_user):
        user = users_factories.ProFactory()

        form_data = {"object_type": "pouet", "object_id": user.id, "redirect": "/deposit"}

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        # check url form
        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Échec de la validation de sécurité, veuillez réessayer"
        )

    def test_connect_as_user_not_found(self, authenticated_client):
        form_data = {"object_type": "user", "object_id": 0, "redirect": "/"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )
        assert response.status_code == 404

    def test_connect_as_inactive_user(self, authenticated_client):
        user = users_factories.ProFactory(isActive=False)

        form_data = {"object_type": "user", "object_id": user.id, "redirect": "/"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "L'utilisation du « connect as » n'est pas disponible pour les comptes inactifs"
        )

    @pytest.mark.parametrize(
        "roles,warning",
        [
            (
                [users_models.UserRole.PRO, users_models.UserRole.ADMIN],
                "L'utilisation du « connect as » n'est pas disponible pour les comptes admin",
            ),
            (
                [users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED],
                "L'utilisation du « connect as » n'est pas disponible pour les comptes anonymisés",
            ),
            ([], ""),
        ],
    )
    def test_connect_as_uneligible_user(self, authenticated_client, roles, warning):
        user = users_factories.UserFactory(roles=roles)

        form_data = {"object_type": "user", "object_id": user.id, "redirect": "/"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for transaction rollback
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        if warning:
            redirected_response = authenticated_client.get(response.location)
            assert html_parser.extract_alert(redirected_response.data) == warning

    def test_connect_as_venue(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerers_factories.UserOffererFactory().offerer,
        )

        form_data = {"object_type": "venue", "object_id": venue.id, "redirect": "/venue"}
        expected_token_data = {
            "user_id": venue.managingOfferer.UserOfferers[0].userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/venue",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_venue_without_user(self, authenticated_client):
        venue = offerers_factories.VenueFactory()

        form_data = {"object_type": "venue", "object_id": venue.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            # +1 for rollback query
            expected_num_queries=self.expected_num_queries + 1,
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à ce partenaire culturel"
        )

    def test_connect_as_venue_not_found(self, authenticated_client):
        form_data = {"object_type": "venue", "object_id": 0, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            # +1 for rollback query
            expected_num_queries=self.expected_num_queries + 1,
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à ce partenaire culturel"
        )

    def test_connect_as_venue_without_active_user(self, authenticated_client):
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerers_factories.UserOffererFactory(
                user__isActive=False,
            ).offerer,
        )

        form_data = {"object_type": "venue", "object_id": venue.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            # +1 for rollback query
            expected_num_queries=self.expected_num_queries + 1,
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à ce partenaire culturel"
        )

    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.PRO, users_models.UserRole.ADMIN],
            [users_models.UserRole.ADMIN],
            [users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED],
        ],
    )
    def test_connect_as_venue_without_eligible_user(self, authenticated_client, roles):
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerers_factories.UserOffererFactory(
                user__roles=roles,
            ).offerer
        )
        form_data = {"object_type": "venue", "object_id": venue.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            # +1 for rollback query
            expected_num_queries=self.expected_num_queries + 1,
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à ce partenaire culturel"
        )

    def test_connect_as_venue_user_has_multiple_offerer(self, authenticated_client, legit_user):
        hidden_user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(user=hidden_user_offerer.user)
        user_offerer = offerers_factories.UserOffererFactory(offerer=hidden_user_offerer.offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        form_data = {"object_type": "venue", "object_id": venue.id, "redirect": "/venue"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/venue",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_offerer(self, authenticated_client, legit_user):
        user_offerer = offerers_factories.UserOffererFactory()
        form_data = {"object_type": "offerer", "object_id": user_offerer.offerer.id, "redirect": "/venue"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/venue",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_offerer_without_user(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        form_data = {"object_type": "offerer", "object_id": offerer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette entité juridique"
        )

    def test_connect_as_offerer_not_found(self, authenticated_client):
        form_data = {"object_type": "offerer", "object_id": 0, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette entité juridique"
        )

    def test_connect_as_offerer_without_active_user(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__isActive=False,
        )

        form_data = {"object_type": "offerer", "object_id": user_offerer.offerer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette entité juridique"
        )

    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.PRO, users_models.UserRole.ADMIN],
            [users_models.UserRole.ADMIN],
            [users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED],
        ],
    )
    def test_connect_as_offerer_without_eligible_user(self, authenticated_client, roles):
        user_offerer = offerers_factories.UserOffererFactory(
            user__roles=roles,
        )
        form_data = {"object_type": "offerer", "object_id": user_offerer.offerer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette entité juridique"
        )

    def test_connect_as_offerer_user_has_multiple_offerer(self, authenticated_client, legit_user):
        hidden_user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(user=hidden_user_offerer.user)
        user_offerer = offerers_factories.UserOffererFactory(offerer=hidden_user_offerer.offerer)

        form_data = {"object_type": "offerer", "object_id": user_offerer.offerer.id, "redirect": "/venue"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/venue",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_offer(self, authenticated_client, legit_user):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(
            venue__managingOfferer=user_offerer.offerer,
        )
        form_data = {"object_type": "offer", "object_id": offer.id, "redirect": "/venue"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/venue",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_offer_without_user(self, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_data = {"object_type": "offer", "object_id": offer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre"
        )

    def test_connect_as_offer_not_found(self, authenticated_client):
        form_data = {"object_type": "offer", "object_id": 0, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre"
        )

    def test_connect_as_offer_without_active_user(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__isActive=False,
        )
        offer = offers_factories.OfferFactory(
            venue__managingOfferer=user_offerer.offerer,
        )

        form_data = {"object_type": "offer", "object_id": offer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre"
        )

    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.PRO, users_models.UserRole.ADMIN],
            [users_models.UserRole.ADMIN],
            [users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED],
        ],
    )
    def test_connect_as_offer_without_eligible_user(self, authenticated_client, roles):
        user_offerer = offerers_factories.UserOffererFactory(
            user__roles=roles,
        )
        offer = offers_factories.OfferFactory(
            venue__managingOfferer=user_offerer.offerer,
        )
        form_data = {"object_type": "offer", "object_id": offer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre"
        )

    def test_connect_as_offer_user_has_multiple_offerer(self, authenticated_client, legit_user):
        hidden_user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(user=hidden_user_offerer.user)
        user_offerer = offerers_factories.UserOffererFactory(offerer=hidden_user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        form_data = {"object_type": "offer", "object_id": offer.id, "redirect": "/offer"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/offer",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_bank_account(self, authenticated_client, legit_user):
        bank_account = finance_factories.BankAccountFactory(offerer=offerers_factories.UserOffererFactory().offerer)

        form_data = {"object_type": "bank_account", "object_id": bank_account.id, "redirect": "/bank_account"}
        expected_token_data = {
            "user_id": bank_account.offerer.UserOfferers[0].userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/bank_account",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_bank_account_without_user(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()

        form_data = {"object_type": "bank_account", "object_id": bank_account.id, "redirect": "/bank_account"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à ce compte bancaire"
        )

    def test_connect_as_bank_account_not_found(self, authenticated_client):
        form_data = {"object_type": "bank_account", "object_id": 0, "redirect": "/bank_account"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à ce compte bancaire"
        )

    def test_connect_as_bank_account_without_active_user(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory(
            offerer=offerers_factories.UserOffererFactory(
                user__isActive=False,
            ).offerer
        )

        form_data = {"object_type": "bank_account", "object_id": bank_account.id, "redirect": "/bank_account"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à ce compte bancaire"
        )

    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.PRO, users_models.UserRole.ADMIN],
            [users_models.UserRole.ADMIN],
            [users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED],
        ],
    )
    def test_connect_as_bank_account_without_eligible_user(self, authenticated_client, roles):
        bank_account = finance_factories.BankAccountFactory(
            offerer=offerers_factories.UserOffererFactory(
                user__roles=roles,
            ).offerer
        )
        form_data = {"object_type": "bank_account", "object_id": bank_account.id, "redirect": "/bank_account"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à ce compte bancaire"
        )

    def test_connect_as_bank_account_user_has_multiple_offerer(self, authenticated_client, legit_user):
        hidden_user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(user=hidden_user_offerer.user)
        user_offerer = offerers_factories.UserOffererFactory(offerer=hidden_user_offerer.offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=user_offerer.offerer)
        form_data = {"object_type": "bank_account", "object_id": bank_account.id, "redirect": "/bank_account"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/bank_account",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_collective_offer(self, authenticated_client, legit_user):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
        )
        form_data = {"object_type": "collective_offer", "object_id": offer.id, "redirect": "/venue"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/venue",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_collective_offer_without_user(self, authenticated_client):
        offer = educational_factories.CollectiveOfferFactory()

        form_data = {"object_type": "collective_offer", "object_id": offer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective"
        )

    def test_connect_as_collective_offer_not_found(self, authenticated_client):
        form_data = {"object_type": "collective_offer", "object_id": 0, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective"
        )

    def test_connect_as_collective_offer_without_active_user(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__isActive=False,
        )
        offer = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
        )

        form_data = {"object_type": "collective_offer", "object_id": offer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective"
        )

    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.PRO, users_models.UserRole.ADMIN],
            [users_models.UserRole.ADMIN],
            [users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED],
        ],
    )
    def test_connect_as_collective_offer_without_eligible_user(self, authenticated_client, roles):
        user_offerer = offerers_factories.UserOffererFactory(
            user__roles=roles,
        )
        offer = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
        )
        form_data = {"object_type": "collective_offer", "object_id": offer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective"
        )

    def test_connect_as_collective_offer_user_has_multiple_offerer(self, authenticated_client, legit_user):
        hidden_user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(user=hidden_user_offerer.user)
        user_offerer = offerers_factories.UserOffererFactory(offerer=hidden_user_offerer.offerer)
        offer = educational_factories.CollectiveOfferFactory(venue__managingOfferer=user_offerer.offerer)
        form_data = {"object_type": "collective_offer", "object_id": offer.id, "redirect": "/venue"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/venue",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_collective_offer_template(self, authenticated_client, legit_user):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            venue__managingOfferer=user_offerer.offerer,
        )
        form_data = {"object_type": "collective_offer_template", "object_id": offer.id, "redirect": "/venue"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/venue",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    def test_connect_as_collective_offer_template_without_user(self, authenticated_client):
        offer = educational_factories.CollectiveOfferTemplateFactory()

        form_data = {"object_type": "collective_offer_template", "object_id": offer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective vitrine"
        )

    def test_connect_as_collective_offer_template_not_found(self, authenticated_client):
        form_data = {"object_type": "collective_offer_template", "object_id": 0, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective vitrine"
        )

    def test_connect_as_collective_offer_template_without_active_user(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__isActive=False,
        )
        offer = educational_factories.CollectiveOfferTemplateFactory(
            venue__managingOfferer=user_offerer.offerer,
        )

        form_data = {"object_type": "collective_offer_template", "object_id": offer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective vitrine"
        )

    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.PRO, users_models.UserRole.ADMIN],
            [users_models.UserRole.ADMIN],
            [users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED],
        ],
    )
    def test_connect_as_collective_offer_template_without_eligible_user(self, authenticated_client, roles):
        user_offerer = offerers_factories.UserOffererFactory(
            user__roles=roles,
        )
        offer = educational_factories.CollectiveOfferTemplateFactory(
            venue__managingOfferer=user_offerer.offerer,
        )
        form_data = {"object_type": "collective_offer_template", "object_id": offer.id, "redirect": "/venue"}
        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries + 1,  # +1 for rollback query
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.home", _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective vitrine"
        )

    def test_connect_as_collective_offer_template_user_has_multiple_offerer(self, authenticated_client, legit_user):
        hidden_user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserOffererFactory(user=hidden_user_offerer.user)
        user_offerer = offerers_factories.UserOffererFactory(offerer=hidden_user_offerer.offerer)
        offer = educational_factories.CollectiveOfferTemplateFactory(venue__managingOfferer=user_offerer.offerer)
        form_data = {"object_type": "collective_offer_template", "object_id": offer.id, "redirect": "/venue"}
        expected_token_data = {
            "user_id": user_offerer.userId,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL + "/venue",
        }

        response = self.post_to_endpoint(
            authenticated_client,
            form=form_data,
            expected_num_queries=self.expected_num_queries,
        )

        assert response.status_code == 303
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data
