from unittest.mock import patch

import pytest

from pcapi.connectors import sirene
import pcapi.core.offerers.models as offerers_models
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")

REQUEST_BODY = {
    "createVenueWithoutSiret": False,
    "publicName": "Pass Culture",
    "siret": "85331845900031",
    "target": "INDIVIDUAL",
    "venueTypeCode": "MOVIE",
    "webPresence": "www.example.com, instagram.com/example, @example@mastodon.example",
}


class Returns200Test:
    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_nominal(self, client):
        user = users_factories.UserFactory(email="pro@example.com")

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 201
        created_offerer = offerers_models.Offerer.query.one()
        assert created_offerer.address == "3 RUE DE VALOIS"
        assert created_offerer.city == "Paris"
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert not created_offerer.isValidated
        assert created_offerer.postalCode == "75001"
        created_venue = offerers_models.Venue.query.filter(offerers_models.Venue.isVirtual.is_(False)).one()
        assert created_venue.address == "3 RUE DE VALOIS"
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


class Returns400Test:
    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    @patch("pcapi.connectors.sirene.get_siret", side_effect=sirene.UnknownEntityException())
    def test_siret_unknown(self, _get_siret_mock, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 400
        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.UserOfferer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    @patch("pcapi.connectors.sirene.get_siret", side_effect=sirene.NonPublicDataException())
    def test_non_diffusible_siret(self, _get_siret_mock, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 400
        assert response.json == {"global": ["Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles."]}
        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.UserOfferer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0


class Returns403Test:
    @override_features(WIP_ENABLE_NEW_ONBOARDING=False)
    def test_siret_unknown(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 403


class Returns500Test:
    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    @patch("pcapi.connectors.sirene.get_siret", side_effect=sirene.SireneApiException())
    def test_sirene_api_ko(self, _get_siret_mock, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 500
        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.UserOfferer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0
