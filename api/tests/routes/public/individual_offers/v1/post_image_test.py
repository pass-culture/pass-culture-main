import typing
from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.utils import human_ids

import tests
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


IMAGES_DIR = Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class PostProductImageTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/{offer_id}/image"
    endpoint_method = "post"
    default_path_params = {"offer_id": 123435}

    def _get_valid_form(self) -> dict:
        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        return {"file": (BytesIO(thumb), "image.jpg"), "credit": "John Do"}

    @staticmethod
    def setup_base_resource(
        venue: offerers_models.Venue, provider: providers_models.Provider | None = None, **extra: typing.Any
    ) -> offers_models.Offer:
        base_kwargs = {
            "venue": venue,
            "lastProviderId": provider and provider.id,
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "description": "Un livre de contrepèterie",
            "name": "Vieux motard que jamais",
            "ean": "1234567890123",
        }

        return offers_factories.ThingOfferFactory(**{**base_kwargs, **extra})

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        offer = self.setup_base_resource(venue)

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, form_body=self._get_valid_form())

        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        venue = venue_provider.venue
        offer = self.setup_base_resource(venue)
        response = self.make_request(plain_api_key, {"offer_id": offer.id}, form_body=self._get_valid_form())

        assert response.status_code == 404

    def test_post_image_with_credit_test(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, form_body=self._get_valid_form())

        assert response.status_code == 204
        mediation = db.session.query(offers_models.Mediation).one()
        assert mediation.thumbCount == 1
        assert offer.image == offers_models.OfferImage(
            url=f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(mediation.id)}", credit="John Do"
        )

    @pytest.mark.parametrize(
        "payload,expected_response_json",
        [
            # no image
            ({"credit": "John Do"}, {"file": ["A file must be provided in the request"]}),
            # bad ratio
            (
                {"file": (BytesIO((IMAGES_DIR / "mouette_square.jpg").read_bytes()), "image.jpg"), "credit": "John Do"},
                {"file": "Bad image ratio: expected 0.66, found 1.0"},
            ),
            # wrong content type
            (
                {"file": (BytesIO((IMAGES_DIR / "mouette_fake_jpg.jpg").read_bytes()), "image.jpg")},
                {"file": "The file is not a valid image."},
            ),
        ],
    )
    def test_returns_400(self, payload, expected_response_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, form_body=payload)

        assert response.status_code == 400
        assert response.json == expected_response_json

    @mock.patch("pcapi.core.offers.validation.check_image")
    def test_returns_400_image_too_small(self, mock_check_image, client):
        mock_check_image.side_effect = exceptions.ImageTooSmall(min_width=400, min_height=400)
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)

        thumb = (IMAGES_DIR / "mouette_small.jpg").read_bytes()

        payload = {"file": (BytesIO(thumb), "image.jpg")}
        response = self.make_request(plain_api_key, {"offer_id": offer.id}, form_body=payload)

        assert response.status_code == 400
        assert response.json == {"file": "The image is too small. It must be above 400x600 pixels."}

    @mock.patch("pcapi.core.offers.validation.check_image")
    def test_returns_400_content_too_large(self, mock_check_image, client):
        mock_check_image.side_effect = exceptions.FileSizeExceeded(max_size=10_000_000)
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        payload = {"file": (BytesIO(thumb), "image.jpg")}

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, form_body=payload)

        assert response.status_code == 400
        assert response.json == {"file": "The file is too large. It must be less than 10000000 bytes."}
