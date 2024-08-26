import datetime
import decimal

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.utils import date as date_utils

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper

from . import utils


@pytest.mark.usefixtures("db_session")
class PostEventStocksTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}/dates"
    endpoint_method = "post"
    default_path_params = {"event_id": 1}

    @staticmethod
    def _get_base_payload(price_category_id) -> dict:
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
                    "id_at_provider": "id_143556",
                }
            ]
        }

    def setup_base_resource(self, venue=None, provider=None) -> tuple[offers_models.Offer, offers_models.PriceCategory]:
        event = offers_factories.EventOfferFactory(venue=venue or self.setup_venue(), lastProvider=provider)
        category_label = offers_factories.PriceCategoryLabelFactory(label="carre or", venue=event.venue)
        price_category = offers_factories.PriceCategoryFactory(
            offer=event, price=decimal.Decimal("88.99"), priceCategoryLabel=category_label
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
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        carre_or_category_label = offers_factories.PriceCategoryLabelFactory(label="carre or", venue=event_offer.venue)
        carre_or_price_category = offers_factories.PriceCategoryFactory(
            offer=event_offer, price=decimal.Decimal("88.99"), priceCategoryLabel=carre_or_category_label
        )

        free_category_label = offers_factories.PriceCategoryLabelFactory(label="gratuit", venue=event_offer.venue)
        free_price_category = offers_factories.PriceCategoryFactory(
            offer=event_offer, price=decimal.Decimal("0"), priceCategoryLabel=free_category_label
        )

        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")
        two_months_from_now = next_month + datetime.timedelta(days=30)
        two_months_from_now_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(two_months_from_now, "972")
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/dates",
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
        created_stocks = offers_models.Stock.query.filter(offers_models.Stock.offerId == event_offer.id).all()
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
                        "price": 0,
                    },
                    "quantity": "unlimited",
                    "idAtProvider": None,
                },
            ],
        }

    def test_invalid_offer_id(self, client):
        utils.create_offerer_provider_linked_to_venue()

        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events/quinze/dates",
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

    def test_404_price_category_id(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )

        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/dates",
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

    def test_404_for_product_offer(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue)

        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{product_offer.id}/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": next_month_in_non_utc_tz.isoformat(),
                        "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
                        "priceCategoryId": 0,
                        "quantity": 10,
                    },
                ],
            },
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    def test_400_for_dates_in_past(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{product_offer.id}/dates",
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
