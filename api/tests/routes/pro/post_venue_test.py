import pathlib

import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Venue
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.factories import ProFactory
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

import tests


pytestmark = pytest.mark.usefixtures("db_session")
IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


def create_valid_venue_data(user=None):
    user_offerer_data = {"offerer__siren": "302559178"}
    if user:
        user_offerer_data["user"] = user
    user_offerer = offerers_factories.UserOffererFactory(**user_offerer_data)
    venue_label = offerers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")

    return {
        "name": "Ma venue",
        "siret": f"{user_offerer.offerer.siren}10045",
        "address": "75 Rue Charles Fourier, 75013 Paris",
        "postalCode": "75200",
        "bookingEmail": "toto@example.com",
        "city": "Paris",
        "managingOffererId": humanize(user_offerer.offerer.id),
        "latitude": 48.82387,
        "longitude": 2.35284,
        "publicName": "Ma venue publique",
        "venueTypeCode": "BOOKSTORE",
        "venueLabelId": humanize(venue_label.id),
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
    def test_register_new_venue_with_a_business_unit(self, client):
        # given
        user = ProFactory()
        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)
        offerer = offerers_models.Offerer.query.all()[0]
        existing_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_data["businessUnitId"] = existing_venue.businessUnit.id

        # when
        response = client.post("/venues", json=venue_data)

        # then
        assert response.status_code == 201
        idx = response.json["id"]

        venue = Venue.query.filter_by(id=dehumanize(idx)).one()
        assert venue.businessUnitId == venue_data["businessUnitId"]

        assert len(sendinblue_testing.sendinblue_requests) == 1

    @testing.override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_register_new_venue(self, client):
        user = ProFactory()
        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)

        response = client.post("/venues", json=venue_data)

        assert response.status_code == 201
        idx = response.json["id"]

        venue = Venue.query.filter_by(id=dehumanize(idx)).one()

        assert venue.name == venue_data["name"]
        assert venue.publicName == venue_data["publicName"]
        assert venue.siret == venue_data["siret"]
        assert venue.venueTypeCode.name == "BOOKSTORE"
        assert venue.venueLabelId == dehumanize(venue_data["venueLabelId"])
        assert venue.description == venue_data["description"]
        assert venue.audioDisabilityCompliant == venue_data["audioDisabilityCompliant"]
        assert venue.mentalDisabilityCompliant == venue_data["mentalDisabilityCompliant"]
        assert venue.motorDisabilityCompliant == venue_data["motorDisabilityCompliant"]
        assert venue.visualDisabilityCompliant == venue_data["visualDisabilityCompliant"]
        assert venue.contact.email == venue_data["contact"]["email"]
        assert venue.dmsToken

        assert venue.isValidated
        assert not venue.isPermanent
        assert not venue.contact.phone_number
        assert not venue.contact.social_medias

        assert len(sendinblue_testing.sendinblue_requests) == 1


class Returns400Test:
    @testing.override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=False)
    def test_business_unit_not_exist(self, client):
        # given
        user = ProFactory()
        client = client.with_session_auth(email=user.email)
        venue_data = create_valid_venue_data(user)
        venue_data["businessUnitId"] = "777"

        # when
        response = client.post("/venues", json=venue_data)

        # then
        assert response.status_code == 400
        assert response.json["businessUnitId"] == ["Ce point de facturation n'existe pas."]

        assert len(sendinblue_testing.sendinblue_requests) == 0

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


class Returns403Test:
    def test_user_is_not_managing_offerer_create_venue(self, client):
        user = ProFactory()
        venue_data = create_valid_venue_data()

        client = client.with_session_auth(email=user.email)
        response = client.post("/venues", json=venue_data)

        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
