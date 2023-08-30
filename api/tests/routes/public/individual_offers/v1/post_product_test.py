import base64
import datetime
import decimal
import pathlib
from unittest import mock

import freezegun
import pytest

from pcapi import settings
from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import offer_mixin
from pcapi.utils import human_ids

import tests
from tests import conftest
from tests.routes import image_data

from . import utils


class PostProductTest:

    def test_physical_product_minimal_body(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    }
                ],
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_MUSIQUE"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == "Technical provider"
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert not created_offer.isDuo
        assert created_offer.extraData == {"ean": "1234567891234", "musicType": "820", "musicSubType": "829"}
        assert created_offer.bookingEmail is None
        assert created_offer.description is None
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT

        assert response.json == {
            "productOffers": [
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "author": None,
                        "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                        "ean": "1234567891234",
                        "musicType": "ROCK-LO_FI",
                        "performer": None,
                    },
                    "description": None,
                    "accessibility": {
                        "audioDisabilityCompliant": True,
                        "mentalDisabilityCompliant": True,
                        "motorDisabilityCompliant": True,
                        "visualDisabilityCompliant": True,
                    },
                    "enableDoubleBookings": False,
                    "externalTicketOfficeUrl": None,
                    "id": created_offer.id,
                    "image": None,
                    "itemCollectionDetails": None,
                    "location": {"type": "physical", "venueId": venue.id},
                    "name": "Le champ des possibles",
                    "status": "SOLD_OUT",
                    "stock": None,
                }
            ]
        }


    def test_create_multiple_products(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    },
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567890987",
                            "musicType": "HIP_HOP_RAP-RAP_OLD_SCHOOL",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Pump it",
                    },
                ],
            },
        )

        assert response.status_code == 200
        created_offers = offers_models.Offer.query.order_by(offers_models.Offer.extraData.name).all()
        first_created_offer = next(offer for offer in created_offers if offer.name == "Le champ des possibles")
        second_created_offer = next(offer for offer in created_offers if offer.name == "Pump it")
        assert second_created_offer.name == "Pump it"
        assert first_created_offer.name == "Le champ des possibles"
        assert second_created_offer.venue == venue
        assert first_created_offer.venue == venue
        assert second_created_offer.subcategoryId == "SUPPORT_PHYSIQUE_MUSIQUE"
        assert first_created_offer.subcategoryId == "SUPPORT_PHYSIQUE_MUSIQUE"
        assert second_created_offer.audioDisabilityCompliant is True
        assert first_created_offer.audioDisabilityCompliant is True
        assert second_created_offer.lastProvider.name == "Technical provider"
        assert first_created_offer.lastProvider.name == "Technical provider"
        assert first_created_offer.mentalDisabilityCompliant is True
        assert first_created_offer.motorDisabilityCompliant is True
        assert first_created_offer.visualDisabilityCompliant is True
        assert not second_created_offer.isDuo
        assert not first_created_offer.isDuo
        assert second_created_offer.extraData == {"ean": "1234567890987", "musicType": "900", "musicSubType": "910"}
        assert first_created_offer.extraData == {"ean": "1234567891234", "musicType": "820", "musicSubType": "829"}
        assert first_created_offer.bookingEmail is None
        assert first_created_offer.description is None
        assert first_created_offer.status == offer_mixin.OfferStatus.SOLD_OUT

        offer_1 = next(offer for offer in response.json["productOffers"] if offer["name"] == "Le champ des possibles")

        assert offer_1 == {
            "bookingContact": None,
            "bookingEmail": None,
            "categoryRelatedFields": {
                "author": None,
                "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                "ean": "1234567891234",
                "musicType": "ROCK-LO_FI",
                "performer": None,
            },
            "description": None,
            "accessibility": {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "id": created_offers[1].id,
            "image": None,
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": venue.id},
            "name": "Le champ des possibles",
            "status": "SOLD_OUT",
            "stock": None,
        }

        offer_2 = next(offer for offer in response.json["productOffers"] if offer["name"] == "Pump it")

        assert offer_2 == {
            "bookingContact": None,
            "bookingEmail": None,
            "categoryRelatedFields": {
                "author": None,
                "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                "ean": "1234567890987",
                "musicType": "HIP_HOP_RAP-RAP_OLD_SCHOOL",
                "performer": None,
            },
            "description": None,
            "accessibility": {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "id": created_offers[0].id,
            "image": None,
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": venue.id},
            "name": "Pump it",
            "status": "SOLD_OUT",
            "stock": None,
        }


    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_product_creation_with_full_body(self, client, clear_tests_assets_bucket):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "enableDoubleBookings": False,
                        "bookingContact": "contact@example.com",
                        "bookingEmail": "spam@example.com",
                        "categoryRelatedFields": {
                            "author": "Maurice",
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "JAZZ-FUSION",
                            "performer": "Pink Pâtisserie",
                            "stageDirector": "Alfred",  # field not applicable
                        },
                        "description": "Enregistrement pour la nuit des temps",
                        "accessibility": {
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
                        "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
                        "name": "Le champ des possibles",
                        "stock": {
                            "bookingLimitDatetime": "2022-01-01T16:00:00+04:00",
                            "price": 1234,
                            "quantity": 3,
                        },
                    }
                ],
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_MUSIQUE"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == "Technical provider"
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is False
        assert created_offer.visualDisabilityCompliant is False
        assert created_offer.isDuo is False
        assert created_offer.extraData == {
            "author": "Maurice",
            "ean": "1234567891234",
            "musicType": "501",
            "musicSubType": "511",
            "performer": "Pink Pâtisserie",
        }
        assert created_offer.bookingEmail == "spam@example.com"
        assert created_offer.description == "Enregistrement pour la nuit des temps"
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.status == offer_mixin.OfferStatus.EXPIRED
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"

        created_stock = offers_models.Stock.query.one()
        assert created_stock.price == decimal.Decimal("12.34")
        assert created_stock.quantity == 3
        assert created_stock.offer == created_offer
        assert created_stock.bookingLimitDatetime == datetime.datetime(2022, 1, 1, 12, 0, 0)

        created_mediation = offers_models.Mediation.query.one()
        assert created_mediation.offer == created_offer
        assert created_offer.image.url == created_mediation.thumbUrl
        assert (
            created_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(created_mediation.id)}"
        )

        assert response.json == {
            "productOffers": [
                {
                    "bookingContact": "contact@example.com",
                    "bookingEmail": "spam@example.com",
                    "categoryRelatedFields": {
                        "author": "Maurice",
                        "ean": "1234567891234",
                        "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                        "musicType": "JAZZ-FUSION",
                        "performer": "Pink Pâtisserie",
                    },
                    "description": "Enregistrement pour la nuit des temps",
                    "accessibility": {
                        "audioDisabilityCompliant": True,
                        "mentalDisabilityCompliant": True,
                        "motorDisabilityCompliant": False,
                        "visualDisabilityCompliant": False,
                    },
                    "enableDoubleBookings": False,
                    "externalTicketOfficeUrl": "https://maposaic.com",
                    "id": created_offer.id,
                    "image": {
                        "credit": "Jean-Crédit Photo",
                        "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(created_mediation.id)}",
                    },
                    "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
                    "location": {"type": "physical", "venueId": venue.id},
                    "name": "Le champ des possibles",
                    "status": "EXPIRED",
                    "stock": {
                        "bookedQuantity": 0,
                        "bookingLimitDatetime": "2022-01-01T12:00:00",
                        "price": 1234,
                        "quantity": 3,
                    },
                }
            ],
        }


    def test_unlimited_quantity(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                        "stock": {
                            "bookedQuantity": 0,
                            "price": 1,
                            "quantity": "unlimited",
                        },
                    }
                ],
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.status == offer_mixin.OfferStatus.ACTIVE

        created_stock = offers_models.Stock.query.one()
        assert created_stock.price == decimal.Decimal("0.01")
        assert created_stock.quantity is None
        assert created_stock.offer == created_offer


    def test_price_must_be_integer_strict(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                        "stock": {
                            "price": 12.34,
                            "quantity": "unlimited",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"productOffers.0.stock.price": ["Saisissez un nombre valide"]}


    def test_price_must_be_positive(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                        "stock": {
                            "price": -1200,
                            "quantity": "unlimited",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"productOffers.0.stock.price": ["Value must be positive"]}


    def test_quantity_must_be_positive(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                        "stock": {
                            "price": 1200,
                            "quantity": -1,
                        },
                    }
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"productOffers.0.stock.quantity": ["Value must be positive"]}


    def test_is_duo_not_applicable(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "enableDoubleBookings": True,
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    },
                ],
            },
        )
        assert response.status_code == 400
        assert offers_models.Offer.query.one_or_none() is None
        assert response.json == {"enableDoubleBookings": ["the category chosen does not allow double bookings"]}


    @testing.override_features(WIP_ENABLE_OFFER_CREATION_API_V1=False)
    def test_api_disabled(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {"category": "SPECTACLE_ENREGISTRE"},
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert offers_models.Offer.query.first() is None
        assert response.json == {"global": ["This API is not enabled"]}


    def test_extra_data_deserialization(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                            "performer": "Ichika Nito",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    },
                ],
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()

        assert created_offer.extraData == {
            "ean": "1234567891234",
            "musicType": "820",
            "musicSubType": "829",
            "performer": "Ichika Nito",
        }

        assert response.json["productOffers"][0]["categoryRelatedFields"] == {
            "author": None,
            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
            "ean": "1234567891234",
            "musicType": "ROCK-LO_FI",
            "performer": "Ichika Nito",
        }


    def test_physical_product_attached_to_digital_venue(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_virtual=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "CHANSON_VARIETE-OTHER",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"venue": ['Une offre physique ne peut être associée au lieu "Offre numérique"']}
        assert offers_models.Offer.query.first() is None


    def test_event_category_not_accepted(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {"category": "EVENEMENT_JEU"},
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert "productOffers.0.categoryRelatedFields.category" in response.json
        assert offers_models.Offer.query.first() is None


    def test_venue_allowed(self, client):
        utils.create_offerer_provider_linked_to_venue()
        not_allowed_venue = offerers_factories.VenueFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": not_allowed_venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    },
                ],
            },
        )

        assert response.status_code == 404
        assert response.json == {"venueId": ["There is no venue with this id associated to your API key"]}
        assert offers_models.Offer.query.first() is None

    @conftest.clean_database
    @mock.patch("pcapi.core.offers.api.create_thumb", side_effect=Exception)
    # this test needs "clean_database" instead of "db_session" fixture because with the latter, the mediation would still be present in databse
    def test_no_objects_saved_on_image_error(self, create_thumb_mock, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                        "image": {"file": image_data.GOOD_IMAGE},
                        "stock": {"quantity": 1, "price": 100},
                    },
                ],
            },
        )

        assert response.status_code == 500
        assert response.json == {}

        assert offers_models.Offer.query.first() is None
        assert offers_models.Stock.query.first() is None

    @conftest.clean_database
    def test_image_too_small(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                        "image": {"file": image_data.WRONG_IMAGE_SIZE},
                        "stock": {"quantity": 1, "price": 100},
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "The image is too small. It must be above 400x600 pixels."}

        assert offers_models.Offer.query.first() is None
        assert offers_models.Stock.query.first() is None

    @conftest.clean_database
    def test_bad_image_ratio(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        image_bytes = (pathlib.Path(tests.__path__[0]) / "files" / "mouette_square.jpg").read_bytes()
        encoded_bytes = base64.b64encode(image_bytes)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                        "image": {"file": encoded_bytes.decode()},
                        "stock": {"quantity": 1, "price": 100},
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "Bad image ratio: expected 0.66, found 1.0"}

        assert offers_models.Offer.query.first() is None
        assert offers_models.Stock.query.first() is None


    def test_stock_booking_limit_without_timezone(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "ean": "1234567891234",
                            "musicType": "ROCK-LO_FI",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                        "stock": {"bookingLimitDatetime": "2021-01-01T00:00:00", "price": 10, "quantity": 10},
                    },
                ],
            },
        )

        assert response.status_code == 400

        assert response.json == {
            "productOffers.0.stock.bookingLimitDatetime": ["The datetime must be timezone-aware."],
        }


    def test_only_physical_music_is_allowed(self, client):
        utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "digital", "url": "https://la-flute-en-chantier.fr"},
                "product_offers": [
                    {
                        "categoryRelatedFields": {"category": "SPECTACLE_ENREGISTRE", "showType": "OPERA-GRAND_OPERA"},
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "location": {"type": "digital", "url": "https://la-flute-en-chantier.fr"},
                        "name": "La flûte en chantier",
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert "productOffers.0.categoryRelatedFields.category" in response.json
        assert "SUPPORT_PHYSIQUE_MUSIQUE" in response.json["productOffers.0.categoryRelatedFields.category"][0]
        assert offers_models.Offer.query.first() is None


    def test_books_are_not_allowed(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "LIVRE_PAPIER",
                            "ean": "1234567890123",
                            "author": "Maurice",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "A qui mieux mieux",
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert offers_models.Offer.query.count() == 0
