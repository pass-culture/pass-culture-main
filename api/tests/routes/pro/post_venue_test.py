import pathlib

import pytest

from pcapi.core import testing
from pcapi.core.external.zendesk_sell_backends import testing as zendesk_testing
from pcapi.core.geography import models as geography_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Venue
from pcapi.core.testing import override_settings
from pcapi.core.users import testing as external_testing
from pcapi.core.users.factories import ProFactory

import tests
from tests.connectors import sirene_test_data


pytestmark = pytest.mark.usefixtures("db_session")
IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


def get_api_address_response():
    return {
        "type": "FeatureCollection",
        "version": "draft",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [3.893166, 44.626322]},
                "properties": {
                    "label": "Chemin de Chaniaux 48250 Laveyrune",
                    "score": 0.928571818181818,
                    "type": "locality",
                    "importance": 0.21429,
                    "id": "07136_0040",
                    "name": "Chemin de Chaniaux",
                    "postcode": "48250",
                    "citycode": "07136",
                    "x": 770848.89,
                    "y": 6392314.73,
                    "city": "Laveyrune",
                    "context": "07, Ardèche, Auvergne-Rhône-Alpes",
                    "locality": "Chemin de Chaniaux",
                },
            }
        ],
        "attribution": "BAN",
        "licence": "ETALAB-2.0",
        "query": "Chemin de chaniaux Laveyrune",
        "filters": {"postcode": "48250"},
        "limit": 1,
    }


def create_valid_venue_data(user=None):
    user_offerer_data = {"offerer__siren": "302559178"}
    if user:
        user_offerer_data["user"] = user
    user_offerer = offerers_factories.UserOffererFactory(**user_offerer_data)
    venue_label = offerers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")

    return {
        "name": "MINISTERE DE LA CULTURE",
        "siret": f"{user_offerer.offerer.siren}10045",
        "street": "Chemin de Chaniaux 48250 Laveyrune",
        "postalCode": "48250",
        "bookingEmail": "toto@example.com",
        "city": "Laveyrune",
        "managingOffererId": user_offerer.offerer.id,
        "latitude": 44.626322,
        "longitude": 3.893166,
        "publicName": "Ma venue publique",
        "venueTypeCode": "BOOKSTORE",
        "venueLabelId": venue_label.id,
        "description": "Some description",
        "audioDisabilityCompliant": True,
        "mentalDisabilityCompliant": False,
        "motorDisabilityCompliant": False,
        "visualDisabilityCompliant": False,
        "contact": {"email": "some@email.com"},
    }


venue_malformed_test_data = [
    ({"description": "a" * 1024}, "description"),
    ({"contact": {"email": "not_an_email"}}, "contact.email"),
    ({"contact": {"website": "not_an_url"}}, "contact.website"),
    ({"contact": {"phoneNumber": "not_a_phone_number"}}, "contact.phoneNumber"),
    ({"contact": {"social_medias": {"a": "b"}}}, "contact.socialMedias.__key__"),
    ({"contact": {"social_medias": {"facebook": "not_an_url"}}}, "contact.socialMedias.facebook"),
]


