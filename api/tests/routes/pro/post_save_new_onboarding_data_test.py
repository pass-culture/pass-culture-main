from unittest.mock import patch

import pytest

import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.connectors.api_adresse import AddressInfo
from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.core.geography import models as geography_models
from pcapi.core.history import models as history_models
from pcapi.models import db

from tests.connectors import sirene_test_data


pytestmark = pytest.mark.usefixtures("db_session")

REQUEST_BODY = {
    "address": {
        "city": "Paris",
        "banId": "75101_9575_00003",
        "latitude": 2.30829,
        "longitude": 48.87171,
        "postalCode": "75001",
        "inseeCode": "75101",
        "street": "3 Rue de Valois",
    },
    "siret": "85331845900031",
    "publicName": "Pass Culture",
    "createVenueWithoutSiret": False,
    "target": "INDIVIDUAL",
    "venueTypeCode": "MOVIE",
    "isOpenToPublic": False,
    "webPresence": "https://www.example.com, https://instagram.com/example, https://mastodon.social/@example",
    "token": "token",
}


class Returns200Test:
    @patch("pcapi.connectors.api_adresse.TestingBackend.get_single_address_result")
    def test_nominal(self, mocked_get_address, client):
        user = users_factories.UserFactory(email="pro@example.com")

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 201
        created_offerer = db.session.query(offerers_models.Offerer).one()
        assert created_offerer.street == "3 Rue de Valois"
        assert created_offerer.city == "Paris"
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert not created_offerer.isValidated
        assert created_offerer.postalCode == "75001"
        created_venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.isVirtual.is_(False)).one()
        assert created_venue.street == "3 Rue de Valois"
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

        mocked_get_address.assert_not_called()
        address = db.session.query(geography_models.Address).one()
        assert created_venue.offererAddress.addressId == address.id
        assert address.street == "3 Rue de Valois"
        assert address.city == REQUEST_BODY["address"]["city"]
        assert address.isManualEdition is False

        assert created_venue.offererAddress.offererId == created_venue.managingOffererId

    @patch(
        "pcapi.connectors.api_adresse.TestingBackend.get_municipality_centroid",
        return_value=AddressInfo(
            id="75101",
            label="Paris",
            postcode="75001",
            citycode="75056",
            score=0.9651727272727272,
            latitude=48.87171,
            longitude=2.308289,
            city="Paris",
            street="unused",
        ),
    )
    def test_nominal_case_with_manually_edited_address(self, mocked_get_centroid, client):
        user = users_factories.UserFactory(email="pro@example.com")

        client = client.with_session_auth(user.email)
        data = {**REQUEST_BODY}
        data["address"]["isManualEdition"] = True
        data["address"].pop("inseeCode")
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 201
        created_offerer = db.session.query(offerers_models.Offerer).one()
        assert created_offerer.street == "3 Rue de Valois"
        assert created_offerer.city == "Paris"
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert not created_offerer.isValidated
        assert created_offerer.postalCode == "75001"
        created_venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.isVirtual.is_(False)).one()
        assert created_venue.street == "3 Rue de Valois"
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

        address = db.session.query(geography_models.Address).one()
        assert created_venue.offererAddress.addressId == address.id
        assert address.street == REQUEST_BODY["address"]["street"]
        assert address.city == REQUEST_BODY["address"]["city"]
        assert address.isManualEdition is True
        assert address.inseeCode == "75056"
        assert address.banId is None
        mocked_get_centroid.assert_called_once()

    def test_returns_public_information_only(self, client):
        user = users_factories.UserFactory(email="pro@example.com")

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        created_offerer = db.session.query(offerers_models.Offerer).one()
        assert response.json == {
            "id": created_offerer.id,
            "siren": "853318459",
            "name": "MINISTERE DE LA CULTURE",
        }

    @pytest.mark.settings(IS_INTEGRATION=True)
    def test_validated_in_integration(self, client):
        user = users_factories.UserFactory(email="pro@example.com")

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 201
        created_offerer = db.session.query(offerers_models.Offerer).one()
        assert created_offerer.isValidated

        created_venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.isVirtual.is_(False)).one()
        assert created_venue.adageId is not None
        assert created_venue.adageInscriptionDate is not None

    @pytest.mark.features(WIP_2025_SIGN_UP=True)
    def test_user_can_create_offerer_with_phone_number(self, client):
        pro = users_factories.ProFactory(phoneNumber=None)

        body = {**REQUEST_BODY, **{"phoneNumber": "0123456789"}}
        assert not pro.phoneNumber

        client = client.with_session_auth(pro.email)
        response = client.post("/offerers/new", json=body)

        created_offerer = db.session.query(offerers_models.Offerer).one()
        assert response.json["id"] == created_offerer.id

        pro = db.session.query(users_models.User).filter_by(id=pro.id).one()
        assert pro.phoneNumber == "+33123456789"

    @pytest.mark.features(WIP_2025_SIGN_UP=True)
    def test_user_can_create_offerer_without_phone_number(self, client):
        pro = users_factories.ProFactory(phoneNumber=None)

        body = {**REQUEST_BODY, **{"phoneNumber": None}}

        assert not pro.phoneNumber

        client = client.with_session_auth(pro.email)
        response = client.post("/offerers/new", json=body)

        created_offerer = db.session.query(offerers_models.Offerer).one()
        assert response.json["id"] == created_offerer.id

        pro = db.session.query(users_models.User).filter_by(id=pro.id).one()
        assert not pro.phoneNumber


class Returns400Test:
    @patch("pcapi.connectors.entreprise.sirene.get_siret", side_effect=sirene_exceptions.UnknownEntityException())
    def test_siret_unknown(self, _get_siret_mock, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 400
        assert db.session.query(offerers_models.Offerer).count() == 0
        assert db.session.query(offerers_models.UserOfferer).count() == 0
        assert db.session.query(offerers_models.Venue).count() == 0

    @patch("pcapi.connectors.entreprise.sirene.get_siret", side_effect=sirene_exceptions.NonPublicDataException())
    def test_non_diffusible_siret(self, _get_siret_mock, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 400
        assert response.json == {"global": ["Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles."]}
        assert db.session.query(offerers_models.Offerer).count() == 0
        assert db.session.query(offerers_models.UserOfferer).count() == 0
        assert db.session.query(offerers_models.Venue).count() == 0

    @pytest.mark.settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
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
        assert db.session.query(offerers_models.Offerer).count() == 0
        assert db.session.query(offerers_models.UserOfferer).count() == 0
        assert db.session.query(offerers_models.Venue).count() == 0


class Returns500Test:
    @patch("pcapi.connectors.entreprise.sirene.get_siret", side_effect=sirene_exceptions.ApiException())
    def test_sirene_api_ko(self, _get_siret_mock, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post("/offerers/new", json=REQUEST_BODY)

        assert response.status_code == 500
        assert db.session.query(offerers_models.Offerer).count() == 0
        assert db.session.query(offerers_models.UserOfferer).count() == 0
        assert db.session.query(offerers_models.Venue).count() == 0
