import re

from flask import url_for
import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models.validation_status_mixin import ValidationStatus

from .helpers import html_parser
from .helpers import search as search_helpers
from .helpers.get import GetEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class SearchProUnauthorizedTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.search_pro"
    needed_permission = perm_models.Permissions.SEARCH_PRO_ACCOUNT


class SearchProTest(search_helpers.SearchHelper):
    # This class performs basic search tests by inheritance
    endpoint = "backoffice_v3_web.search_pro"


def assert_user_equals(result_card_text: str, expected_user: users_models.User):
    assert f"{expected_user.firstName} {expected_user.lastName} " in result_card_text
    assert f"User ID : {expected_user.id} " in result_card_text
    assert f"E-mail : {expected_user.email} " in result_card_text
    if expected_user.phoneNumber:
        assert f"Tél : {expected_user.phoneNumber} " in result_card_text
    assert "Pro " in result_card_text
    if not expected_user.isActive:
        assert "Suspendu " in result_card_text


def assert_offerer_equals(result_card_text: str, expected_offerer: offerers_models.Offerer):
    assert f"{expected_offerer.name.upper()} " in result_card_text
    assert f"Offerer ID : {expected_offerer.id} " in result_card_text
    assert f"SIREN : {expected_offerer.siren} " in result_card_text
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
    assert f"E-mail : {expected_venue.bookingEmail} " in result_card_text
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
    endpoint = "backoffice_v3_web.search_pro"

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
        # given
        self._create_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=self.pro_accounts[5].id, pro_type="user"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], self.pro_accounts[5])

    def test_can_search_pro_by_email(self, authenticated_client):
        # given
        self._create_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=self.pro_accounts[2].email, pro_type="user"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], self.pro_accounts[2])

    def test_can_search_pro_by_last_name(self, authenticated_client):
        # given
        self._create_accounts()
        users_factories.AdminFactory(firstName="Admin", lastName="Dubois")

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="Dubois", pro_type="user"))

        # then
        assert response.status_code == 200
        cards_titles = html_parser.extract_cards_titles(response.data)
        assert set(cards_titles) == {"Alice Dubois", "Bob Dubois", "Oscar Dubois"}

    def test_can_search_pro_by_first_and_last_name(self, authenticated_client):
        # given
        self._create_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="Alice Dubois", pro_type="user"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], self.pro_accounts[3])

    @pytest.mark.parametrize("query", ["'", '""', "*", "([{#/="])
    def test_can_search_pro_unexpected(self, authenticated_client, query):
        # given
        self._create_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=query, pro_type="user"))

        # then
        assert response.status_code == 200
        assert len(html_parser.extract_cards_text(response.data)) == 0

    def test_search_pro_with_percent_is_forbidden(self, authenticated_client):
        # given
        self._create_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="%terms", pro_type="user"))

        # then
        assert response.status_code == 400

    def test_can_search_pro_also_beneficiary(self, authenticated_client):
        # given
        pro_beneficiary = users_factories.BeneficiaryGrant18Factory(
            firstName="Paul",
            lastName="Ochon",
            email="po@example.net",
            phoneNumber="+33740506070",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            roles=[users_models.UserRole.BENEFICIARY, users_models.UserRole.PRO],
        )
        offerers_factories.UserOffererFactory(user=pro_beneficiary)

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=pro_beneficiary.id, pro_type="user"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], pro_beneficiary)


class SearchOffererTest:
    endpoint = "backoffice_v3_web.search_pro"

    def _create_offerers(
        self,
        number: int = 12,
        name_part1: list[str] = ("Librairie", "Cinéma", "Théâtre"),
        name_part2: list[str] = ("de la Gare", "de la Plage", "du Centre", "du Centaure"),
    ):
        validation_statuses = list(ValidationStatus)
        self.offerers = []
        for i in range(number):
            offerer = offerers_factories.OffererFactory(
                name=f"{name_part1[i % len(name_part1)]} {name_part2[i % len(name_part2)]}",
                siren=str(123456000 + i),
                validationStatus=validation_statuses[i % len(validation_statuses)],
                isActive=bool(i % 4),
            )
            self.offerers.append(offerer)

    def test_can_search_offerer_by_id(self, authenticated_client):
        # given
        self._create_offerers()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=self.offerers[2].id, pro_type="offerer"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_offerer_equals(cards_text[0], self.offerers[2])

    def test_can_search_offerer_by_siren(self, authenticated_client):
        # given
        self._create_offerers()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=self.offerers[3].siren, pro_type="offerer"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_offerer_equals(cards_text[0], self.offerers[3])

    def test_can_search_offerer_by_name(self, authenticated_client):
        # given
        self._create_offerers()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="Théâtre du Centre", pro_type="offerer"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) >= 2  # Results may contain all "Théâtre", "Centre", "Centaure"
        assert len(cards_text) <= 8  # Results should not contain Libraire/Cinéma + Gare/Plage
        assert_offerer_equals(cards_text[0], self.offerers[2])  # Théâtre du Centre (most relevant)
        assert_offerer_equals(cards_text[1], self.offerers[11])  # Théâtre du Centaure (very close to the first one)

    @pytest.mark.parametrize("query", ["987654321", "festival@example.com", "Festival de la Montagne"])
    def test_can_search_offerer_no_result(self, authenticated_client, query):
        # given
        self._create_offerers()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=query, pro_type="offerer"))

        # then
        assert response.status_code == 200
        assert len(html_parser.extract_cards_text(response.data)) == 0


