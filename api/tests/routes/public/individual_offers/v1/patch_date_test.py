import dataclasses
import datetime
from unittest import mock

import pytest

from pcapi.core.bookings import factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional import sendinblue_template_ids
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import date as date_utils

from . import utils


@pytest.mark.usefixtures("db_session")
class PatchDateTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_update_all_fields_on_date_with_price(self, mocked_async_index_offer_ids, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        next_year = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=365)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=10,
            price=12,
            priceCategory=None,
            bookingLimitDatetime=next_year,
            beginningDatetime=next_year,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        two_weeks_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=2)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "beginningDatetime": date_utils.utc_datetime_to_department_timezone(next_month, None).isoformat(),
                "bookingLimitDatetime": date_utils.utc_datetime_to_department_timezone(
                    two_weeks_from_now, departement_code=None
                ).isoformat(),
                "priceCategoryId": price_category.id,
                "quantity": 24,
                "id_at_provider": "hey you !",
            },
        )

        assert response.status_code == 200, response.json
        assert event_stock.bookingLimitDatetime == two_weeks_from_now
        assert event_stock.beginningDatetime == next_month
        assert event_stock.price == price_category.price
        assert event_stock.priceCategory == price_category
        assert event_stock.quantity == 24
        assert event_stock.idAtProviders == "hey you !"
        mocked_async_index_offer_ids.assert_called_once()

    def test_sends_email_if_beginning_date_changes_on_edition(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue(venue_params={"bookingEmail": "venue@email.com"})
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        now = datetime.datetime.utcnow()
        tomorrow = now + datetime.timedelta(days=1)
        two_days_after = now + datetime.timedelta(days=2)
        three_days_after = now + datetime.timedelta(days=3)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=10,
            price=12,
            priceCategory=None,
            bookingLimitDatetime=tomorrow,
            beginningDatetime=two_days_after,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)
        bookings_factories.BookingFactory(stock=event_stock, user__email="benefeciary@email.com")

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "bookingLimitDatetime": date_utils.format_into_utc_date(two_days_after),
                "beginningDatetime": date_utils.format_into_utc_date(three_days_after),
                "priceCategoryId": price_category.id,
                "quantity": 24,
            },
        )

        assert response.status_code == 200
        assert event_stock.bookingLimitDatetime == two_days_after
        assert event_stock.beginningDatetime == three_days_after
        assert event_stock.price == price_category.price
        assert event_stock.priceCategory == price_category
        assert event_stock.quantity == 25
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            sendinblue_template_ids.TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value
        )
        assert mails_testing.outbox[0]["To"] == "venue@email.com"
        assert mails_testing.outbox[1]["template"] == dataclasses.asdict(
            sendinblue_template_ids.TransactionalEmail.BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[1]["To"] == "benefeciary@email.com"

    def test_update_all_fields_on_date_with_price_category(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        now = datetime.datetime.utcnow()
        tomorrow = now + datetime.timedelta(days=1)
        two_days_after = now + datetime.timedelta(days=2)
        three_days_after = now + datetime.timedelta(days=3)

        old_price_category = offers_factories.PriceCategoryFactory(offer=event_offer)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=10,
            priceCategory=old_price_category,
            bookingLimitDatetime=now,
            beginningDatetime=tomorrow,
        )
        new_price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "bookingLimitDatetime": date_utils.format_into_utc_date(two_days_after),
                "beginningDatetime": date_utils.format_into_utc_date(three_days_after),
                "priceCategoryId": new_price_category.id,
                "quantity": 24,
            },
        )

        assert response.status_code == 200
        assert event_stock.bookingLimitDatetime == two_days_after
        assert event_stock.beginningDatetime == three_days_after
        assert event_stock.price == new_price_category.price
        assert event_stock.priceCategory == new_price_category
        assert event_stock.quantity == 24

    def test_update_only_one_field(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)
        next_year = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=365)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=10,
            priceCategory=price_category,
            bookingLimitDatetime=next_year,
            beginningDatetime=next_year,
            idAtProviders="hoho",
        )

        eight_days_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=8)
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "bookingLimitDatetime": date_utils.utc_datetime_to_department_timezone(
                    eight_days_from_now, departement_code=None
                ).isoformat(),
            },
        )

        assert response.status_code == 200, response.json
        assert event_stock.bookingLimitDatetime == eight_days_from_now
        assert event_stock.beginningDatetime == next_year
        assert event_stock.price == price_category.price
        assert event_stock.quantity == 10
        assert event_stock.priceCategory == price_category
        assert event_stock.idAtProviders == "hoho"

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

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_no_update(self, mocked_async_index_offer_ids, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)
        stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=20,
            priceCategory=price_category,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        response = client.patch(
            f"/public/offers/v1/events/{stock.offerId}/dates/{stock.id}",
            json={"quantity": stock.quantity},  # unchanged
        )

        assert response.status_code == 200
        assert stock.quantity == 20
        mocked_async_index_offer_ids.assert_not_called()


@pytest.mark.usefixtures("db_session")
class PatchDateReturns400Test:
    def test_should_return_400_because_booking_limit_datetime_is_after_beginning_datetime(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        # dates
        two_weeks_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=2)
        one_hour_later = two_weeks_from_now + datetime.timedelta(hours=1)

        # event stock 2 weeks from now
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            quantity=10,
            price=12,
            priceCategory=None,
            bookingLimitDatetime=two_weeks_from_now,
            beginningDatetime=two_weeks_from_now,
        )

        # tries to set `bookingLimitDatetime` to next month
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "bookingLimitDatetime": date_utils.utc_datetime_to_department_timezone(
                    one_hour_later, departement_code=venue.departementCode
                ).isoformat()
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "The bookingLimitDatetime must be before the beginning of the event",
            ],
        }


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
        assert response.json == {"stock_id": ["No stock could be found"]}

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