class Returns201Test:
    @testing.override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    @testing.override_features(
        ENABLE_ZENDESK_SELL_CREATION=True, ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=True
    )
    def test_register_new_venue(self, client, requests_mock):
        api_adresse_response = get_api_address_response()
        user = ProFactory()
        venue_data = create_valid_venue_data(user)
        requests_mock.get(
            """https://api-adresse.data.gouv.fr/search?q=Chemin+de+Chaniaux+48250+Laveyrune&postcode=48250&autocomplete=0&limit=1""",
            json=api_adresse_response,
        )

        client = client.with_session_auth(email=user.email)
        response = client.post("/venues", json=venue_data)

        assert response.status_code == 201

        venue = Venue.query.filter_by(id=response.json["id"]).one()
        address = geography_models.Address.query.one()
        offerer_address = models.OffererAddress.query.one()

        assert venue.name == venue_data["name"]
        assert venue.publicName == venue_data["publicName"]
        assert venue.siret == venue_data["siret"]
        assert venue.venueTypeCode.name == "BOOKSTORE"
        assert venue.venueLabelId == venue_data["venueLabelId"]
        assert venue.description == venue_data["description"]
        assert venue.audioDisabilityCompliant == venue_data["audioDisabilityCompliant"]
        assert venue.mentalDisabilityCompliant == venue_data["mentalDisabilityCompliant"]
        assert venue.motorDisabilityCompliant == venue_data["motorDisabilityCompliant"]
        assert venue.visualDisabilityCompliant == venue_data["visualDisabilityCompliant"]
        assert venue.contact.email == venue_data["contact"]["email"]
        assert venue.dmsToken

        assert not venue.isPermanent
        assert not venue.contact.phone_number
        assert not venue.contact.social_medias

        assert len(venue.adage_addresses) == 1
        adage_addr = venue.adage_addresses[0]

        assert adage_addr.venueId == venue.id
        assert adage_addr.adageId == venue.adageId
        assert adage_addr.adageInscriptionDate == venue.adageInscriptionDate

        assert len(external_testing.sendinblue_requests) == 1
        assert external_testing.zendesk_sell_requests == [
            {
                "action": "create",
                "type": "Venue",
                "id": response.json["id"],
                "parent_organization_id": zendesk_testing.TESTING_ZENDESK_ID_OFFERER,
            }
        ]

        assert venue.offererAddressId == offerer_address.id
        assert offerer_address.addressId == address.id
        assert venue.timezone == address.timezone
        assert venue.city == address.city
        assert venue.postalCode == address.postalCode
        assert address.street == api_adresse_response["features"][0]["properties"]["locality"]
        assert address.inseeCode == api_adresse_response["features"][0]["properties"]["citycode"]
        assert address.inseeCode.startswith(address.departmentCode)
        assert address.departmentCode == "07"
        assert address.timezone == "Europe/Paris"

        assert len(venue.action_history) == 1
        assert venue.action_history[0].actionType == history_models.ActionType.VENUE_CREATED
        assert venue.action_history[0].authorUser == user

    @testing.override_settings(
        ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend",
        IS_INTEGRATION=True,
    )
    @testing.override_features(
        ENABLE_ZENDESK_SELL_CREATION=True, ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=True
    )
    def test_register_new_venue_from_integration_env(self, client, requests_mock):
        api_adresse_response = get_api_address_response()
        user = ProFactory()

        requests_mock.get(
            """https://api-adresse.data.gouv.fr/search?q=Chemin+de+Chaniaux+48250+Laveyrune&postcode=48250&autocomplete=0&limit=1""",
            json=api_adresse_response,
        )

        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)

        response = client.post("/venues", json=venue_data)

        assert response.status_code == 201

        venue = Venue.query.filter_by(id=response.json["id"]).one()

        assert venue.name == venue_data["name"]
        assert venue.adageId
        assert venue.adageInscriptionDate
        assert venue.managingOfferer.allowedOnAdage

    @testing.override_features(ENABLE_ZENDESK_SELL_CREATION=True)
    def test_register_new_venue_without_double_model_writing(self, client, requests_mock):
        user = ProFactory()
        venue_data = create_valid_venue_data(user)

        client = client.with_session_auth(email=user.email)
        response = client.post("/venues", json=venue_data)

        assert response.status_code == 201

        venue = Venue.query.filter_by(id=response.json["id"]).one()
        assert not geography_models.Address.query.one_or_none()
        assert not models.OffererAddress.query.one_or_none()

        assert venue.name == venue_data["name"]
        assert venue.publicName == venue_data["publicName"]
        assert venue.siret == venue_data["siret"]
        assert venue.venueTypeCode.name == "BOOKSTORE"
        assert venue.venueLabelId == venue_data["venueLabelId"]
        assert venue.description == venue_data["description"]
        assert venue.audioDisabilityCompliant == venue_data["audioDisabilityCompliant"]
        assert venue.mentalDisabilityCompliant == venue_data["mentalDisabilityCompliant"]
        assert venue.motorDisabilityCompliant == venue_data["motorDisabilityCompliant"]
        assert venue.visualDisabilityCompliant == venue_data["visualDisabilityCompliant"]
        assert venue.contact.email == venue_data["contact"]["email"]
        assert venue.dmsToken

        assert not venue.isPermanent
        assert not venue.contact.phone_number
        assert not venue.contact.social_medias

        assert len(venue.adage_addresses) == 1
        adage_addr = venue.adage_addresses[0]

        assert adage_addr.venueId == venue.id
        assert adage_addr.adageId == venue.adageId
        assert adage_addr.adageInscriptionDate == venue.adageInscriptionDate

        assert len(external_testing.sendinblue_requests) == 1
        assert external_testing.zendesk_sell_requests == [
            {
                "action": "create",
                "type": "Venue",
                "id": response.json["id"],
                "parent_organization_id": zendesk_testing.TESTING_ZENDESK_ID_OFFERER,
            }
        ]

        assert not venue.offererAddressId

    def test_use_venue_name_retrieved_from_sirene_api(self, client):
        user = ProFactory()
        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)
        venue_data = {**venue_data, "name": "edited venue name"}

        response = client.post("/venues", json=venue_data)

        assert response.status_code == 201
        venue = Venue.query.filter_by(id=response.json["id"]).one()
        assert venue.name == "MINISTERE DE LA CULTURE"


