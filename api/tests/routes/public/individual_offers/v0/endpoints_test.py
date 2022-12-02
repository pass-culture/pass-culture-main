import base64
import decimal
import pathlib
from unittest import mock

import pytest

from pcapi import settings
from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.utils import human_ids

import tests
from tests import conftest
from tests.routes import image_data


pytestmark = pytest.mark.usefixtures("db_session")

DISABILITY_COMPLIANCE_FIELDS = {
    "audioDisabilityCompliant": True,
    "mentalDisabilityCompliant": True,
    "motorDisabilityCompliant": True,
    "visualDisabilityCompliant": True,
}


class PostProductTest:
    def test_physical_product_minimal_body(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "LIVRE_PAPIER"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert not created_offer.isDuo
        assert created_offer.extraData == {}
        assert created_offer.bookingEmail is None
        assert created_offer.description is None

    @pytest.mark.usefixtures("db_session")
    def test_offer_creation_with_full_body(self, client, clear_tests_assets_bucket):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "acceptDoubleBookings": False,
                "bookingEmail": "spam@example.com",
                "categoryRelatedFields": {
                    "author": "Maurice",
                    "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                    "musicType": "100",
                    "performer": "Pink Pâtisserie",
                    "stageDirector": "Alfred",  # field not applicable
                },
                "description": "Enregistrement pour la nuit des temps",
                "disabilityCompliance": {
                    "audioDisabilityCompliant": True,
                    "mentalDisabilityCompliant": True,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                },
                "externalTicketOfficeUrl": "https://maposaic.com",
                "image": {
                    "credit": "Jean-Crédit Photo",
                    "file": image_data.GOOD_IMAGE,
                },
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "stock": {
                    "price": 1234,
                    "quantity": 3,
                },
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_MUSIQUE"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is False
        assert created_offer.visualDisabilityCompliant is False
        assert created_offer.isDuo is False
        assert created_offer.extraData == {
            "author": "Maurice",
            "musicType": "100",
            "performer": "Pink Pâtisserie",
        }
        assert created_offer.bookingEmail == "spam@example.com"
        assert created_offer.description == "Enregistrement pour la nuit des temps"
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"

        created_stock = offers_models.Stock.query.one()
        assert created_stock.price == decimal.Decimal("12.34")
        assert created_stock.quantity == 3
        assert created_stock.offer == created_offer

        created_mediation = offers_models.Mediation.query.one()
        assert created_mediation.offer == created_offer
        assert created_offer.image.url == created_mediation.thumbUrl
        assert (
            created_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(created_mediation.id)}"
        )

    def test_unlimited_quantity(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "stock": {
                    "price": 1,
                    "quantity": "unlimited",
                },
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"

        created_stock = offers_models.Stock.query.one()
        assert created_stock.price == decimal.Decimal("0.01")
        assert created_stock.quantity == None
        assert created_stock.offer == created_offer

    def test_is_duo_not_applicable(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "acceptDoubleBookings": True,
                "categoryRelatedFields": {"category": "SPECTACLE_ENREGISTRE", "showType": "100"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )
        assert response.status_code == 400
        assert offers_models.Offer.query.one_or_none() is None
        assert response.json == {"acceptDoubleBookings": ["the category chosen does not allow double bookings"]}

    @testing.override_features(WIP_ENABLE_OFFER_CREATION_API_V1=False)
    def test_api_disabled(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert offers_models.Offer.query.first() is None
        assert response.json == {"global": ["This API is not enabled"]}

    def test_digital_product(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "VOD"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "digital", "url": "https://example.com"},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "VOD"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert created_offer.url == "https://example.com"
        assert created_offer.extraData == {}

    def test_extra_data_deserialization(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {
                    "author": "Maurice",
                    "category": "CINE_VENTE_DISTANCE",
                    "stageDirector": "Alfred",
                    "isbn": "1234567891123",  # this field is not applicable and not added to extraData
                },
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "digital", "url": "https://example.com"},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()

        assert created_offer.extraData == {"author": "Maurice", "stageDirector": "Alfred"}

    def test_physical_product_attached_to_digital_venue(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_MUSIQUE", "musicType": "100"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert response.json == {"venue": ['Une offre physique ne peut être associée au lieu "Offre numérique"']}
        assert offers_models.Offer.query.first() is None

    def test_physical_product_with_digital_category(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "CINE_VENTE_DISTANCE"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "subcategory": ['Une offre de catégorie CINE_VENTE_DISTANCE doit contenir un champ "url"']
        }
        assert offers_models.Offer.query.first() is None

    def test_right_isbn_format(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE", "isbn": "1234567891123"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()

        assert created_offer.extraData == {"isbn": "1234567891123"}

    def test_wrong_isbn_format(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE", "isbn": "123456789"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "categoryRelatedFields.LIVRE_AUDIO_PHYSIQUE.isbn": ['string does not match regex "^(\\d){13}$"']
        }
        assert offers_models.Offer.query.first() is None

    def test_event_category_not_accepted(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "EVENEMENT_JEU"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert "categoryRelatedFields" in response.json
        assert offers_models.Offer.query.first() is None

    def test_venue_allowed(self, client):
        offerers_factories.ApiKeyFactory()
        not_allowed_venue = offerers_factories.VenueFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": not_allowed_venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 404
        assert response.json == {"venueId": ["There is no venue with this id associated to your API key"]}
        assert offers_models.Offer.query.first() is None

    @mock.patch("pcapi.core.offers.api.create_thumb", side_effect=Exception)
    def test_no_objects_saved_on_image_error(self, create_thumb_mock, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "image": {"file": image_data.GOOD_IMAGE},
                "stock": {"quantity": 1, "price": 100},
            },
        )

        assert response.status_code == 500
        assert response.json == {}

        assert offers_models.Offer.query.first() is None
        assert offers_models.Stock.query.first() is None

    def test_image_too_small(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "image": {"file": image_data.WRONG_IMAGE_SIZE},
                "stock": {"quantity": 1, "price": 100},
            },
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "The image is too small. It must be It must be above 400x600 pixels."}

        assert offers_models.Offer.query.first() is None
        assert offers_models.Stock.query.first() is None

    @conftest.clean_database
    def test_bad_image_ratio(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        image_bytes = (pathlib.Path(tests.__path__[0]) / "files" / "mouette_square.jpg").read_bytes()
        encoded_bytes = base64.b64encode(image_bytes)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "disabilityCompliance": DISABILITY_COMPLIANCE_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "image": {"file": encoded_bytes.decode()},
                "stock": {"quantity": 1, "price": 100},
            },
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "Bad image ratio: expected 0.66, found 1.0"}

        assert offers_models.Offer.query.first() is None
        assert offers_models.Stock.query.first() is None
