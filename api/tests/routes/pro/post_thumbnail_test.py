from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import exceptions
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Mediation
from pcapi.utils.human_ids import humanize

import tests
from tests.conftest import TestClient


IMAGES_DIR = Path(tests.__path__[0]) / "files"


@pytest.fixture(name="offer")
def offer_fixture():
    return offers_factories.ThingOfferFactory()


@pytest.fixture(name="offerer")
def offerer_fixture(offer):
    an_offerer = offer.venue.managingOfferer
    offerers_factories.UserOffererFactory(
        user__email="user@example.com",
        offerer=an_offerer,
    )
    return an_offerer


@pytest.mark.usefixtures("db_session")
class CreateThumbnailWithoutImageTest:
    def test_no_image(self, app, offer, offerer):
        # given
        client = TestClient(app.test_client()).with_session_auth(email="user@example.com")
        data = {
            "offerId": humanize(offer.id),
        }

        # when
        response = client.post("/offers/thumbnails", form=data)

        # Then
        assert response.status_code == 400
        assert response.json == {"errors": ["Nous n'avons pas réceptionné l'image, merci d'essayer à nouveau."]}


@pytest.mark.usefixtures("db_session")
class CreateThumbnailFromFileTest:
    def test_import_from_file(self, app, offer, offerer):
        # given
        client = TestClient(app.test_client()).with_session_auth(email="user@example.com")
        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        data = {
            "offerId": humanize(offer.id),
            "thumb": (BytesIO(thumb), "image.jpg"),
        }

        # when
        response = client.post("/offers/thumbnails", form=data)

        # then
        assert response.status_code == 201
        mediation = Mediation.query.one()
        assert mediation.thumbCount == 1
        assert response.json == {
            "id": humanize(mediation.id),
        }

    def test_wrong_content_type_from_file(self, app, offer, offerer):
        # given
        client = TestClient(app.test_client()).with_session_auth(email="user@example.com")
        thumb = (IMAGES_DIR / "mouette_fake_jpg.jpg").read_bytes()
        data = {
            "offerId": humanize(offer.id),
            "thumb": (BytesIO(thumb), "image.jpg"),
        }

        # when
        response = client.post("/offers/thumbnails", form=data)

        # then
        assert response.status_code == 400
        assert response.json == {"errors": ["Utilisez un format png, jpg, jpeg"]}

    @mock.patch("pcapi.core.offers.validation.check_image")
    def test_image_too_small(self, mock_check_image, app, offer, offerer):
        # given
        mock_check_image.side_effect = exceptions.ImageTooSmall(min_width=400, min_height=400)
        client = TestClient(app.test_client()).with_session_auth(email="user@example.com")
        thumb = (IMAGES_DIR / "mouette_small.jpg").read_bytes()
        data = {
            "offerId": humanize(offer.id),
            "thumb": (BytesIO(thumb), "image.jpg"),
        }

        # when
        response = client.post("/offers/thumbnails", form=data)

        # then
        mock_check_image.assert_called_once()
        assert response.status_code == 400
        assert response.json == {"errors": ["Utilisez une image plus grande (supérieure à 400px par 400px)"]}

    @mock.patch("pcapi.core.offers.validation.check_image")
    def test_content_too_large(self, mock_check_image, app, offer, offerer):
        # given
        mock_check_image.side_effect = exceptions.FileSizeExceeded(max_size=10_000_000)
        client = TestClient(app.test_client()).with_session_auth(email="user@example.com")
        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        data = {
            "offerId": humanize(offer.id),
            "thumb": (BytesIO(thumb), "image.jpg"),
        }

        # when
        response = client.post("/offers/thumbnails", form=data)

        # then
        assert response.status_code == 400
        assert response.json == {"errors": ["Utilisez une image dont le poids est inférieur à 10.0 MB"]}

    def test_bad_image_ratio(self, client, offer, offerer):
        client = client.with_session_auth(email="user@example.com")
        thumb = (IMAGES_DIR / "mouette_landscape_bigger.jpg").read_bytes()
        data = {
            "offerId": humanize(offer.id),
            "thumb": (BytesIO(thumb), "image.jpg"),
        }

        response = client.post("/offers/thumbnails", form=data)

        # then
        assert response.status_code == 400
        assert response.json["code"] == "BAD_IMAGE_RATIO"
        assert response.json["extra"] == "Bad image ratio: expected 0.6666666666666666, found 1.4989293361884368"

    def test_wrong_offer_id(self, client, offer, offerer):
        client = client.with_session_auth(email="user@example.com")
        thumb = (IMAGES_DIR / "mouette_landscape_bigger.jpg").read_bytes()
        data = {
            "offerId": humanize(offer.id + 1),
            "thumb": (BytesIO(thumb), "image.jpg"),
        }

        response = client.post("/offers/thumbnails", form=data)

        # then
        assert response.status_code == 404
        assert response.json["global"] == ["Aucun objet ne correspond à cet identifiant dans notre base de données"]
