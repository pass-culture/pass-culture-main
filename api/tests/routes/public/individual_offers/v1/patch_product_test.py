import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils



class PatchProductTest:
    def test_deactivate_offer(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            isActive=True,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "isActive": False},
                ]
            },
        )

        assert response.status_code == 200
        assert response.json["productOffers"][0]["status"] == "INACTIVE"
        assert product_offer.isActive is False

    def test_sets_field_to_none_and_leaves_other_unchanged(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            withdrawalDetails="Des conditions de retrait sur la sellette",
            bookingEmail="notify@example.com",
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "itemCollectionDetails": None},
                ]
            },
        )

        assert response.status_code == 200
        assert response.json["productOffers"][0]["itemCollectionDetails"] is None
        assert product_offer.withdrawalDetails is None
        assert product_offer.bookingEmail == "notify@example.com"

    def test_updates_booking_email(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            bookingEmail="notify@example.com",
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "bookingEmail": "spam@example.com"},
                ]
            },
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
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "accessibility": {"audioDisabilityCompliant": False}},
                ]
            },
        )

        assert response.status_code == 200
        assert response.json["productOffers"][0]["accessibility"] == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }
        assert product_offer.audioDisabilityCompliant is False
        assert product_offer.mentalDisabilityCompliant is True
        assert product_offer.motorDisabilityCompliant is True
        assert product_offer.visualDisabilityCompliant is True

    def test_update_extra_data_partially(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId="SUPPORT_PHYSIQUE_MUSIQUE",
            extraData={
                "author": "Maurice",
                "musicType": "501",
                "musicSubType": "508",
                "performer": "Pink Pâtisserie",
            },
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {
                        "offer_id": product_offer.id,
                        "categoryRelatedFields": {
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                            "musicType": "JAZZ-ACID_JAZZ",
                        },
                    },
                ]
            },
        )
        assert response.status_code == 200
        assert response.json["productOffers"][0]["categoryRelatedFields"] == {
            "author": "Maurice",
            "ean": None,
            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
            "musicType": "JAZZ-ACID_JAZZ",
            "performer": "Pink Pâtisserie",
        }
        assert product_offer.extraData == {
            "author": "Maurice",
            "musicSubType": "502",
            "musicType": "501",
            "performer": "Pink Pâtisserie",
        }

    def test_create_stock(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "stock": {"price": 1000, "quantity": 1}},
                ]
            },
        )

        assert response.status_code == 200
        assert response.json["productOffers"][0]["stock"] == {
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
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, quantity=30, price=10)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "stock": {"quantity": "unlimited"}},
                ]
            },
        )
        assert response.status_code == 200
        assert response.json["productOffers"][0]["stock"] == {
            "bookedQuantity": 0,
            "bookingLimitDatetime": None,
            "price": 1000,
            "quantity": "unlimited",
        }
        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].quantity is None

    def test_update_multiple_offers(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, quantity=30, price=10)

        product_offer_2 = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId="SUPPORT_PHYSIQUE_MUSIQUE",
            extraData={
                "author": "Maurice",
                "musicType": "501",
                "musicSubType": "508",
                "performer": "Pink Pâtisserie",
            },
            lastProvider=api_key.provider,
        )

        product_offer_3 = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "stock": {"quantity": "unlimited", "price": 15}},
                    {
                        "offer_id": product_offer_2.id,
                        "accessibility": {"audioDisabilityCompliant": False},
                        "categoryRelatedFields": {
                            "musicType": "JAZZ-ACID_JAZZ",
                            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                        },
                    },
                    {"offer_id": product_offer_3.id, "stock": {"price": 1000, "quantity": 1}},
                ]
            },
        )
        assert response.status_code == 200
        assert len(response.json["productOffers"]) == 3
        assert stock != None

    def test_error_if_no_offer_is_found(self, client):
        utils.create_offerer_provider_linked_to_venue()
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": "33", "stock": {"bookingLimitDatetime": None}},
                    {"offer_id": "35", "stock": {"bookingLimitDatetime": None}},
                    {"offer_id": "32", "stock": {"bookingLimitDatetime": None}},
                ]
            },
        )
        assert response.status_code == 404
        assert response.json == {"productOffers": ["The product offers could not be found"]}

    def test_error_if_at_least_one_offer_is_found(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "stock": {"bookingLimitDatetime": None}},
                    {"offer_id": "35", "stock": {"bookingLimitDatetime": None}},
                    {"offer_id": "32", "stock": {"bookingLimitDatetime": None}},
                ]
            },
        )
        assert response.status_code == 404
        assert response.json == {"productOffers": ["The product offers could not be found"]}

    def test_remove_stock_booking_limit_datetime(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime="2021-01-15T00:00:00Z")

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "stock": {"bookingLimitDatetime": None}},
                ]
            },
        )
        assert response.status_code == 200
        assert response.json["productOffers"][0]["stock"]["bookingLimitDatetime"] is None

        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].bookingLimitDatetime is None

    def test_update_stock_booking_limit_datetime(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime=None)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "stock": {"bookingLimitDatetime": "2021-01-15T00:00:00Z"}},
                ]
            },
        )
        assert response.status_code == 200
        assert response.json["productOffers"][0]["stock"]["bookingLimitDatetime"] == "2021-01-15T00:00:00"

        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].bookingLimitDatetime == datetime.datetime(2021, 1, 15, 0, 0, 0)

    def test_delete_stock(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime=None)
        confirmed_booking = bookings_factories.BookingFactory(
            stock=stock, status=bookings_models.BookingStatus.CONFIRMED
        )
        used_booking = bookings_factories.BookingFactory(stock=stock, status=bookings_models.BookingStatus.USED)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "stock": None},
                ]
            },
        )
        assert response.status_code == 200
        assert response.json["productOffers"][0]["stock"] is None

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
                "product_offers": [
                    {
                        "offer_id": product_offer.id,
                        "categoryRelatedFields": {
                            "category": "LIVRE_AUDIO_PHYSIQUE",
                        },
                    }
                ]
            },
        )
        assert response.status_code == 400
        assert response.json == {
            "productOffers.0.categoryRelatedFields.category": [
                "unexpected value; permitted: 'SUPPORT_PHYSIQUE_MUSIQUE'"
            ]
        }

    def test_update_unallowed_subcategory_product_raises_error(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            bookingEmail="notify@example.com",
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/products",
            json={
                "product_offers": [
                    {"offer_id": product_offer.id, "bookingEmail": "spam@example.com"},
                ]
            },
        )

        assert response.status_code == 400
        assert response.json == {"product.subcategory": ["Only SUPPORT_PHYSIQUE_MUSIQUE products can be edited"]}
