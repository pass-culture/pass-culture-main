import dataclasses
import datetime

import freezegun
import pytest

from pcapi.core.bookings import factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional import sendinblue_template_ids
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils


@pytest.mark.usefixtures("db_session")
class PatchDateTest:
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
    def test_sends_email_if_beginning_date_changes_on_edition(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue(venue_params={"bookingEmail": "venue@email.com"})
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
        bookings_factories.BookingFactory(stock=event_stock, user__email="benefeciary@email.com")

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "beginningDatetime": "2022-02-01T15:00:00+02:00",
                "bookingLimitDatetime": "2022-01-20T12:00:00+02:00",
                "priceCategoryId": price_category.id,
                "quantity": 24,
            },
        )

        # Then
        assert response.status_code == 200
        assert event_stock.bookingLimitDatetime == datetime.datetime(2022, 1, 20, 10)
        assert event_stock.beginningDatetime == datetime.datetime(2022, 2, 1, 13)
        assert event_stock.price == price_category.price
        assert event_stock.priceCategory == price_category
        assert event_stock.quantity == 25
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            sendinblue_template_ids.TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value
        )
        assert mails_testing.outbox[0].sent_data["To"] == "venue@email.com"
        assert mails_testing.outbox[1].sent_data["template"] == dataclasses.asdict(
            sendinblue_template_ids.TransactionalEmail.BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[1].sent_data["To"] == "benefeciary@email.com"

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
        assert response.status_code == 200
        assert event_stock.quantity == 11

    def test_does_not_accept_extra_fields(self, client):
        _, api_key = utils.create_offerer_provider_linked_to_venue()
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
        assert response.json == {"testForbidField": ["extra fields not permitted"]}

    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_update_stock_with_existing_booking(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=2,
            priceCategory=price_category,
            bookingLimitDatetime=datetime.datetime(2022, 1, 7),
            beginningDatetime=datetime.datetime(2022, 1, 12),
        )
        bookings_factories.BookingFactory(stock=event_stock, quantity=2)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "quantity": 10,
            },
        )

        assert response.status_code == 200
        assert event_stock.price == price_category.price
        assert event_stock.quantity == 12
        assert event_stock.priceCategory == price_category

    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_update_stock_quantity_0_with_existing_booking(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=20,
            priceCategory=price_category,
            bookingLimitDatetime=datetime.datetime(2022, 1, 7),
            beginningDatetime=datetime.datetime(2022, 1, 12),
        )
        bookings_factories.BookingFactory(stock=event_stock)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "quantity": 0,
            },
        )

        assert response.status_code == 200
        assert event_stock.price == price_category.price
        assert event_stock.quantity == 1
        assert event_stock.priceCategory == price_category


@pytest.mark.usefixtures("db_session")
class PatchDateReturns404Test:
    def test_call_with_inactive_venue_provider_returns_404(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
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
        assert response.status_code == 404

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
