from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions.models import Permissions
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


pytestmark = pytest.mark.usefixtures("db_session")


def assert_user_equals(found_user: dict, expected_user: users_models.User):
    assert found_user["resourceType"] == "proUser"
    assert found_user["id"] == expected_user.id
    assert found_user["payload"]["firstName"] == expected_user.firstName
    assert found_user["payload"]["lastName"] == expected_user.lastName
    assert found_user["payload"]["email"] == expected_user.email
    assert found_user["payload"]["phoneNumber"] == expected_user.phoneNumber


def assert_offerer_equals(found_offerer: dict, expected_offerer: offerers_models.Offerer):
    assert found_offerer["resourceType"] == "offerer"
    assert found_offerer["id"] == expected_offerer.id
    assert found_offerer["payload"]["siren"] == expected_offerer.siren
    assert found_offerer["payload"]["name"] == expected_offerer.name


def assert_venue_equals(found_venue: dict, expected_venue: offerers_models.Venue):
    assert found_venue["resourceType"] == "venue"
    assert found_venue["id"] == expected_venue.id
    assert found_venue["payload"]["siret"] == expected_venue.siret
    assert found_venue["payload"]["name"] == expected_venue.name
    assert (
        found_venue["payload"]["email"] == expected_venue.contact.email
        if expected_venue.contact and expected_venue.contact.email
        else expected_venue.bookingEmail
    )
    assert found_venue["payload"]["permanent"] == expected_venue.isPermanent


class ProSearchUserTest:
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
            url_for("backoffice_blueprint.search_pro", q=self.pro_accounts[5].id, type="proUser"),
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
            url_for("backoffice_blueprint.search_pro", q=self.pro_accounts[2].email, type="proUser"),
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
            url_for("backoffice_blueprint.search_pro", q="Dubois", type="proUser"),
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
            url_for("backoffice_blueprint.search_pro", q="Alice Dubois", type="proUser"),
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
            url_for("backoffice_blueprint.search_pro", q="", type="proUser"),
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
            url_for("backoffice_blueprint.search_pro", q=query, type="proUser"),
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
            url_for("backoffice_blueprint.search_pro", q=pro_beneficiary.id, type="proUser"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_user_equals(response_list[0], pro_beneficiary)


class ProSearchOffererTest:
    def _create_offerers(
        self,
        number: int = 12,
        name_part1: list[str] = ("Librairie", "Cinéma", "Théâtre"),
        name_part2: list[str] = ("de la Gare", "de la Plage", "du Centre", "du Centaure"),
    ) -> None:
        self.offerers = []
        for i in range(number):
            offerer = offerers_factories.OffererFactory(
                name=f"{name_part1[i % len(name_part1)]} {name_part2[i % len(name_part2)]}",
                siren=str(123456000 + i),
            )
            self.offerers.append(offerer)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_offerer_by_id(self, client):
        # given
        self._create_offerers()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=self.offerers[2].id, type="offerer"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_offerer_equals(response_list[0], self.offerers[2])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_offerer_by_siren(self, client):
        # given
        self._create_offerers()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=self.offerers[3].siren, type="offerer"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_offerer_equals(response_list[0], self.offerers[3])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_offerer_by_name(self, client):
        # given
        self._create_offerers()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="Théâtre du Centre", type="offerer"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) >= 2  # Results may contain all "Théâtre", "Centre", "Centaure"
        assert len(response_list) <= 8  # Results should not contain Libraire/Cinéma + Gare/Plage
        assert_offerer_equals(response_list[0], self.offerers[2])  # Théâtre du Centre (most relevant)
        assert_offerer_equals(response_list[1], self.offerers[11])  # Théâtre du Centaure (very close to the first one)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_by_two_consistent_criteria(self, client):
        # given
        self._create_offerers()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for(
                "backoffice_blueprint.search_pro", q=f"{self.offerers[2].siren} {self.offerers[2].name}", type="offerer"
            ),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1  # Single result because only one is matching SIREN even if name is close
        assert_offerer_equals(response_list[0], self.offerers[2])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_by_two_unconsistent_criteria(self, client):
        # given
        self._create_offerers()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for(
                "backoffice_blueprint.search_pro", q=f"{self.offerers[0].siren} {self.offerers[1].name}", type="offerer"
            ),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 0

    @pytest.mark.parametrize("query", ["987654321", "festival@example.com", "Festival de la Montagne", ""])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_offerer_no_result(self, client, query):
        # given
        self._create_offerers()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=query, type="offerer"),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 0


