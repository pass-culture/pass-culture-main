import datetime

from flask import url_for
import pytest

from pcapi import settings
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils import human_ids

from tests.routes import image_data

from . import utils


@pytest.mark.usefixtures("db_session")
class PatchProductTest:
    def test_deactivate_offer(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            isActive=True,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "offerId": product_offer.id,
                "isActive": False,
            },
        )

        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert product_offer.isActive is False

    def test_sets_field_to_none_and_leaves_other_unchanged(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            withdrawalDetails="Des conditions de retrait sur la sellette",
            bookingEmail="notify@example.com",
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={"offerId": product_offer.id, "itemCollectionDetails": None},
        )

        assert response.status_code == 200
        assert response.json["itemCollectionDetails"] is None
        assert product_offer.withdrawalDetails is None
        assert product_offer.bookingEmail == "notify@example.com"

    def test_update_product_image(self, client, clear_tests_assets_bucket):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue, lastProvider=api_key.provider, subcategoryId=subcategories.ABO_BIBLIOTHEQUE.id
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={"offerId": product_offer.id, "image": {"file": image_data.GOOD_IMAGE}},
        )

        assert response.status_code == 200
        assert offers_models.Mediation.query.one()
        assert (
            product_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(product_offer.activeMediation.id)}"
        )

    def test_updates_booking_email(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            bookingEmail="notify@example.com",
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={"offerId": product_offer.id, "bookingEmail": "spam@example.com"},
        )

        assert response.status_code == 200
        assert product_offer.bookingEmail == "spam@example.com"

    def test_sets_accessibility_partially(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={"offerId": product_offer.id, "accessibility": {"audioDisabilityCompliant": False}},
        )

        assert response.status_code == 200
        assert response.json["accessibility"] == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }
        assert product_offer.audioDisabilityCompliant is False
        assert product_offer.mentalDisabilityCompliant is True
        assert product_offer.motorDisabilityCompliant is True
        assert product_offer.visualDisabilityCompliant is True

    def test_create_stock(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={"offerId": product_offer.id, "stock": {"price": 1000, "quantity": 1}},
        )

        assert response.status_code == 200
        assert response.json["stock"] == {
            "bookedQuantity": 0,
            "bookingLimitDatetime": None,
            "price": 1000,
            "quantity": 1,
        }
        assert product_offer.activeStocks[0].quantity == 1
        assert product_offer.activeStocks[0].price == 10

    def test_update_stock_quantity(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, quantity=30, price=10)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={"offerId": product_offer.id, "stock": {"quantity": "unlimited"}},
        )
        assert response.status_code == 200
        assert response.json["stock"] == {
            "bookedQuantity": 0,
            "bookingLimitDatetime": None,
            "price": 1000,
            "quantity": "unlimited",
        }
        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].quantity is None

    def test_error_if_no_offer_is_found(self, client):
        utils.create_offerer_provider_linked_to_venue()
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "offerId": "33",
                "stock": {"bookingLimitDatetime": None},
            },
        )
        assert response.status_code == 404
        assert response.json == {"offerId": ["The product offer could not be found"]}

    def test_inactive_venue_provider_returns_404(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products", json={"offerId": product_offer.id, "isActive": False}
        )

        assert response.status_code == 404

    def test_remove_stock_booking_limit_datetime(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime="2021-01-15T00:00:00Z")

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "offerId": product_offer.id,
                "stock": {"bookingLimitDatetime": None},
            },
        )
        assert response.status_code == 200
        assert response.json["stock"]["bookingLimitDatetime"] is None

        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].bookingLimitDatetime is None

    def test_update_stock_booking_limit_datetime(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime=None)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={"offerId": product_offer.id, "stock": {"bookingLimitDatetime": "2021-01-15T00:00:00Z"}},
        )
        assert response.status_code == 200
        assert response.json["stock"]["bookingLimitDatetime"] == "2021-01-15T00:00:00Z"

        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].bookingLimitDatetime == datetime.datetime(2021, 1, 15, 0, 0, 0)

    def test_delete_stock(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime=None)
        confirmed_booking = bookings_factories.BookingFactory(
            stock=stock, status=bookings_models.BookingStatus.CONFIRMED
        )
        used_booking = bookings_factories.BookingFactory(stock=stock, status=bookings_models.BookingStatus.USED)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "offerId": product_offer.id,
                "stock": None,
            },
        )
        assert response.status_code == 200
        assert response.json["stock"] is None

        assert len(product_offer.activeStocks) == 0
        assert confirmed_booking.status == bookings_models.BookingStatus.CANCELLED
        assert used_booking.status == bookings_models.BookingStatus.USED

    def test_update_subcategory_raises_error(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.ABO_LUDOTHEQUE.id,
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "offerId": product_offer.id,
                "categoryRelatedFields": {
                    "category": "LIVRE_AUDIO_PHYSIQUE",
                },
            },
        )
        assert response.status_code == 400
        assert response.json == {
            "product.subcategory": [
                "Only ABO_BIBLIOTHEQUE, ABO_CONCERT, ABO_LIVRE_NUMERIQUE, ABO_MEDIATHEQUE, ABO_PLATEFORME_MUSIQUE, ABO_PLATEFORME_VIDEO, ABO_PRATIQUE_ART, ABO_PRESSE_EN_LIGNE, ABO_SPECTACLE, ACHAT_INSTRUMENT, APP_CULTURELLE, AUTRE_SUPPORT_NUMERIQUE, CAPTATION_MUSIQUE, CARTE_JEUNES, CARTE_MUSEE, LIVRE_AUDIO_PHYSIQUE, LIVRE_NUMERIQUE, LOCATION_INSTRUMENT, PARTITION, PLATEFORME_PRATIQUE_ARTISTIQUE, PODCAST, PRATIQUE_ART_VENTE_DISTANCE, SPECTACLE_ENREGISTRE, SUPPORT_PHYSIQUE_FILM, TELECHARGEMENT_LIVRE_AUDIO, TELECHARGEMENT_MUSIQUE, VISITE_VIRTUELLE, VOD products can be edited"
            ]
        }

    def test_update_unallowed_subcategory_product_raises_error(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            bookingEmail="notify@example.com",
            lastProvider=api_key.provider,
            subcategoryId=subcategories.CARTE_CINE_ILLIMITE.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "offerId": product_offer.id,
                "bookingEmail": "spam@example.com",
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "product.subcategory": [
                "Only ABO_BIBLIOTHEQUE, ABO_CONCERT, ABO_LIVRE_NUMERIQUE, ABO_MEDIATHEQUE, ABO_PLATEFORME_MUSIQUE, ABO_PLATEFORME_VIDEO, ABO_PRATIQUE_ART, ABO_PRESSE_EN_LIGNE, ABO_SPECTACLE, ACHAT_INSTRUMENT, APP_CULTURELLE, AUTRE_SUPPORT_NUMERIQUE, CAPTATION_MUSIQUE, CARTE_JEUNES, CARTE_MUSEE, LIVRE_AUDIO_PHYSIQUE, LIVRE_NUMERIQUE, LOCATION_INSTRUMENT, PARTITION, PLATEFORME_PRATIQUE_ARTISTIQUE, PODCAST, PRATIQUE_ART_VENTE_DISTANCE, SPECTACLE_ENREGISTRE, SUPPORT_PHYSIQUE_FILM, TELECHARGEMENT_LIVRE_AUDIO, TELECHARGEMENT_MUSIQUE, VISITE_VIRTUELLE, VOD products can be edited"
            ]
        }

    def test_update_name_and_description(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )

        offer_id = product_offer.id
        new_name = product_offer.name + " updated"
        new_desc = product_offer.description + " updated"

        # 1. get api key
        # 2. check FF
        # 3. get offer and related data
        # 4. update offer
        # 5. reload provider
        # 6. reload offer and related data (before serialization)
        with assert_num_queries(6):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                url_for("public_api.edit_product"),
                json={"offerId": offer_id, "name": new_name, "description": new_desc},
            )

            assert response.status_code == 200
            assert response.json["name"] == new_name
            assert response.json["description"] == new_desc

        db.session.refresh(product_offer)
        assert product_offer.name == new_name
        assert product_offer.description == new_desc
