import datetime
import decimal

import freezegun
import pytest

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.utils import human_ids

from . import utils


@pytest.mark.usefixtures("db_session")
class GetEventTest:
    def test_404_when_requesting_a_product(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.ThingOfferFactory(venue__managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event offer could not be found"]}

    def test_get_event(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product = offers_factories.ProductFactory(thumbCount=1)
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            product=product,
        )
        event_offer_id = event_offer.id

        num_query = 1  # feature flag WIP_ENABLE_OFFER_CREATION_API_V1
        num_query += 1  # retrieve API key
        num_query += 1  # retrieve offer

        with testing.assert_num_queries(num_query):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer_id}"
            )

        assert response.status_code == 200
        assert response.json == {
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
            },
            "bookingContact": None,
            "bookingEmail": None,
            "categoryRelatedFields": {"author": None, "category": "SEANCE_CINE", "stageDirector": None, "visa": None},
            "description": "Un livre de contrepèterie",
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "eventDuration": None,
            "id": event_offer.id,
            "image": {
                "credit": None,
                "url": f"http://localhost/storage/thumbs/products/{human_ids.humanize(product.id)}",
            },
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": event_offer.venueId},
            "name": "Vieux motard que jamais",
            "status": "SOLD_OUT",
            "ticketCollection": None,
            "priceCategories": [],
        }

    def test_event_with_not_selectable_category_can_be_retrieved(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            subcategoryId=subcategories.DECOUVERTE_METIERS.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {"category": "DECOUVERTE_METIERS", "speaker": None}

    def test_get_show_offer_without_show_type(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
            venue=venue,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )
        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "SPECTACLE_REPRESENTATION",
            "performer": None,
            "showType": None,
            "stageDirector": None,
        }

    def test_get_music_offer_without_music_type(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )
        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "CONCERT",
            "performer": None,
            "musicType": None,
        }

    def test_ticket_collection_by_email(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=259201,  # 3 days + 1 second
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["ticketCollection"] == {"daysBeforeEvent": 3, "way": "by_email"}

    def test_ticket_collection_on_site(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=1801,  # 30 minutes + 1 second
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["ticketCollection"] == {"minutesBeforeEvent": 30, "way": "on_site"}

    def test_ticket_collection_no_ticket(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.NO_TICKET,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["ticketCollection"] is None


@pytest.mark.usefixtures("db_session")
class GetEventDatesTest:
    @freezegun.freeze_time("2023-01-01 12:00:00")
    def test_event_with_dates(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.StockFactory(offer=event_offer, isSoftDeleted=True)
        price_category = offers_factories.PriceCategoryFactory(
            offer=event_offer, price=12.34, priceCategoryLabel__label="carre or"
        )
        bookable_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            priceCategory=price_category,
            quantity=10,
            bookingLimitDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
            beginningDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
        )
        stock_without_booking = offers_factories.EventStockFactory(
            offer=event_offer,
            # FIXME (cepehang, 2023-02-02): remove price and None price category after price category generation script
            price=12.34,
            priceCategory=None,
            quantity=2,
            bookingLimitDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
            beginningDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
        )
        offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)  # deleted stock, not returned
        bookings_factories.BookingFactory(stock=bookable_stock)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates"
            )

        assert response.status_code == 200
        assert response.json["dates"] == [
            {
                "beginningDatetime": "2023-01-15T13:00:00Z",
                "bookedQuantity": 1,
                "bookingLimitDatetime": "2023-01-15T13:00:00Z",
                "id": bookable_stock.id,
                "priceCategory": {"id": price_category.id, "label": "carre or", "price": 1234},
                "quantity": 10,
            },
            {
                "beginningDatetime": "2023-01-15T13:00:00Z",
                "bookedQuantity": 0,
                "bookingLimitDatetime": "2023-01-15T13:00:00Z",
                "id": stock_without_booking.id,
                "priceCategory": {"id": None, "label": None, "price": 1234},
                "quantity": 2,
            },
        ]
        assert (
            response.json["pagination"]["pagesLinks"]["current"]
            == f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50"
        )

    def test_event_without_dates(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)  # deleted stock, not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates"
            )

        assert response.status_code == 200
        assert response.json == {
            "dates": [],
            "pagination": {
                "currentPage": 1,
                "itemsCount": 0,
                "itemsTotal": 0,
                "lastPage": 1,
                "limitPerPage": 50,
                "pagesLinks": {
                    "current": f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50",
                    "first": f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50",
                    "last": f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50",
                    "next": None,
                    "previous": None,
                },
            },
        }

    def test_404_when_page_is_too_high(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.EventStockFactory(offer=event_offer)  # deleted stock, not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates?page=2&limit=50"
            )

        assert response.status_code == 404
        assert response.json == {
            "page": "The page you requested does not exist. The maximum page for the specified limit is 1"
        }


