from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.utils import human_ids

import tests

from . import utils


IMAGES_DIR = Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class PostProductTest:
    def test_post_image_with_credit_test(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        data = {"file": (BytesIO(thumb), "image.jpg"), "credit": "John Do"}

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/{offer.id}/image", form=data
        )

        assert response.status_code == 204
        mediation = offers_models.Mediation.query.one()
        assert mediation.thumbCount == 1
        assert offer.image == offers_models.OfferImage(
            url=f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(mediation.id)}", credit="John Do"
        )

    def test_returns_400_if_no_image(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        data = {"credit": "John Do"}

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/{offer.id}/image", form=data
        )

        assert response.status_code == 400
        assert response.json == {"file": ["A file must be provided in the request"]}

    def test_returns_400_if_bad_ratio_image(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        thumb = (IMAGES_DIR / "mouette_square.jpg").read_bytes()
        data = {"file": (BytesIO(thumb), "image.jpg"), "credit": "John Do"}

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/{offer.id}/image", form=data
        )

        assert response.status_code == 400
        assert response.json == {"file": "Bad image ratio: expected 0.66, found 1.0"}

    def test_returns_400_wrong_content_type(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        thumb = (IMAGES_DIR / "mouette_fake_jpg.jpg").read_bytes()
        data = {
            "file": (BytesIO(thumb), "image.jpg"),
        }

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/{offer.id}/image", form=data
        )

        assert response.status_code == 400
        assert response.json == {"file": "The file is not a valid image."}

    @mock.patch("pcapi.core.offers.validation.check_image")
    def test_returns_400_image_too_small(self, mock_check_image, client):
        mock_check_image.side_effect = exceptions.ImageTooSmall(min_width=400, min_height=400)
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        thumb = (IMAGES_DIR / "mouette_small.jpg").read_bytes()
        data = {
            "file": (BytesIO(thumb), "image.jpg"),
        }

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/{offer.id}/image", form=data
        )

        assert response.status_code == 400
        assert response.json == {"file": "The image is too small. It must be above 400x600 pixels."}

    @mock.patch("pcapi.core.offers.validation.check_image")
    def test_returns_400_content_too_large(self, mock_check_image, client):
        mock_check_image.side_effect = exceptions.FileSizeExceeded(max_size=10_000_000)
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        data = {
            "file": (BytesIO(thumb), "image.jpg"),
        }

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/{offer.id}/image", form=data
        )

        assert response.status_code == 400
        assert response.json == {"file": "The file is too large. It must be less than 10000000 bytes."}

    def test_returns_401_if_no_token_provided(self, client):
        thumb = (IMAGES_DIR / "mouette_small.jpg").read_bytes()
        data = {"file": (BytesIO(thumb), "image.jpg"), "credit": "John Do"}

        response = client.post("/public/offers/v1/12/image", form=data)

        assert response.status_code == 401
