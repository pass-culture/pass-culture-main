from unittest.mock import patch

import pytest

from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.core.history import models as history_models
import pcapi.core.offerers.models as offerers_models
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories

from tests.connectors import sirene_test_data


pytestmark = pytest.mark.usefixtures("db_session")

REQUEST_BODY = {
    "city": "Paris",
    "banId": "75101_9575_00003",
    "createVenueWithoutSiret": False,
    "latitude": 2.30829,
    "longitude": 48.87171,
    "postalCode": "75001",
    "publicName": "Pass Culture",
    "siret": "85331845900031",
    "street": "3 RUE DE VALOIS",
    "target": "INDIVIDUAL",
    "venueTypeCode": "MOVIE",
    "webPresence": "https://www.example.com, https://instagram.com/example, https://mastodon.social/@example",
    "token": "token",
}


class Returns200Test:
    def test_nominal(self, client):
        user = users_factories.UserFactory(email="pro@example.com")

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 201
        created_offerer = offerers_models.Offerer.query.one()
        assert created_offerer.street == "3 RUE DE VALOIS"
        assert created_offerer.city == "Paris"
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert not created_offerer.isValidated
        assert created_offerer.postalCode == "75001"
        created_venue = offerers_models.Venue.query.filter(offerers_models.Venue.isVirtual.is_(False)).one()
        assert created_venue.street == "3 RUE DE VALOIS"
        assert created_venue.bookingEmail == "pro@example.com"
        assert created_venue.city == "Paris"
        assert created_venue.audioDisabilityCompliant is None
        assert created_venue.mentalDisabilityCompliant is None
        assert created_venue.motorDisabilityCompliant is None
        assert created_venue.visualDisabilityCompliant is None
        assert created_venue.comment is None
        assert created_venue.departementCode == "75"
        assert created_venue.name == "MINISTERE DE LA CULTURE"
        assert created_venue.postalCode == "75001"
        assert created_venue.publicName == "Pass Culture"
        assert created_venue.siret == "85331845900031"
        assert created_venue.venueTypeCode == offerers_models.VenueTypeCode.MOVIE
        assert created_venue.withdrawalDetails is None
        assert created_venue.adageId is None
        assert created_venue.adageInscriptionDate is None

        assert len(created_venue.adage_addresses) == 1
        adage_addr = created_venue.adage_addresses[0]

        assert adage_addr.venueId == created_venue.id
        assert adage_addr.adageId == created_venue.adageId
        assert adage_addr.adageInscriptionDate == created_venue.adageInscriptionDate

        assert len(created_offerer.action_history) == 1
        assert created_offerer.action_history[0].actionType == history_models.ActionType.OFFERER_NEW
        assert created_offerer.action_history[0].authorUser == user
        assert len(created_venue.action_history) == 1
        assert created_venue.action_history[0].actionType == history_models.ActionType.VENUE_CREATED
        assert created_venue.action_history[0].authorUser == user

    def test_returns_public_information_only(self, client):
        user = users_factories.UserFactory(email="pro@example.com")

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        created_offerer = offerers_models.Offerer.query.one()
        assert response.json == {
            "id": created_offerer.id,
            "siren": "853318459",
            "name": "MINISTERE DE LA CULTURE",
        }

    @override_settings(IS_INTEGRATION=True)
    def test_validated_in_integration(self, client):
        user = users_factories.UserFactory(email="pro@example.com")

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 201
        created_offerer = offerers_models.Offerer.query.one()
        assert created_offerer.isValidated

        created_venue = offerers_models.Venue.query.filter(offerers_models.Venue.isVirtual.is_(False)).one()
        assert created_venue.adageId is not None
        assert created_venue.adageInscriptionDate is not None


class Returns400Test:
    @patch("pcapi.connectors.entreprise.sirene.get_siret", side_effect=sirene_exceptions.UnknownEntityException())
    def test_siret_unknown(self, _get_siret_mock, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 400
        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.UserOfferer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0

    @patch("pcapi.connectors.entreprise.sirene.get_siret", side_effect=sirene_exceptions.NonPublicDataException())
    def test_non_diffusible_siret(self, _get_siret_mock, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 400
        assert response.json == {"global": ["Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles."]}
        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.UserOfferer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0

    @override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
    def test_inactive_siret(self, requests_mock, client):
        siret = REQUEST_BODY["siret"]

        requests_mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_INACTIVE_COMPANY,
        )

        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 400
        assert response.json == {"siret": "SIRET is no longer active"}
        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.UserOfferer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0


class Returns500Test:
    @patch("pcapi.connectors.entreprise.sirene.get_siret", side_effect=sirene_exceptions.ApiException())
    def test_sirene_api_ko(self, _get_siret_mock, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 500
        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.UserOfferer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0