class SearchVenueTest:
    endpoint = "backoffice_v3_web.search_pro"

    def _create_venues(
        self,
        number: int = 12,
        name_part1: list[str] = ("Librairie", "Cinéma", "Théâtre"),
        name_part2_admin: list[str] = ("Alpha", "Beta", "Gamma", "Delta"),
        name_part2_public: list[str] = ("de la Gare", "de la Plage", "du Centre", "du Centaure"),
        domains: list[str] = ("librairie.fr", "cinema.com", "theatre.net"),
    ):
        validation_statuses = list(ValidationStatus)
        self.venues = []
        for i in range(number):
            venue = offerers_factories.VenueFactory(
                name=f"{name_part1[i % len(name_part1)]} {name_part2_admin[i % len(name_part2_admin)]}",
                publicName=f"{name_part1[i % len(name_part1)]} {name_part2_public[i % len(name_part2_public)]}",
                siret=f"123456{i:03}{i:05}",
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
        # given
        self._create_venues()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=self.venues[2].id, pro_type="venue"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_venue_equals(cards_text[0], self.venues[2])

    def test_can_search_venue_by_siret(self, authenticated_client):
        # given
        self._create_venues()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=self.venues[3].siret, pro_type="venue"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_venue_equals(cards_text[0], self.venues[3])

    def test_can_search_venue_by_booking_email(self, authenticated_client):
        # given
        self._create_venues()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=self.venues[1].bookingEmail, pro_type="venue"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_venue_equals(cards_text[0], self.venues[1])

    def test_can_search_venue_by_booking_email_domain(self, authenticated_client):
        # given
        self._create_venues()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="@librairie.fr", pro_type="venue"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2  # 4 * Librairie but only odd indexes in venues have contact email
        sorted_cards_text = sorted(cards_text, key=lambda text: re.findall(r"Venue ID : \d+ ", text)[0])
        assert_venue_equals(sorted_cards_text[0], self.venues[3])  # Librairie Delta / du Centaure
        assert_venue_equals(sorted_cards_text[1], self.venues[9])  # Librairie Beta / de la Plage

    def test_can_search_venue_by_contact_email(self, authenticated_client):
        # given
        self._create_venues()

        # when
        response = authenticated_client.get(
            url_for(self.endpoint, terms=self.venues[1].contact.email, pro_type="venue")
        )

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_venue_equals(cards_text[0], self.venues[1])

    def test_can_search_venue_by_name(self, authenticated_client):
        # given
        self._create_venues()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="Alpha", pro_type="venue"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 3
        sorted_cards_text = sorted(cards_text, key=lambda text: re.findall(r"Venue ID : \d+ ", text)[0])
        assert_venue_equals(sorted_cards_text[0], self.venues[0])  # Librairie Alpha
        assert_venue_equals(sorted_cards_text[1], self.venues[4])  # Cinéma Alpha
        assert_venue_equals(sorted_cards_text[2], self.venues[8])  # Théâtre Alpha

    def test_can_search_venue_by_public_name(self, authenticated_client):
        # given
        self._create_venues()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="Théâtre du Centre", pro_type="venue"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) >= 2  # Results may contain all "Théâtre", "Centre", "Centaure"
        assert len(cards_text) <= 8  # Results should not contain Libraire/Cinéma + Gare/Plage
        assert_venue_equals(cards_text[0], self.venues[2])  # Théâtre du Centre (most relevant)
        assert_venue_equals(cards_text[1], self.venues[11])  # Théâtre du Centaure (very close to the first one)

    @pytest.mark.parametrize("query", ["987654321", "festival@example.com", "Festival de la Montagne"])
    def test_can_search_venue_no_result(self, authenticated_client, query):
        # given
        self._create_venues()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=query, pro_type="venue"))

        # then
        assert response.status_code == 200
        assert len(html_parser.extract_cards_text(response.data)) == 0
