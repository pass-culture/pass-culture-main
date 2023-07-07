import datetime
import decimal

import freezegun
import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models

from . import utils


@pytest.mark.usefixtures("db_session")
class PostDatesTest:
    @freezegun.freeze_time("2022-01-01 10:00:00")
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

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": "2022-02-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "price_category_id": carre_or_price_category.id,
                        "quantity": 10,
                    },
                    {
                        "beginningDatetime": "2022-03-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "price_category_id": free_price_category.id,
                        "quantity": "unlimited",
                    },
                ],
            },
        )

        assert response.status_code == 200
        created_stocks = offers_models.Stock.query.filter(offers_models.Stock.offerId == event_offer.id).all()
        assert len(created_stocks) == 2
        first_stock = next(
            stock for stock in created_stocks if stock.beginningDatetime == datetime.datetime(2022, 2, 1, 10, 0, 0)
        )
        assert first_stock.price == decimal.Decimal("88.99")
        assert first_stock.quantity == 10
        second_stock = next(
            stock for stock in created_stocks if stock.beginningDatetime == datetime.datetime(2022, 3, 1, 10, 0, 0)
        )
        assert second_stock.price == decimal.Decimal("0")
        assert second_stock.quantity is None

        assert response.json == {
            "dates": [
                {
                    "beginningDatetime": "2022-02-01T10:00:00",
                    "bookedQuantity": 0,
                    "bookingLimitDatetime": "2022-01-15T13:00:00",
                    "id": first_stock.id,
                    "priceCategory": {
                        "id": first_stock.priceCategoryId,
                        "label": first_stock.priceCategory.label,
                        "price": 8899,
                    },
                    "quantity": 10,
                },
                {
                    "beginningDatetime": "2022-03-01T10:00:00",
                    "bookedQuantity": 0,
                    "bookingLimitDatetime": "2022-01-15T13:00:00",
                    "id": second_stock.id,
                    "priceCategory": {
                        "id": second_stock.priceCategoryId,
                        "label": second_stock.priceCategory.label,
                        "price": 0,
                    },
                    "quantity": "unlimited",
                },
            ],
        }

    @freezegun.freeze_time("2022-01-01 10:00:00")
    def test_invalid_offer_id(self, client):
        utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events/quinze/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": "2022-02-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "priceCategoryId": 0,
                        "quantity": 10,
                    }
                ]
            },
        )

        assert response.status_code == 404

    @freezegun.freeze_time("2022-01-01 10:00:00")
    def test_404_price_category_id(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": "2022-02-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "priceCategoryId": 0,
                        "quantity": 10,
                    }
                ]
            },
        )

        assert response.status_code == 404

    @freezegun.freeze_time("2022-01-01 10:00:00")
    def test_404_for_other_offerer_offer(self, client):
        utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": "2022-02-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "priceCategoryId": 0,
                        "quantity": 10,
                    },
                ],
            },
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    @freezegun.freeze_time("2022-01-01 10:00:00")
    def test_404_for_product_offer(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{product_offer.id}/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": "2022-02-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "priceCategoryId": 0,
                        "quantity": 10,
                    },
                ],
            },
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_400_for_dates_in_past(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{product_offer.id}/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": "2022-01-01T15:59:59+04:00",
                        "bookingLimitDatetime": "2022-01-01T10:59:59-01:00",
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
