import datetime
import decimal

import pytest
import time_machine

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils import date as date_utils

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class PostEventStocksTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{offer_id}/dates"
    endpoint_method = "post"
    default_path_params = {"offer_id": 1}

    @staticmethod
    def _get_base_date_dict(price_category_id: int, id_at_provider: str | None = None) -> dict:
        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")
        return {
            "beginningDatetime": next_month_in_non_utc_tz.isoformat(),
            "bookingLimitDatetime": date_utils.format_into_utc_date(next_week),
            "price_category_id": price_category_id,
            "quantity": 10,
            "id_at_provider": id_at_provider,
        }

    def setup_base_resource(
        self,
        venue=None,
        provider=None,
        publication_datetime=None,
        booking_allowed_datetime=None,
    ) -> tuple[offers_models.Offer, offers_models.PriceCategory]:
        additional_offer_params = {}

        if publication_datetime:
            additional_offer_params["publicationDatetime"] = publication_datetime
        if booking_allowed_datetime:
            additional_offer_params["bookingAllowedDatetime"] = booking_allowed_datetime

        offer = offers_factories.EventOfferFactory(
            venue=venue or self.setup_venue(),
            lastProvider=provider,
            **additional_offer_params,
        )
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
            price=decimal.Decimal("88.99"),
            priceCategoryLabel__label="carre or",
            priceCategoryLabel__venue=offer.venue,
        )

        return offer, price_category

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        offer, category = self.setup_base_resource()
        payload = {"dates": [self._get_base_date_dict(category.id)]}
        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        offer, category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        payload = {"dates": [self._get_base_date_dict(category.id)]}
        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 404

    def test_new_dates_are_added(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer, carre_or_price_category = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        free_price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
            price=decimal.Decimal("0"),
            priceCategoryLabel__label="gratuit",
            priceCategoryLabel__venue=venue_provider.venue,
        )

        next_week = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=1)
        next_month = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=30)
        next_month_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(next_month, "973")
        two_months_from_now = next_month + datetime.timedelta(days=30)
        two_months_from_now_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(two_months_from_now, "972")

        payload = {
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
        }
        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200
        created_stocks = db.session.query(offers_models.Stock).filter(offers_models.Stock.offerId == offer.id).all()
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

    def test_should_raise_404_because_of_invalid_offer_id(self):
        plain_api_key, _ = self.setup_provider()

        payload = {"dates": [self._get_base_date_dict(1)]}
        response = self.make_request(plain_api_key, {"offer_id": "gouzi_gouzi"}, json_body=payload)

        assert response.status_code == 404

    def test_should_raise_404_because_of_product_offer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = offers_factories.ThingOfferFactory(venue=venue_provider.venue)

        payload = {"dates": [self._get_base_date_dict(1)]}
        response = self.make_request(plain_api_key, {"offer_id": product.id}, json_body=payload)

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    @time_machine.travel(datetime.datetime(2025, 6, 27), tick=False)
    @pytest.mark.parametrize(
        "partial_dates,expected_response_json",
        [
            # errors on datetimes
            (
                [{"beginningDatetime": "1999-01-01T15:59:59+04:00"}],
                {"dates.0.beginningDatetime": ["The datetime must be in the future."]},
            ),
            (
                [{}, {"bookingLimitDatetime": "1999-01-01T15:59:59+04:00"}],
                {"dates.1.bookingLimitDatetime": ["The datetime must be in the future."]},
            ),
            (
                [{"beginningDatetime": "2025-06-28T15:59:00"}],
                {"dates.0.beginningDatetime": ["The datetime must be timezone-aware."]},
            ),
            (
                [{}, {"bookingLimitDatetime": "2025-06-28T15:59:00"}],
                {"dates.1.bookingLimitDatetime": ["The datetime must be timezone-aware."]},
            ),
            (
                [
                    {"bookingLimitDatetime": "2025-06-28T15:59:00+02:00"},
                    {"bookingLimitDatetime": "2025-07-03T12:59:00+02:00"},
                ],
                {
                    "dates.0.bookingLimitDatetime": [
                        "the stock will not be published before its `bookingLimitDatetime`. Either change `bookingLimitDatetime` to a later date, or update the offer `publicationDatetime`",
                        "the stock will not be bookable before its `bookingLimitDatetime`. Either change `bookingLimitDatetime` to a later date, or update the offer `bookingAllowedDatetime`",
                    ],
                    "dates.1.bookingLimitDatetime": [
                        "the stock will not be bookable before its `bookingLimitDatetime`. Either change `bookingLimitDatetime` to a later date, or update the offer `bookingAllowedDatetime`",
                    ],
                },
            ),
            # errors on price category
            (
                [{}, {"priceCategoryId": 234445453}],
                {"dates.1.priceCategoryId": ["The price category could not be found"]},
            ),
            # errors because too many items
            (
                [{} for a in range(0, offers_models.Offer.MAX_STOCKS_PER_OFFER + 1)],
                {"dates": ["ensure this value has at most 2500 items"]},
            ),
            (  # should raise because offer has already one stock
                [{} for a in range(0, offers_models.Offer.MAX_STOCKS_PER_OFFER)],
                {
                    "dates": [
                        f"The maximum number of stock entries allowed per offer is {offers_models.Offer.MAX_STOCKS_PER_OFFER}"
                    ]
                },
            ),
            # errors on idAtProvider
            (
                [{"idAtProvider": "c'est déjà pris :'("}],
                {"dates.0.idAtProvider": ["`c'est déjà pris :'(` is already taken by another offer stock"]},
            ),
            (
                [{"idAtProvider": "a" * 71}],
                {"dates.0.idAtProvider": ["ensure this value has at most 70 characters"]},
            ),
        ],
    )
    def test_should_raise_400(self, partial_dates, expected_response_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer, price_category = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            publication_datetime=datetime.datetime(2025, 7, 2),
            booking_allowed_datetime=datetime.datetime(2025, 7, 4),
        )
        existing_stock = offers_factories.StockFactory(offer=offer, idAtProviders="c'est déjà pris :'(")
        dates = []

        for partial_date in partial_dates:
            date_dict = self._get_base_date_dict(price_category_id=price_category.id)
            date_dict.update(**partial_date)
            dates.append(date_dict)

        response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body={"dates": dates})

        assert response.status_code == 400
        assert response.json == expected_response_json

        assert db.session.query(offers_models.Stock).filter(offers_models.Stock.id != existing_stock.id).count() == 0