class ProSearchVenueTest:
    def _create_venues(
        self,
        number: int = 12,
        name_part1: list[str] = ("Librairie", "Cinéma", "Théâtre"),
        name_part2_admin: list[str] = ("Alpha", "Beta", "Gamma", "Delta"),
        name_part2_public: list[str] = ("de la Gare", "de la Plage", "du Centre", "du Centaure"),
        domains: list[str] = ("librairie.fr", "cinema.com", "theatre.net"),
    ) -> None:
        self.venues = []
        for i in range(number):
            venue = offerers_factories.VenueFactory(
                name=f"{name_part1[i % len(name_part1)]} {name_part2_admin[i % len(name_part2_admin)]}",
                publicName=f"{name_part1[i % len(name_part1)]} {name_part2_public[i % len(name_part2_public)]}",
                siret=f"123456{i:03}{i:05}",
                isPermanent=bool(i % 2 == 0),
                contact=None,
            )
            if i % 2:
                offerers_factories.VenueContactFactory(
                    venue=venue,
                    email=f"contact{venue.id}@{domains[i % len(domains)]}",
                    phone_number=f"+331020304{i:02}",
                )
            self.venues.append(venue)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_venue_by_id(self, client):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=self.venues[2].id, type="venue"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_venue_equals(response_list[0], self.venues[2])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_venue_by_siret(self, client):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=self.venues[3].siret, type="venue"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_venue_equals(response_list[0], self.venues[3])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_venue_by_booking_email(self, client):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=self.venues[1].bookingEmail, type="venue"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_venue_equals(response_list[0], self.venues[1])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_venue_by_booking_email_domain(self, client):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="@librairie.fr", type="venue"),
        )

        # then
        assert response.status_code == 200
        response_list = sorted(response.json["data"], key=lambda v: v["id"])
        assert len(response_list) == 2  # 4 * Librairie but only odd indexes in venues have contact email
        assert_venue_equals(response_list[0], self.venues[3])  # Librairie du Centaure
        assert_venue_equals(response_list[1], self.venues[9])  # Librairie de la Plage

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_venue_by_contact_email(self, client):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=self.venues[1].contact.email, type="venue"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1
        assert_venue_equals(response_list[0], self.venues[1])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_venue_by_name(self, client):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="Alpha", type="venue"),
        )

        # then
        assert response.status_code == 200
        response_list = sorted(response.json["data"], key=lambda v: v["id"])
        assert len(response_list) == 3
        assert_venue_equals(response_list[0], self.venues[0])  # Librairie Alpha
        assert_venue_equals(response_list[1], self.venues[4])  # Cinéma Alpha
        assert_venue_equals(response_list[2], self.venues[8])  # Théâtre Alpha

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_venue_by_public_name(self, client):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="Théâtre du Centre", type="venue"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) >= 2  # Results may contain all "Théâtre", "Centre", "Centaure"
        assert len(response_list) <= 8  # Results should not contain Libraire/Cinéma + Gare/Plage
        assert_venue_equals(response_list[0], self.venues[2])  # Théâtre du Centre (most relevant)
        assert_venue_equals(response_list[1], self.venues[11])  # Théâtre du Centaure (very close to the first one)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_by_two_consistent_criteria(self, client):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=f"{self.venues[2].siret} {self.venues[2].name}", type="venue"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 1  # Single result because only one is matching SIREN even if name is close
        assert_venue_equals(response_list[0], self.venues[2])

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_pro_by_two_unconsistent_criteria(self, client):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=f"{self.venues[0].siret} {self.venues[1].name}", type="venue"),
        )

        # then
        assert response.status_code == 200
        response_list = response.json["data"]
        assert len(response_list) == 0

    @pytest.mark.parametrize("query", ["987654321", "festival@example.com", "Festival de la Montagne", ""])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_venue_no_result(self, client, query):
        # given
        self._create_venues()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q=query, type="venue"),
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == 0


class ProSearchReturns403Test:
    @pytest.mark.parametrize("res_type", ["proUser", "offerer", "venue"])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_without_permission(self, client, res_type):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="anything", type=res_type),
        )

        # then
        assert response.status_code == 403

    @pytest.mark.parametrize("res_type", ["proUser", "offerer", "venue"])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_as_anonymous(self, client, res_type):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PRO_ACCOUNT])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.search_pro", q="anything", type=res_type),
        )

        # then
        assert response.status_code == 403