@pytest.mark.usefixtures("db_session")
class GetProductsTest:
    ENDPOINT_URL = "http://localhost/public/offers/v1/products"

    def test_get_first_page(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue=venue)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5"
            )

        assert response.status_code == 200
        assert response.json["pagination"] == {
            "currentPage": 1,
            "itemsCount": 5,
            "itemsTotal": 12,
            "lastPage": 3,
            "limitPerPage": 5,
            "pagesLinks": {
                "current": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                "first": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                "last": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=3&limit=5",
                "next": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=2&limit=5",
                "previous": None,
            },
        }
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[0:5]]

    def test_get_last_page(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue=venue)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5&page=3"
            )

        assert response.status_code == 200
        assert response.json["pagination"] == {
            "currentPage": 3,
            "itemsCount": 2,
            "itemsTotal": 12,
            "lastPage": 3,
            "limitPerPage": 5,
            "pagesLinks": {
                "current": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=3&limit=5",
                "first": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                "last": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=3&limit=5",
                "next": None,
                "previous": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=2&limit=5",
            },
        }
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[10:12]]

    def test_404_when_the_page_is_too_high(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5&page=2"
            )
        assert response.status_code == 404
        assert response.json == {
            "page": "The page you requested does not exist. The maximum page for the " "specified limit is 1"
        }

    def test_200_for_first_page_if_no_items(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5"
            )

        assert response.status_code == 200
        assert response.json == {
            "pagination": {
                "currentPage": 1,
                "itemsCount": 0,
                "itemsTotal": 0,
                "limitPerPage": 5,
                "lastPage": 1,
                "pagesLinks": {
                    "current": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                    "first": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                    "last": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                    "next": None,
                    "previous": None,
                },
            },
            "products": [],
        }

    def test_400_when_limit_is_too_high(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=51"
            )

        assert response.status_code == 400
        assert response.json == {"limit": ["ensure this value is less than or equal to 50"]}

    def test_get_filtered_venue_offer(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.ThingOfferFactory(
            venue__managingOfferer=venue.managingOfferer
        )  # offer attached to other venue

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}"
            )

        assert response.status_code == 200
        assert response.json["pagination"] == {
            "currentPage": 1,
            "itemsCount": 1,
            "itemsTotal": 1,
            "lastPage": 1,
            "limitPerPage": 50,
            "pagesLinks": {
                "current": f"http://localhost/public/offers/v1/products?venueId={venue.id}&page=1&limit=50",
                "first": f"http://localhost/public/offers/v1/products?venueId={venue.id}&page=1&limit=50",
                "last": f"http://localhost/public/offers/v1/products?venueId={venue.id}&page=1&limit=50",
                "next": None,
                "previous": None,
            },
        }
        assert [product["id"] for product in response.json["products"]] == [offer.id]

    def test_404_when_venue_id_not_tied_to_api_key(self, client):
        offerers_factories.ApiKeyFactory()
        unrelated_venue = offerers_factories.VenueFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products?venueId={unrelated_venue.id}"
        )

        assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
class GetEventsTest:
    ENDPOINT_URL = "http://localhost/public/offers/v1/events"

    def test_get_first_page(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers = offers_factories.EventOfferFactory.create_batch(12, venue=venue)
        offers_factories.ThingOfferFactory.create_batch(3, venue=venue)  # not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events?limit=5&venueId={venue.id}"
            )

        assert response.status_code == 200
        assert response.json["pagination"] == {
            "currentPage": 1,
            "itemsCount": 5,
            "itemsTotal": 12,
            "lastPage": 3,
            "limitPerPage": 5,
            "pagesLinks": {
                "current": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                "first": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                "last": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=3&limit=5",
                "next": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=2&limit=5",
                "previous": None,
            },
        }
        assert [event["id"] for event in response.json["events"]] == [offer.id for offer in offers[0:5]]

    def test_404_when_venue_id_not_tied_to_api_key(self, client):
        offerers_factories.ApiKeyFactory()
        unrelated_venue = offerers_factories.VenueFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events?venueId={unrelated_venue.id}"
        )

        assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
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


