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
    @pytest.mark.usefixtures("db_session")
    def test_physical_product_minimal_body(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_FILM"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == "Technical provider"
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert not created_offer.isDuo
        assert created_offer.bookingEmail is None
        assert created_offer.description is None
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT

        assert response.json == {
            "productOffers": [
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "category": "SUPPORT_PHYSIQUE_FILM",
                        "ean": "1234567891234",
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

    @pytest.mark.usefixtures("db_session")
    def test_create_multiple_products(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    },
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567890987",
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
        assert second_created_offer.subcategoryId == "SUPPORT_PHYSIQUE_FILM"
        assert first_created_offer.subcategoryId == "SUPPORT_PHYSIQUE_FILM"
        assert second_created_offer.audioDisabilityCompliant is True
        assert first_created_offer.audioDisabilityCompliant is True
        assert second_created_offer.lastProvider.name == "Technical provider"
        assert first_created_offer.lastProvider.name == "Technical provider"
        assert first_created_offer.mentalDisabilityCompliant is True
        assert first_created_offer.motorDisabilityCompliant is True
        assert first_created_offer.visualDisabilityCompliant is True
        assert not second_created_offer.isDuo
        assert not first_created_offer.isDuo
        assert first_created_offer.bookingEmail is None
        assert first_created_offer.description is None
        assert first_created_offer.status == offer_mixin.OfferStatus.SOLD_OUT

        offer_1 = next(offer for offer in response.json["productOffers"] if offer["name"] == "Le champ des possibles")

        assert offer_1 == {
            "bookingContact": None,
            "bookingEmail": None,
            "categoryRelatedFields": {
                "category": "SUPPORT_PHYSIQUE_FILM",
                "ean": "1234567891234",
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
            "id": offer_2["id"],
            "accessibility": {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "bookingContact": None,
            "bookingEmail": None,
            "description": None,
            "externalTicketOfficeUrl": None,
            "image": None,
            "enableDoubleBookings": False,
            "location": {"type": "physical", "venueId": venue.id},
            "name": "Pump it",
            "status": "SOLD_OUT",
            "itemCollectionDetails": None,
            "categoryRelatedFields": {"ean": "1234567890987", "category": "SUPPORT_PHYSIQUE_FILM"},
            "stock": None,
        }

    @pytest.mark.usefixtures("db_session")
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
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_FILM"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == "Technical provider"
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is False
        assert created_offer.visualDisabilityCompliant is False
        assert created_offer.isDuo is False
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
                        "ean": "1234567891234",
                        "category": "SUPPORT_PHYSIQUE_FILM",
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

    @pytest.mark.usefixtures("db_session")
    def test_unlimited_quantity(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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

    @pytest.mark.usefixtures("db_session")
    def test_price_must_be_integer_strict(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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
        assert response.json == {"productOffers.0.stock.price": ["value is not a valid integer"]}

    @pytest.mark.usefixtures("db_session")
    def test_price_must_be_positive(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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
        assert response.json == {"productOffers.0.stock.price": ["ensure this value is greater than or equal to 0"]}

    @pytest.mark.usefixtures("db_session")
    def test_quantity_must_be_positive(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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

    @pytest.mark.usefixtures("db_session")
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
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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

    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
    def test_extra_data_deserialization(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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
        }

        assert response.json["productOffers"][0]["categoryRelatedFields"] == {
            "category": "SUPPORT_PHYSIQUE_FILM",
            "ean": "1234567891234",
        }

    @pytest.mark.usefixtures("db_session")
    def test_physical_product_attached_to_digital_venue(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_virtual=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "productOffers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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

    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
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
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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

    @pytest.mark.usefixtures("db_session")
    def test_stock_booking_limit_without_timezone(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
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

    @pytest.mark.usefixtures("db_session")
    def test_not_allowed_categories(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_virtual=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "digital", "url": "https://la-flute-en-chantier.fr", "venue_id": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {"category": "CARTE_CINE_ILLIMITE", "showType": "OPERA-GRAND_OPERA"},
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "La flûte en chantier",
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "productOffers.0.categoryRelatedFields.category": [
                "unexpected value; permitted: 'ABO_BIBLIOTHEQUE'",
                "unexpected value; permitted: 'ABO_CONCERT'",
                "unexpected value; permitted: 'ABO_LIVRE_NUMERIQUE'",
                "unexpected value; permitted: 'ABO_MEDIATHEQUE'",
                "unexpected value; permitted: 'ABO_PLATEFORME_MUSIQUE'",
                "unexpected value; permitted: 'ABO_PLATEFORME_VIDEO'",
                "unexpected value; permitted: 'ABO_PRATIQUE_ART'",
                "unexpected value; permitted: 'ABO_PRESSE_EN_LIGNE'",
                "unexpected value; permitted: 'ABO_SPECTACLE'",
                "unexpected value; permitted: 'ACHAT_INSTRUMENT'",
                "unexpected value; permitted: 'APP_CULTURELLE'",
                "unexpected value; permitted: 'AUTRE_SUPPORT_NUMERIQUE'",
                "unexpected value; permitted: 'CARTE_JEUNES'",
                "unexpected value; permitted: 'CARTE_MUSEE'",
                "unexpected value; permitted: 'LIVRE_AUDIO_PHYSIQUE'",
                "unexpected value; permitted: 'LIVRE_NUMERIQUE'",
                "unexpected value; permitted: 'LOCATION_INSTRUMENT'",
                "unexpected value; permitted: 'PARTITION'",
                "unexpected value; permitted: 'PLATEFORME_PRATIQUE_ARTISTIQUE'",
                "unexpected value; permitted: 'PODCAST'",
                "unexpected value; permitted: 'PRATIQUE_ART_VENTE_DISTANCE'",
                "unexpected value; permitted: 'SPECTACLE_ENREGISTRE'",
                "unexpected value; permitted: 'SUPPORT_PHYSIQUE_FILM'",
                "unexpected value; permitted: 'TELECHARGEMENT_LIVRE_AUDIO'",
                "unexpected value; permitted: 'TELECHARGEMENT_MUSIQUE'",
                "unexpected value; permitted: 'VISITE_VIRTUELLE'",
                "unexpected value; permitted: 'VOD'",
            ],
            "productOffers.0.categoryRelatedFields.ean": ["field required", "field required", "field required"],
            "productOffers.0.categoryRelatedFields.musicType": ["field required", "field required"],
        }
        assert offers_models.Offer.query.first() is None

    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
    def test_create_allowed_product(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_virtual=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "digital", "url": "https://la-flute-en-chantier.fr", "venue_id": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {"category": "SPECTACLE_ENREGISTRE", "showType": "OPERA-GRAND_OPERA"},
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "La flûte en chantier",
                    },
                ],
            },
        )

        assert response.status_code == 200
        assert offers_models.Offer.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_returns_404_for_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "product_offers": [
                    {
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_FILM",
                            "ean": "1234567891234",
                        },
                        "accessibility": utils.ACCESSIBILITY_FIELDS,
                        "name": "Le champ des possibles",
                    }
                ],
            },
        )

        assert response.status_code == 404
