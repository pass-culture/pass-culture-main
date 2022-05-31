import io
import pathlib
from unittest.mock import patch

from freezegun import freeze_time
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Venue
from pcapi.core.testing import override_settings
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.factories import ProFactory
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

import tests
from tests.conftest import TestClient


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


@pytest.mark.usefixtures("db_session")
def test_should_register_new_venue(client):
    # given
    user = ProFactory()
    auth_request = client.with_session_auth(email=user.email)
    venue_data = create_valid_venue_data(user)

    # when
    response = auth_request.post("/venues", json=venue_data)

    # then
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

    assert venue.isValidated
    assert not venue.isPermanent
    assert not venue.contact.phone_number
    assert not venue.contact.social_medias

    assert len(sendinblue_testing.sendinblue_requests) == 1


@pytest.mark.usefixtures("db_session")
def test_should_register_new_venue_with_a_business_unit(app):
    # given
    user = ProFactory()
    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
    venue_data = create_valid_venue_data(user)
    offerer = offerers_models.Offerer.query.all()[0]
    existing_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue_data["businessUnitId"] = existing_venue.businessUnit.id

    # when
    response = auth_request.post("/venues", json=venue_data)

    # then
    assert response.status_code == 201
    idx = response.json["id"]

    venue = Venue.query.filter_by(id=dehumanize(idx)).one()
    assert venue.businessUnitId == venue_data["businessUnitId"]

    assert len(sendinblue_testing.sendinblue_requests) == 1


@pytest.mark.usefixtures("db_session")
def test_should_return_401_when_business_unit_not_exist(app):
    # given
    user = ProFactory()
    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
    venue_data = create_valid_venue_data(user)
    venue_data["businessUnitId"] = "777"

    # when
    response = auth_request.post("/venues", json=venue_data)

    # then
    assert response.status_code == 400
    assert response.json["businessUnitId"] == ["Ce point de facturation n'existe pas."]

    assert len(sendinblue_testing.sendinblue_requests) == 0


@pytest.mark.usefixtures("db_session")
def test_should_return_401_when_latitude_out_of_range_and_longitude_wrong_format(app):
    # given
    user = ProFactory()
    venue_data = create_valid_venue_data(user)

    venue_data = {
        **venue_data,
        "latitude": -98.82387,
        "longitude": "112°3534",
    }

    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

    # when
    response = auth_request.post("/venues", json=venue_data)

    # then
    assert response.status_code == 400
    assert response.json["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]
    assert response.json["longitude"] == ["Format incorrect"]


@pytest.mark.usefixtures("db_session")
def test_should_return_401_when_longitude_out_of_range_and_latitude_wrong_format(app):
    # given
    user = ProFactory()

    venue_data = create_valid_venue_data(user)
    venue_data = {
        **venue_data,
        "latitude": "76°8237",
        "longitude": 210.43251,
    }

    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

    # when
    response = auth_request.post("/venues", json=venue_data)

    # then
    assert response.status_code == 400
    assert response.json["longitude"] == ["La longitude doit être comprise entre -180.0 et +180.0"]
    assert response.json["latitude"] == ["Format incorrect"]


@pytest.mark.usefixtures("db_session")
def test_mandatory_accessibility_fields(app):
    # given
    user = ProFactory()

    venue_data = create_valid_venue_data(user)
    venue_data.pop("audioDisabilityCompliant")
    venue_data.pop("mentalDisabilityCompliant")
    venue_data.pop("motorDisabilityCompliant")
    venue_data.pop("visualDisabilityCompliant")

    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

    # when
    response = auth_request.post("/venues", json=venue_data)

    # then
    assert response.status_code == 400
    assert response.json["global"] == ["L'accessibilité du lieu doit être définie."]


@pytest.mark.usefixtures("db_session")
def test_should_return_403_when_user_is_not_managing_offerer_create_venue(app):
    user = ProFactory()
    venue_data = create_valid_venue_data()
    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

    response = auth_request.post("/venues", json=venue_data)

    assert response.status_code == 403
    assert response.json["global"] == ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]