class Returns400Test:
    def test_latitude_out_of_range_and_longitude_wrong_format(self, client):
        user = ProFactory()
        venue_data = create_valid_venue_data(user)

        venue_data = {
            **venue_data,
            "latitude": -98.82387,
            "longitude": "112°3534",
        }

        client = client.with_session_auth(email=user.email)
        response = client.post("/venues", json=venue_data)

        assert response.status_code == 400
        assert response.json["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]
        assert response.json["longitude"] == ["Format incorrect"]

    def test_longitude_out_of_range_and_latitude_wrong_format(self, client):
        user = ProFactory()

        venue_data = create_valid_venue_data(user)
        venue_data = {
            **venue_data,
            "latitude": "76°8237",
            "longitude": 210.43251,
        }

        client = client.with_session_auth(email=user.email)
        response = client.post("/venues", json=venue_data)

        assert response.status_code == 400
        assert response.json["longitude"] == ["La longitude doit être comprise entre -180.0 et +180.0"]
        assert response.json["latitude"] == ["Format incorrect"]

    def test_mandatory_accessibility_fields(self, client):
        user = ProFactory()

        venue_data = create_valid_venue_data(user)
        venue_data.pop("audioDisabilityCompliant")
        venue_data.pop("mentalDisabilityCompliant")
        venue_data.pop("motorDisabilityCompliant")
        venue_data.pop("visualDisabilityCompliant")

        client = client.with_session_auth(email=user.email)
        response = client.post("/venues", json=venue_data)

        assert response.status_code == 400
        assert response.json["global"] == ["L'accessibilité du lieu doit être définie."]

    @pytest.mark.parametrize("data, key", venue_malformed_test_data)
    def test_create_venue_malformed(self, client, data, key):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.post("/venues", json=data)

        assert response.status_code == 400
        assert key in response.json

    def test_no_siret_nor_comment(self, client):
        user = ProFactory()
        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)
        venue_data.pop("siret")

        response = client.post("/venues", json=venue_data)

        assert response.status_code == 400
        assert response.json["siret"] == ["Veuillez saisir soit un SIRET soit un commentaire"]

    def test_both_siret_and_comment(self, client):
        user = ProFactory()
        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)
        venue_data["comment"] = "J'ai déjà saisi un SIRET"

        response = client.post("/venues", json=venue_data)

        assert response.status_code == 400
        assert response.json["siret"] == ["Veuillez saisir soit un SIRET soit un commentaire"]

    def test_comment_too_long(self, client) -> None:
        user = ProFactory()
        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)
        venue_data["siret"] = None
        venue_data["comment"] = "Pas de SIRET " * 40

        response = client.post("/venues", json=venue_data)

        assert response.status_code == 400
        assert response.json["comment"] == ["ensure this value has at most 500 characters"]

    def test_withdrawal_details_too_long(self, client) -> None:
        user = ProFactory()
        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)
        venue_data["withdrawalDetails"] = "Trop long " * 51

        response = client.post("/venues", json=venue_data)

        assert response.status_code == 400
        assert response.json["withdrawalDetails"] == ["ensure this value has at most 500 characters"]

    @override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
    def test_with_inactive_siret(self, requests_mock, client):
        siret = "30255917810045"
        requests_mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_INACTIVE_COMPANY,
        )

        user = ProFactory()
        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)

        response = client.post("/venues", json=venue_data)

        assert response.status_code == 400
        assert response.json["siret"] == ["SIRET is no longer active"]


class Returns403Test:
    def test_user_is_not_managing_offerer_create_venue(self, client):
        user = ProFactory()
        venue_data = create_valid_venue_data()

        client = client.with_session_auth(email=user.email)
        response = client.post("/venues", json=venue_data)

        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]
