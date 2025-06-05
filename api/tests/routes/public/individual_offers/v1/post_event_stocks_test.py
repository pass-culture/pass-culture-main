import datetime
import decimal

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils import date as date_utils

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class PostEventStocksTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}/dates"
    endpoint_method = "post"
    default_path_params = {"event_id": 1}

    @staticmethod
    def _get_base_payload(price_category_id: int, id_at_provider: str | None = None) -> dict:
        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")
        return {
            "dates": [
                {
                    "beginningDatetime": next_month_in_non_utc_tz.isoformat(),
                    "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
                    "price_category_id": price_category_id,
                    "quantity": 10,
                    "id_at_provider": id_at_provider,
                }
            ]
        }

    def setup_base_resource(self, venue=None, provider=None) -> tuple[offers_models.Offer, offers_models.PriceCategory]:
        event = offers_factories.EventOfferFactory(venue=venue or self.setup_venue(), lastProvider=provider)
        price_category = offers_factories.PriceCategoryFactory(
            offer=event,
            price=decimal.Decimal("88.99"),
            priceCategoryLabel__label="carre or",
            priceCategoryLabel__venue=event.venue,
        )

        return event, price_category

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        event, category = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json=self._get_base_payload(category.id),
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event, category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json=self._get_base_payload(category.id),
        )
        assert response.status_code == 404

    def test_new_dates_are_added(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, carre_or_price_category = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        free_price_category = offers_factories.PriceCategoryFactory(
            offer=event,
            price=decimal.Decimal("0"),
            priceCategoryLabel__label="gratuit",
            priceCategoryLabel__venue=venue_provider.venue,
        )

        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")
        two_months_from_now = next_month + datetime.timedelta(days=30)
        two_months_from_now_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(two_months_from_now, "972")
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json={
                "dates": [
                    {
                        "beginningDatetime": next_month_in_non_utc_tz.isoformat(),
                        "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
                        "price_category_id": carre_or_price_category.id,
                        "quantity": 10,
                        "id_at_provider": "id_143556",
                    },
                    {
                        "beginningDatetime": two_months_from_now_in_non_utc_tz.isoformat(),
                        "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
                        "price_category_id": free_price_category.id,
                        "quantity": "unlimited",
                    },
                ],
            },
        )

        assert response.status_code == 200
        created_stocks = db.session.query(offers_models.Stock).filter(offers_models.Stock.offerId == event.id).all()
        assert len(created_stocks) == 2
        first_stock = next(stock for stock in created_stocks if stock.beginningDatetime == next_month)
        assert first_stock.price == decimal.Decimal("88.99")
        assert first_stock.quantity == 10
        assert first_stock.idAtProviders == "id_143556"
        second_stock = next(stock for stock in created_stocks if stock.beginningDatetime == two_months_from_now)
        assert second_stock.price == decimal.Decimal("0")
        assert second_stock.quantity is None
        assert second_stock.idAtProviders is None

        assert response.json == {
            "dates": [
                {
                    "beginningDatetime": date_utils.format_into_utc_date(next_month),
                    "bookedQuantity": 0,
                    "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
                    "id": first_stock.id,
                    "priceCategory": {
                        "id": first_stock.priceCategoryId,
                        "label": first_stock.priceCategory.label,
                        "idAtProvider": None,
                        "price": 8899,
                    },
                    "quantity": 10,
                    "idAtProvider": "id_143556",
                },
                {
                    "beginningDatetime": date_utils.format_into_utc_date(two_months_from_now),
                    "bookedQuantity": 0,
                    "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
                    "id": second_stock.id,
                    "priceCategory": {
                        "id": second_stock.priceCategoryId,
                        "label": second_stock.priceCategory.label,
                        "idAtProvider": None,
                        "price": 0,
                    },
                    "quantity": "unlimited",
                    "idAtProvider": None,
                },
            ],
        }

    def test_should_raise_404_because_of_invalid_offer_id(self, client):
        plain_api_key, _ = self.setup_provider()

        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id="gouzi_gouzi"),
            json={
                "dates": [
                    {
                        "beginningDatetime": next_month_in_non_utc_tz.isoformat(),
                        "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
                        "priceCategoryId": 0,
                        "quantity": 10,
                    }
                ]
            },
        )

        assert response.status_code == 404

    def test_should_raise_404_because_of_price_category_id(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, _ = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        payload_with_not_existing_category_id = self._get_base_payload(0)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json=payload_with_not_existing_category_id,
        )

        assert response.status_code == 404

    def test_should_raise_404_because_of_product_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = offers_factories.ThingOfferFactory(venue=venue_provider.venue)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=product.id), json=self._get_base_payload(0)
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    def test_should_raise_400_for_dates_in_past(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, _ = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json={
                "dates": [
                    {
                        "beginningDatetime": "1999-01-01T15:59:59+04:00",
                        "bookingLimitDatetime": "1999-01-01T10:59:59-01:00",
                        "priceCategoryId": 0,
                        "quantity": 10,
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "dates.0.beginningDatetime": ["The datetime must be in the future."],
            "dates.0.bookingLimitDatetime": ["The datetime must be in the future."],
        }

    def test_should_raise_400_because_id_at_provider_already_taken(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        duplicate_id = "aïe aïe aïe"
        offers_factories.StockFactory(offer=event, idAtProviders=duplicate_id)
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json=self._get_base_payload(price_category_id=price_category.id, id_at_provider=duplicate_id),
        )

        assert response.status_code == 400
        assert response.json == {"idAtProvider": ["`aïe aïe aïe` is already taken by another offer stock"]}

    def test_should_raise_400_because_too_many_stocks_sent(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, carre_or_price_category = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider
        )

        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json={
                "dates": [
                    {
                        "beginningDatetime": next_month_in_non_utc_tz.isoformat(),
                        "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
                        "price_category_id": carre_or_price_category.id,
                        "quantity": 10,
                        "id_at_provider": f"id_143556{a}",
                    }
                    for a in range(0, offers_models.Offer.MAX_STOCKS_PER_OFFER + 1)
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"dates": ["ensure this value has at most 2500 items"]}

    def test_should_raise_400_because_stocks_would_exceed_max_stocks_per_offer(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, carre_or_price_category = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        offers_factories.StockFactory(offer=event)

        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json={
                "dates": [
                    {
                        "beginningDatetime": next_month_in_non_utc_tz.isoformat(),
                        "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
                        "price_category_id": carre_or_price_category.id,
                        "quantity": 10,
                        "id_at_provider": f"id_143556{a}",
                    }
                    for a in range(0, offers_models.Offer.MAX_STOCKS_PER_OFFER)
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "dates": [
                f"The maximum number of stock entries allowed per offer is {offers_models.Offer.MAX_STOCKS_PER_OFFER}"
            ]
        }
