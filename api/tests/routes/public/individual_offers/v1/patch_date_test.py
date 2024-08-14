import dataclasses
import datetime
import decimal
from unittest import mock

import pytest

from pcapi.core.bookings import factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional import sendinblue_template_ids
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.utils import date as date_utils

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper

from . import utils


@pytest.mark.usefixtures("db_session")
class PatchEventStockTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}/dates/{stock_id}"

    @staticmethod
    def _get_base_payload(price_category_id) -> dict:
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        two_weeks_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=2)
        return {
            "beginningDatetime": date_utils.utc_datetime_to_department_timezone(next_month, None).isoformat(),
            "bookingLimitDatetime": date_utils.utc_datetime_to_department_timezone(
                two_weeks_from_now, departement_code=None
            ).isoformat(),
            "priceCategoryId": price_category_id,
            "quantity": 20,
            "id_at_provider": "some_id",
        }

    def setup_base_resource(self, venue=None, provider=None) -> tuple[offers_models.Offer, offers_models.Stock]:
        event = offers_factories.EventOfferFactory(venue=venue or self.setup_venue(), lastProvider=provider)
        category_label = offers_factories.PriceCategoryLabelFactory(label="carre or", venue=event.venue)
        price_category = offers_factories.PriceCategoryFactory(
            offer=event, price=decimal.Decimal("88.99"), priceCategoryLabel=category_label
        )
        next_year = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=365)
        stock = offers_factories.EventStockFactory(
            offer=event,
            quantity=10,
            price=12,
            priceCategory=price_category,
            bookingLimitDatetime=next_year,
            beginningDatetime=next_year,
        )

        return event, stock

    def test_should_raise_401_because_not_authenticated(self, client: TestClient):
        event, stock = self.setup_base_resource()
        response = client.patch(self.endpoint_url.format(event_id=event.id, stock_id=stock.id))
        assert response.status_code == 401

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        event, stock = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id),
            json=self._get_base_payload(price_category_id=stock.priceCategoryId),
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id),
            json=self._get_base_payload(price_category_id=stock.priceCategoryId),
        )
        assert response.status_code == 404

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_update_all_fields_on_date_with_price(self, mocked_async_index_offer_ids, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event)

        one_week_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        twenty_four_day_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(
            days=24
        )
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id),
            json={
                "beginningDatetime": date_utils.utc_datetime_to_department_timezone(
                    twenty_four_day_from_now, None
                ).isoformat(),
                "bookingLimitDatetime": date_utils.utc_datetime_to_department_timezone(
                    one_week_from_now, departement_code=None
                ).isoformat(),
                "priceCategoryId": price_category.id,
                "quantity": 24,
                "id_at_provider": "hey you !",
            },
        )

        assert response.status_code == 200, response.json
        assert stock.bookingLimitDatetime == one_week_from_now
        assert stock.beginningDatetime == twenty_four_day_from_now
        assert stock.price == price_category.price
        assert stock.priceCategory == price_category
        assert stock.quantity == 24
        assert stock.idAtProviders == "hey you !"
        mocked_async_index_offer_ids.assert_called_once()

    def test_sends_email_if_beginning_date_changes_on_edition(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        now = datetime.datetime.utcnow()
        two_days_after = now + datetime.timedelta(days=2)
        three_days_after = now + datetime.timedelta(days=3)

        price_category = offers_factories.PriceCategoryFactory(offer=event)
        bookings_factories.BookingFactory(stock=stock, user__email="benefeciary@email.com")

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id),
            json={
                "bookingLimitDatetime": date_utils.format_into_utc_date(two_days_after),
                "beginningDatetime": date_utils.format_into_utc_date(three_days_after),
                "priceCategoryId": price_category.id,
                "quantity": 24,
            },
        )

        assert response.status_code == 200
        assert stock.bookingLimitDatetime == two_days_after
        assert stock.beginningDatetime == three_days_after
        assert stock.price == price_category.price
        assert stock.priceCategory == price_category
        assert stock.quantity == 25
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            sendinblue_template_ids.TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value
        )
        assert mails_testing.outbox[0]["To"] == event.venue.bookingEmail
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
