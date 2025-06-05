import dataclasses
import datetime
import decimal
import logging
from unittest import mock

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.mails.transactional import sendinblue_template_ids
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils import date as date_utils

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class PatchEventStockTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}/dates/{stock_id}"
    endpoint_method = "patch"
    default_path_params = {"event_id": 1, "stock_id": 2}

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
    def test_update_all_fields_on_date_with_price(self, mocked_async_index_offer_ids, client, caplog):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event)

        one_week_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        twenty_four_day_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(
            days=24
        )
        with caplog.at_level(logging.INFO):
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

        log_message = "Successfully updated stock"
        log = next(record for record in caplog.records if record.message == log_message)

        assert log.extra["provider_id"]

        changes = log.extra["changes"]

        assert changes["priceCategory"]["old_value"] != changes["priceCategory"]["new_value"]
        assert changes["priceCategory"]["new_value"].id == price_category.id

        assert changes["idAtProviders"]["old_value"] != changes["idAtProviders"]["new_value"]
        assert changes["idAtProviders"]["new_value"] == "hey you !"

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
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = offers_factories.EventOfferFactory(venue=venue_provider.venue, lastProvider=venue_provider.provider)
        now = datetime.datetime.utcnow()
        tomorrow = now + datetime.timedelta(days=1)
        two_days_after = now + datetime.timedelta(days=2)
        three_days_after = now + datetime.timedelta(days=3)

        old_price_category = offers_factories.PriceCategoryFactory(offer=event)
        stock = offers_factories.EventStockFactory(
            offer=event,
            quantity=10,
            priceCategory=old_price_category,
            bookingLimitDatetime=now,
            beginningDatetime=tomorrow,
        )
        new_price_category = offers_factories.PriceCategoryFactory(offer=event)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={
                "bookingLimitDatetime": date_utils.format_into_utc_date(two_days_after),
                "beginningDatetime": date_utils.format_into_utc_date(three_days_after),
                "priceCategoryId": new_price_category.id,
                "quantity": 24,
            },
        )

        assert response.status_code == 200
        assert stock.bookingLimitDatetime == two_days_after
        assert stock.beginningDatetime == three_days_after
        assert stock.price == new_price_category.price
        assert stock.priceCategory == new_price_category
        assert stock.quantity == 24

    def test_update_only_one_field(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event)
        next_year = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=365)
        stock = offers_factories.EventStockFactory(
            offer=event,
            quantity=10,
            priceCategory=price_category,
            bookingLimitDatetime=next_year,
            beginningDatetime=next_year,
            idAtProviders="hoho",
        )

        eight_days_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=8)
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={
                "bookingLimitDatetime": date_utils.utc_datetime_to_department_timezone(
                    eight_days_from_now, departement_code=None
                ).isoformat(),
            },
        )

        assert response.status_code == 200, response.json
        assert stock.bookingLimitDatetime == eight_days_from_now
        assert stock.beginningDatetime == next_year
        assert stock.price == price_category.price
        assert stock.quantity == 10
        assert stock.priceCategory == price_category
        assert stock.idAtProviders == "hoho"

    def test_update_quantity(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        stock = offers_factories.EventStockFactory(
            offer__venue=venue_provider.venue,
            offer__lastProvider=venue_provider.provider,
            quantity=10,
            dnBookedQuantity=8,
        )
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={"quantity": 3},
        )
        assert response.status_code == 200
        assert stock.quantity == 11

    def test_update_quantity_to_zero_deletes_the_existing_stock(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        stock = offers_factories.EventStockFactory(
            offer__venue=venue_provider.venue, offer__lastProvider=venue_provider.provider, quantity=10
        )

        url = self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id)
        response = client.with_explicit_token(plain_api_key).patch(url, json={"quantity": 0})
        assert response.status_code == 204

        db.session.refresh(stock)
        assert stock.isSoftDeleted

    def test_update_stock_with_existing_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event)
        stock = offers_factories.EventStockFactory(
            offer=event,
            quantity=2,
            priceCategory=price_category,
        )
        bookings_factories.BookingFactory(stock=stock, quantity=2)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={"quantity": 10},
        )

        assert response.status_code == 200
        assert stock.price == price_category.price
        assert stock.quantity == 12
        assert stock.priceCategory == price_category

    def test_update_stock_quantity_0_with_existing_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event)
        stock = offers_factories.EventStockFactory(
            offer=event,
            quantity=20,
            priceCategory=price_category,
        )
        bookings_factories.BookingFactory(stock=stock)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={"quantity": 0},
        )

        assert response.status_code == 200
        assert stock.price == price_category.price
        assert stock.quantity == 1
        assert stock.priceCategory == price_category

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_no_update(self, mocked_async_index_offer_ids, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=event)
        stock = offers_factories.EventStockFactory(
            offer=event,
            quantity=20,
            priceCategory=price_category,
        )

        client = client.with_explicit_token(plain_api_key)
        response = client.patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={"quantity": stock.quantity},  # unchanged
        )

        assert response.status_code == 200
        assert stock.quantity == 20
        mocked_async_index_offer_ids.assert_not_called()

    def test_should_raise_400_because_of_extra_fields(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        stock = offers_factories.EventStockFactory(
            offer__venue=venue_provider.venue,
            offer__lastProvider=venue_provider.provider,
        )
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={"testForbidField": "test"},
        )
        assert response.status_code == 400
        assert response.json == {"testForbidField": ["extra fields not permitted"]}

    def test_should_return_400_because_booking_limit_datetime_is_after_beginning_datetime(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
        )
        # dates
        two_weeks_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=2)
        one_hour_later = two_weeks_from_now + datetime.timedelta(hours=1)

        # event stock 2 weeks from now
        stock = offers_factories.EventStockFactory(
            offer=event,
            quantity=10,
            price=12,
            priceCategory=None,
            bookingLimitDatetime=two_weeks_from_now,
            beginningDatetime=two_weeks_from_now,
        )

        # tries to set `bookingLimitDatetime` to next month
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={
                "bookingLimitDatetime": date_utils.utc_datetime_to_department_timezone(
                    one_hour_later, departement_code=venue_provider.venue.departementCode
                ).isoformat()
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "The bookingLimitDatetime must be before the beginning of the event",
            ],
        }

    @pytest.mark.parametrize("date_field", ["bookingLimitDatetime", "beginningDatetime"])
    def test_should_return_400_because_new_date_is_in_the_past(self, client, date_field):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        now = datetime.datetime.now()
        new_date = now - datetime.timedelta(days=2)

        stock = offers_factories.EventStockFactory(
            offer__venue=venue_provider.venue, offer__lastProvider=venue_provider.provider
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={date_field: date_utils.format_into_utc_date(new_date)},
        )

        assert response.status_code == 400
        assert response.json == {date_field: ["The datetime must be in the future."]}

    def test_should_raise_400_because_stock_idAtProvider_already_taken(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        duplicate_id_at_provider = "ouille ouille ouille"
        offers_factories.StockFactory(offer=event, idAtProviders=duplicate_id_at_provider)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={"idAtProvider": duplicate_id_at_provider},
        )

        assert response.status_code == 400
        assert response.json == {
            "idAtProvider": [
                "`ouille ouille ouille` is already taken by another offer stock",
            ],
        }

    def test_find_no_stock_returns_404(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
        )

        new_beginning = datetime.datetime.now() + datetime.timedelta(minutes=1)
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event.id, stock_id="12"),
            json={"beginningDatetime": date_utils.format_into_utc_date(new_beginning)},
        )
        assert response.status_code == 404
        assert response.json == {"stock_id": ["No stock could be found"]}

    def test_find_no_price_category_returns_404(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        stock = offers_factories.EventStockFactory(
            offer__venue=venue_provider.venue,
            offer__lastProvider=venue_provider.provider,
            priceCategory=None,
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=stock.offerId, stock_id=stock.id),
            json={"priceCategoryId": 0},
        )

        assert response.status_code == 404

    def test_patch_date_with_the_same_date_should_not_trigger_any_notification(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        event = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
        )

        price_category = offers_factories.PriceCategoryFactory(offer=event)

        start = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)
        stock = offers_factories.EventStockFactory(
            offer=event,
            priceCategory=price_category,
            bookingLimitDatetime=start - datetime.timedelta(days=5),
            beginningDatetime=start,
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id),
            json={"beginningDatetime": start.isoformat()},
        )

        assert response.status_code == 200

        parsed_date = datetime.datetime.fromisoformat(response.json["beginningDatetime"])

        assert parsed_date.tzinfo == datetime.timezone.utc
        assert parsed_date.date() == start.date()

        db.session.refresh(stock)
        assert stock.beginningDatetime == start.replace(tzinfo=None)
