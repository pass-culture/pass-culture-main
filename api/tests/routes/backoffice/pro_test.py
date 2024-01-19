import logging
import re
import typing

from flask import url_for
import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.backoffice.forms.search import TypeOptions
from pcapi.utils.human_ids import humanize

from .helpers import html_parser
from .helpers import search as search_helpers
from .helpers.get import GetEndpointHelper
from .helpers.url import assert_response_location


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class SearchProTest(search_helpers.SearchHelper, GetEndpointHelper):
    # This class performs basic search tests by inheritance
    endpoint = "backoffice_web.search_pro"
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
    assert "Structure " in result_card_text
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
    assert f"Structure : {expected_venue.managingOfferer.name} " in result_card_text
    assert f"Email : {expected_venue.bookingEmail} " in result_card_text
    if expected_venue.contact:
        assert f"Tél : {expected_venue.contact.phone_number} " in result_card_text
    if expected_venue.isPermanent:
        assert "Lieu permanent " in result_card_text
    else:
        assert "Lieu " in result_card_text
        assert "Lieu permanent " not in result_card_text
    if not expected_venue.managingOfferer.isActive:
        assert " Suspendu " in result_card_text


class SearchProUserTest:
    endpoint = "backoffice_web.search_pro"

    # - fetch session
    # - fetch authenticated user
    # - fetch feature flags
    expected_num_queries_when_no_query = 3
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
                offerers_factories.NotValidatedUserOffererFactory(user=user)

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

        with assert_num_queries(self.expected_num_queries_when_no_query):
            response = authenticated_client.get(url_for(self.endpoint, q="%terms", pro_type=TypeOptions.USER.name))
            assert response.status_code == 400

    def test_can_search_pro_also_beneficiary(self, authenticated_client):
        pro_beneficiary = users_factories.BeneficiaryGrant18Factory(
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


class SearchOffererTest:
    endpoint = "backoffice_web.search_pro"

    # - fetch session
    # - fetch authenticated user
    # - fetch results
    # - fetch count for pagination
    # - fetch feature flags
    expected_num_queries = 5

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

    def test_can_search_offerer_by_name(self, authenticated_client):
        self._create_offerers()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="Théâtre du Centre", pro_type=TypeOptions.OFFERER.name)
            )
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) >= 2  # Results may contain all "Théâtre", "Centre", "Centaure"
        assert len(cards_text) <= 8  # Results should not contain Libraire/Cinéma + Gare/Plage
        assert_offerer_equals(cards_text[0], self.offerers[2])  # Théâtre du Centre (most relevant)
        assert_offerer_equals(cards_text[1], self.offerers[11])  # Théâtre du Centaure (very close to the first one)

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


class SearchVenueTest:
    endpoint = "backoffice_web.search_pro"

    # - fetch session
    # - fetch authenticated user
    # - fetch results
    # - fetch count for pagination
    # - fetch all feature flags
    expected_num_queries = 5

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
                postalCode=postal_codes[i % len(postal_codes)],
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
        sorted_cards_text = sorted(cards_text, key=lambda text: re.findall(r"Venue ID : \d+ ", text)[0])
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
        sorted_cards_text = sorted(cards_text, key=lambda text: re.findall(r"Venue ID : \d+ ", text)[0])
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
        sorted_cards_text = sorted(cards_text, key=lambda text: re.findall(r"Venue ID : \d+ ", text)[0])
        assert_venue_equals(sorted_cards_text[0], self.venues[1])  # Cinéma Beta
        assert_venue_equals(sorted_cards_text[1], self.venues[7])  # Cinéma Delta

    def test_can_search_venue_by_public_name(self, authenticated_client):
        self._create_venues()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="Théâtre du Centre", pro_type=TypeOptions.VENUE.name)
            )
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) >= 2  # Results may contain all "Théâtre", "Centre", "Centaure"
        assert len(cards_text) <= 8  # Results should not contain Libraire/Cinéma + Gare/Plage
        assert_venue_equals(cards_text[0], self.venues[2])  # Théâtre du Centre (most relevant)
        assert_venue_equals(cards_text[1], self.venues[11])  # Théâtre du Centaure (very close to the first one)

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

    @pytest.mark.parametrize(
        "query,departments",
        [("987654321", []), ("festival@example.com", []), ("Festival de la Montagne", []), ("Plage", ["74", "77"])],
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
    endpoint = "backoffice_web.search_pro"

    # session + current user (2 queries)
    # results + count in .paginate (2 queries)
    # get feature flag WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY (1 query)
    expected_num_queries = 5

    def _search_for_one(self, authenticated_client, search_query: typing.Any, expected_id: int):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q=str(search_query), pro_type=TypeOptions.BANK_ACCOUNT.name)
            )
            assert response.status_code == 303

        assert response.location == url_for(
            "backoffice_web.bank_account.get", bank_account_id=expected_id, q=str(search_query), _external=True
        )

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_search_bank_account_by_humanized_id(self, authenticated_client):
        bank_accounts = finance_factories.BankAccountFactory.create_batch(3)
        self._search_for_one(authenticated_client, humanize(bank_accounts[2].id), bank_accounts[2].id)

    @pytest.mark.parametrize("search_query", ["FR7612345000000123456789008", "FR76 1234 5000 0001 2345 6789 008"])
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_search_bank_account_by_iban(self, authenticated_client, search_query):
        bank_account = finance_factories.BankAccountFactory(label="Expected", iban="FR7612345000000123456789008")
        finance_factories.BankAccountFactory(label="Other")
        self._search_for_one(authenticated_client, search_query, bank_account.id)

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_search_bank_account_by_id_not_available(self, authenticated_client):
        bank_account = finance_factories.BankAccountFactory()
        search_query = bank_account.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q=search_query, pro_type=TypeOptions.BANK_ACCOUNT.name)
            )
            assert response.status_code == 200

        assert len(html_parser.extract_cards_text(response.data)) == 0

    @pytest.mark.parametrize("search_query", ["123", "FR76123450000001234567890", "Mon compte"])
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
    def test_search_bank_account_no_result(self, authenticated_client, search_query):
        finance_factories.BankAccountFactory(label="Mon compte", iban="FR7612345000000123456789008")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q=search_query, pro_type=TypeOptions.BANK_ACCOUNT.name)
            )
            assert response.status_code == 200

        assert len(html_parser.extract_cards_text(response.data)) == 0


class LogsTest:
    endpoint = "backoffice_web.search_pro"

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
