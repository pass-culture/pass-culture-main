from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
import requests_mock

import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Mediation
from pcapi.models import ApiErrors
from pcapi.routes.serialization import mediations_serialize
from pcapi.utils.human_ids import humanize

import tests
from tests.conftest import TestClient


IMAGES_DIR = Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class Returns201:
    def when_mediation_is_created_with_thumb_url(self, app):
        # given
        offer = offers_factories.ThingOfferFactory()
        offerer = offer.venue.managingOfferer
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )

        # when
        client = TestClient(app.test_client()).with_auth(email="user@example.com")
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        data = {
            "offerId": humanize(offer.id),
            "offererId": humanize(offerer.id),
            "thumbUrl": "https://example.com/image.jpg",
        }
        with requests_mock.Mocker() as mock:
            mock.get(
                "https://example.com/image.jpg",
                content=image_as_bytes,
                headers={"Content-Type": "image/jpeg"},
            )
            response = client.post("/mediations", form=data)

        # then
        assert response.status_code == 201
        mediation = Mediation.query.one()
        assert mediation.thumbCount == 1
        assert response.json == {
            "id": humanize(mediation.id),
        }

    def when_mediation_is_created_with_thumb_file(self, app):
        # given
        offer = offers_factories.ThingOfferFactory()
        offerer = offer.venue.managingOfferer
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )

        # when
        client = TestClient(app.test_client()).with_auth(email="user@example.com")
        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        files = {
            "offerId": humanize(offer.id),
            "offererId": humanize(offerer.id),
            "thumb": (BytesIO(thumb), "image.png"),
        }
        response = client.post("/mediations", files=files)

        # then
        assert response.status_code == 201
        mediation = Mediation.query.one()
        assert mediation.thumbCount == 1
        assert response.status_code == 201


@pytest.mark.usefixtures("db_session")
class Returns400:
    def when_mediation_is_created_with_bad_thumb_url(self, app):
        # given
        offer = offers_factories.ThingOfferFactory()
        offerer = offer.venue.managingOfferer
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )

        # when
        client = TestClient(app.test_client()).with_auth(email="user@example.com")
        data = {
            "offerId": humanize(offer.id),
            "offererId": humanize(offerer.id),
            "thumbUrl": "https://example.com/image.jpg",
        }
        with requests_mock.Mocker() as mock:
            mock.get("https://example.com/image.jpg", status_code=404)
            response = client.post("/mediations", form=data)

        # then
        assert response.status_code == 400
        assert response.json == {"thumbUrl": ["L'adresse saisie n'est pas valide"]}


class CreateMediationBodyModelTest:
    class FakeRequest:
        class _File(BytesIO):
            def __init__(self, filename, *args, **kwargs):
                self.filename = filename
                super().__init__(*args, **kwargs)

        def __init__(self, filename="", file_as_bytes=None):
            self.files = {}
            if file_as_bytes:
                self.files["thumb"] = self._File(filename, file_as_bytes)

    def test_get_image_as_bytes_requires_url_or_uploaded_file(self):
        pass

    def test_get_image_as_bytes_from_uploaded_file(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        request = self.FakeRequest(filename="image.jpg", file_as_bytes=image_as_bytes)
        deserializer = mediations_serialize.CreateMediationBodyModel(offerId=1, offererId=1)
        assert deserializer.get_image_as_bytes(request) == image_as_bytes

    def test_get_image_as_bytes_from_uploaded_file_fails_if_wrong_extension(self):
        image_as_bytes = b"whatever"
        request = self.FakeRequest(filename="image.pdf", file_as_bytes=image_as_bytes)
        deserializer = mediations_serialize.CreateMediationBodyModel(offerId=1, offererId=1)
        with pytest.raises(ApiErrors) as error:
            deserializer.get_image_as_bytes(request)
        assert "ou son format n'est pas autorisé" in error.value.errors["thumb"][0]

    def test_get_image_as_bytes_from_url(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        request = self.FakeRequest()
        deserializer = mediations_serialize.CreateMediationBodyModel(
            offerId=1, offererId=1, thumbUrl="https://www.example.com/image.jpg"
        )
        with requests_mock.Mocker() as mock:
            mock.get(
                "https://www.example.com/image.jpg",
                content=image_as_bytes,
                headers={"Content-Type": "image/jpeg"},
            )
            assert deserializer.get_image_as_bytes(request) == image_as_bytes

    def test_get_image_as_bytes_from_url_fails_if_invalid_url(self):
        request = self.FakeRequest()
        deserializer = mediations_serialize.CreateMediationBodyModel(offerId=1, offererId=1, thumbUrl="an invalid url")
        with pytest.raises(ApiErrors) as error:
            deserializer.get_image_as_bytes(request)
        assert error.value.errors["thumbUrl"] == ["L'adresse saisie n'est pas valide"]

    def test_get_image_as_bytes_from_url_fails_if_wrong_content_type(self):
        request = self.FakeRequest()
        deserializer = mediations_serialize.CreateMediationBodyModel(
            offerId=1, offererId=1, thumbUrl="https://www.example.com/image.jpg"
        )
        with requests_mock.Mocker() as mock:
            mock.get(
                "https://www.example.com/image.jpg",
                content=b"whatever",
                headers={"Content-Type": "application/pdf"},
            )
            with pytest.raises(ApiErrors) as error:
                deserializer.get_image_as_bytes(request)
            assert error.value.errors["thumbUrl"] == ["L'adresse saisie n'est pas valide"]

    def test_get_image_as_bytes_from_url_fails_if_wrong_status_code(self):
        request = self.FakeRequest()
        deserializer = mediations_serialize.CreateMediationBodyModel(
            offerId=1, offererId=1, thumbUrl="https://www.example.com/image.jpg"
        )
        with requests_mock.Mocker() as mock:
            mock.get("https://www.example.com/image.jpg", status_code=404)
            with pytest.raises(ApiErrors) as error:
                deserializer.get_image_as_bytes(request)
            assert error.value.errors["thumbUrl"] == ["L'adresse saisie n'est pas valide"]

    @patch("pcapi.utils.requests.get")
    def test_get_image_as_bytes_from_url_fails_if_request_error(self, mocked_get):
        request = self.FakeRequest()
        deserializer = mediations_serialize.CreateMediationBodyModel(
            offerId=1, offererId=1, thumbUrl="https://www.example.com/image.jpg"
        )
        mocked_get.side_effect = ValueError("Connection timeout or something like that")
        with pytest.raises(ApiErrors) as error:
            deserializer.get_image_as_bytes(request)
        assert error.value.errors["thumbUrl"] == ["Impossible de télécharger l'image à cette adresse"]