@pytest.mark.usefixtures("db_session")
class DeleteDateTest:
    def test_delete_date(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        to_delete_stock = offers_factories.EventStockFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{event_offer.id}/dates/{to_delete_stock.id}",
        )

        assert response.status_code == 204
        assert response.json is None
        assert to_delete_stock.isSoftDeleted is True

    def test_404_if_already_soft_deleted(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        already_deleted_stock = offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{event_offer.id}/dates/{already_deleted_stock.id}",
        )

        assert response.status_code == 404
        assert response.json == {"date_id": ["The date could not be found"]}

    def test_404_if_others_offerer_offer(self, client):
        offerers_factories.ApiKeyFactory()
        others_stock = offers_factories.EventStockFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{others_stock.offerId}/dates/{others_stock.id}",
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}


@pytest.mark.usefixtures("db_session")
class PatchEventTest:
    def test_edit_product_offer_returns_404(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        thing_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer, isActive=True, lastProvider=api_key.provider
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{thing_offer.id}",
            json={"isActive": False},
        )

        assert response.status_code == 404
        assert thing_offer.isActive is True

    def test_deactivate_offer(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, isActive=True, lastProvider=api_key.provider)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={"isActive": False},
        )

        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert event_offer.isActive is False

    def test_sets_field_to_none_and_leaves_other_unchanged(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId="CONCERT",
            venue=venue,
            withdrawalDetails="Des conditions de retrait sur la sellette",
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=86400,
            bookingContact="contact@example.com",
            bookingEmail="notify@example.com",
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={"itemCollectionDetails": None},
        )

        assert response.status_code == 200
        assert response.json["itemCollectionDetails"] is None
        assert event_offer.withdrawalDetails is None
        assert event_offer.bookingEmail == "notify@example.com"
        assert event_offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL
        assert event_offer.withdrawalDelay == 86400

    def test_sets_accessibility_partially(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={"accessibility": {"audioDisabilityCompliant": False}},
        )

        assert response.status_code == 200
        assert response.json["accessibility"] == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }
        assert event_offer.audioDisabilityCompliant is False
        assert event_offer.mentalDisabilityCompliant is True
        assert event_offer.motorDisabilityCompliant is True
        assert event_offer.visualDisabilityCompliant is True

    def test_update_extra_data_partially(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            subcategoryId="FESTIVAL_ART_VISUEL",
            extraData={
                "author": "Maurice",
                "stageDirector": "Robert",
                "performer": "Pink Pâtisserie",
            },
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={
                "categoryRelatedFields": {
                    "category": "FESTIVAL_ART_VISUEL",
                    "author": "Maurice",
                    "stageDirector": "Robert",
                    "performer": "Pink Pâtisserie",
                }
            },
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": "Maurice",
            "category": "FESTIVAL_ART_VISUEL",
            "performer": "Pink Pâtisserie",
        }
        assert event_offer.extraData == {
            "author": "Maurice",
            "performer": "Pink Pâtisserie",
            "stageDirector": "Robert",
        }

    def test_patch_all_fields(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            bookingContact="contact@example.com",
            bookingEmail="notify@passq.com",
            subcategoryId="CONCERT",
            durationMinutes=20,
            isDuo=False,
            lastProvider=api_key.provider,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=86400,
            withdrawalDetails="Around there",
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={
                "ticketCollection": {"way": "on_site", "minutesBeforeEvent": 60},
                "bookingContact": "test@myemail.com",
                "bookingEmail": "test@myemail.com",
                "eventDuration": 40,
                "enableDoubleBookings": "true",
                "itemCollectionDetails": "Here !",
            },
        )
        assert response.status_code == 200
        assert event_offer.withdrawalType == offers_models.WithdrawalTypeEnum.ON_SITE
        assert event_offer.withdrawalDelay == 3600
        assert event_offer.durationMinutes == 40
        assert event_offer.isDuo is True
        assert event_offer.bookingContact == "test@myemail.com"
        assert event_offer.bookingEmail == "test@myemail.com"
        assert event_offer.withdrawalDetails == "Here !"


