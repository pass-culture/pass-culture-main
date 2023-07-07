import datetime
import decimal

import freezegun
import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils


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