venue_malformed_test_data = [
    ({"description": "a" * 1024}, "description"),
    ({"contact": {"email": "not_an_email"}}, "contact.email"),
    ({"contact": {"website": "not_an_url"}}, "contact.website"),
    ({"contact": {"phoneNumber": "not_a_phone_number"}}, "contact.phoneNumber"),
    ({"contact": {"social_medias": {"a": "b"}}}, "contact.socialMedias.__key__"),
    ({"contact": {"social_medias": {"facebook": "not_an_url"}}}, "contact.socialMedias.facebook"),
]


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize("data, key", venue_malformed_test_data)
def test_create_venue_malformed(app, client, data, key):
    user_offerer = offerers_factories.UserOffererFactory()

    client = client.with_session_auth(user_offerer.user.email)
    response = client.post("/venues", json=data)

    assert response.status_code == 400
    assert key in response.json


@pytest.mark.usefixtures("db_session")
@freeze_time("2020-10-15 00:00:00")
class VenueBannerTest:
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_upload_image(self, mock_search_async_index_venue_ids, client, tmpdir):
        """
        Check that the image upload works for a legit file (size and type):
            * API returns a 201 status code
            * the file has been saved to disk (and resized/cropped before that)
            * venue's banner information have been updated
            * venue's banner information are sent back to the client
        """
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        image_content = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        file = {"banner": (io.BytesIO(image_content), "upsert_banner.jpg")}

        client = client.with_session_auth(email=user_offerer.user.email)
        url = f"/venues/{humanize(venue.id)}/banner"
        url += "?x_crop_percent=0.0&y_crop_percent=0.0&height_crop_percent=0.6&width_crop_percent=0.9&image_credit=none"

        # Override storage url otherwise it would be, well, an URL
        # (like http://localhost) and make some checks more difficult.
        # Override local storage and use a temporary directory instead.
        with override_settings(OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)):
            response = client.post(url, files=file)
            assert response.status_code == 201

            url_prefix = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

            banner_url_timestamp = 1602720000
            assert response.json["bannerUrl"] == str(url_prefix / f"{humanize(venue.id)}_{banner_url_timestamp}")

            original_banner_url_timestamp = 1602720001
            assert response.json["bannerMeta"] == {
                "image_credit": "none",
                "original_image_url": str(url_prefix / f"{humanize(venue.id)}_{original_banner_url_timestamp}"),
                "crop_params": {
                    "x_crop_percent": 0.0,
                    "y_crop_percent": 0.0,
                    "height_crop_percent": 0.6,
                    "width_crop_percent": 0.9,
                },
            }

    def test_upload_image_missing(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(email=user_offerer.user.email)
        url = f"/venues/{humanize(venue.id)}/banner"
        response = client.post(url)

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_BANNER_CONTENT"

    def test_upload_image_invalid_query_param(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        url = f"/venues/{humanize(venue.id)}/banner"
        url += "?x_crop_percent=0.8&y_crop_percent=invalid_value"

        image_content = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        file = {"banner": (io.BytesIO(image_content), "upsert_banner.jpg")}

        client = client.with_session_auth(email=user_offerer.user.email)
        response = client.post(url, files=file)

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_BANNER_PARAMS"

    def test_upload_image_bad_ratio(self, client, tmpdir):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # this image is too small to be resized and has a 1:1 ratio
        # it should be rejected
        image_content = (IMAGES_DIR / "mouette_small.jpg").read_bytes()
        file = {"banner": (io.BytesIO(image_content), "upsert_banner.jpg")}

        client = client.with_session_auth(email=user_offerer.user.email)
        url = f"/venues/{humanize(venue.id)}/banner"
        url += "?x_crop_percent=0.0&y_crop_percent=0.0&height_crop_percent=1.0&width_crop_percent=1.0&image_credit=none"

        # Override storage url otherwise it would be, well, an URL
        # (like http://localhost) and make some checks more difficult.
        # Override local storage and use a temporary directory instead.
        with override_settings(OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)):
            response = client.post(url, files=file)
            assert response.status_code == 400
            assert response.json["code"] == "BAD_IMAGE_RATIO"