@pytest.mark.usefixtures("db_session")
class PatchDateTest:
    def test_find_no_stock_returns_404(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/dates/12",
            json={"beginningDatetime": "2022-02-01T12:00:00+02:00"},
        )
        assert response.status_code == 404
        assert response.json == {"date_id": ["No date could be found"]}

    def test_find_no_price_category_returns_404(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        event_stock = offers_factories.EventStockFactory(offer=event_offer, priceCategory=None)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/dates/{event_stock.id}",
            json={"priceCategoryId": 0},
        )

        assert response.status_code == 404

    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_update_all_fields_on_date_with_price(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=10,
            price=12,
            priceCategory=None,
            bookingLimitDatetime=datetime.datetime(2022, 1, 7),
            beginningDatetime=datetime.datetime(2022, 1, 12),
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "beginningDatetime": "2022-02-01T15:00:00+02:00",
                "bookingLimitDatetime": "2022-01-20T12:00:00+02:00",
                "priceCategoryId": price_category.id,
                "quantity": 24,
            },
        )
        assert response.status_code == 200
        assert event_stock.bookingLimitDatetime == datetime.datetime(2022, 1, 20, 10)
        assert event_stock.beginningDatetime == datetime.datetime(2022, 2, 1, 13)
        assert event_stock.price == price_category.price
        assert event_stock.priceCategory == price_category
        assert event_stock.quantity == 24

    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_update_all_fields_on_date_with_price_category(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)

        old_price_category = offers_factories.PriceCategoryFactory(offer=event_offer)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=10,
            priceCategory=old_price_category,
            bookingLimitDatetime=datetime.datetime(2022, 1, 7),
            beginningDatetime=datetime.datetime(2022, 1, 12),
        )
        new_price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "beginningDatetime": "2022-02-01T15:00:00+02:00",
                "bookingLimitDatetime": "2022-01-20T12:00:00+02:00",
                "priceCategoryId": new_price_category.id,
                "quantity": 24,
            },
        )

        assert response.status_code == 200
        assert event_stock.bookingLimitDatetime == datetime.datetime(2022, 1, 20, 10)
        assert event_stock.beginningDatetime == datetime.datetime(2022, 2, 1, 13)
        assert event_stock.price == new_price_category.price
        assert event_stock.priceCategory == new_price_category
        assert event_stock.quantity == 24

    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_update_only_one_field(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=10,
            priceCategory=price_category,
            bookingLimitDatetime=datetime.datetime(2022, 1, 7),
            beginningDatetime=datetime.datetime(2022, 1, 12),
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "bookingLimitDatetime": "2022-01-09T12:00:00+02:00",
            },
        )

        assert response.status_code == 200
        assert event_stock.bookingLimitDatetime == datetime.datetime(2022, 1, 9, 10)
        assert event_stock.beginningDatetime == datetime.datetime(2022, 1, 12)
        assert event_stock.price == price_category.price
        assert event_stock.quantity == 10
        assert event_stock.priceCategory == price_category

    def test_update_with_error(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()

        event_stock = offers_factories.EventStockFactory(
            offer__venue=venue,
            offer__lastProvider=api_key.provider,
            quantity=10,
            dnBookedQuantity=8,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "quantity": 3,
            },
        )
        assert response.status_code == 400
        assert response.json == {"quantity": ["Le stock total ne peut être inférieur au nombre de réservations"]}

    def test_does_not_accept_extra_fields(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_stock = offers_factories.EventStockFactory(
            offer__venue__managingOfferer=api_key.offerer,
            offer__lastProvider=api_key.provider,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "testForbidField": "test",
            },
        )
        assert response.status_code == 400
        assert response.json == {"testForbidField": ["Vous ne pouvez pas changer cette information"]}


@pytest.mark.usefixtures("db_session")
class PatchPriceCategoryTest:
    def test_find_no_offer_returns_404(self, client):
        offerers_factories.ApiKeyFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/events/inexistent_event_id/price_categories/inexistent_price_category_id",
            json={"price": 2500, "label": "carre or"},
        )
        assert response.status_code == 404

    def test_update_price_category(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/price_categories/{price_category.id}",
            json={"price": 2500, "label": "carre or"},
        )
        assert response.status_code == 200

        assert price_category.price == decimal.Decimal("25")
        assert price_category.label == "carre or"

    def test_update_only_one_field(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)

        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/price_categories/{price_category.id}",
            json={"price": 2500},
        )
        assert response.status_code == 200

        assert price_category.price == decimal.Decimal("25")

    def test_update_with_error(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/price_categories/{price_category.id}",
            json={"price": -1},
        )
        assert response.status_code == 400

    def test_does_not_accept_extra_fields(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/price_categories/{price_category.id}",
            json={"price": 2500, "label": "carre or", "unrecognized_key": True},
        )
        assert response.status_code == 400
        assert response.json == {"unrecognized_key": ["Vous ne pouvez pas changer cette information"]}

    def test_stock_price_update(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="Already exists", venue=offer.venue),
        )
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_category)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_category)
        expired_stock = offers_factories.EventStockFactory(
            offer=offer,
            priceCategory=price_category,
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=-2),
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{offer.id}/price_categories/{price_category.id}",
            json={"price": 25},
        )

        assert response.status_code == 200
        assert all((stock.price == decimal.Decimal("0.25") for stock in offer.stocks if not stock.isEventExpired))
        assert expired_stock.price != decimal.Decimal("0.25")
