import datetime
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    @patch("pcapi.core.search.async_index_offer_ids")
    def test_create_event_stocks(self, mocked_async_index_offer_ids, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        first_label = offers_factories.PriceCategoryLabelFactory(label="Tarif 1", venue=offer.venue)
        second_label = offers_factories.PriceCategoryLabelFactory(label="Tarif 2", venue=offer.venue)
        first_price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=first_label, price=20)
        second_price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=second_label, price=30)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "priceCategoryId": first_price_cat.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                },
                {
                    "priceCategoryId": first_price_cat.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                },
                {
                    "priceCategoryId": second_price_cat.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                },
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk", json=stock_data)

        assert response.status_code == 201

        assert response.json["stocks_count"] == len(stock_data["stocks"])

        created_stocks = db.session.query(offers_models.Stock).order_by(offers_models.Stock.price).all()
        assert len(created_stocks) == 3
        assert db.session.query(offers_models.PriceCategory).count() == 2
        assert db.session.query(offers_models.PriceCategoryLabel).count() == 2
        assert created_stocks[0].price == 20
        assert created_stocks[0].priceCategory.price == 20
        assert created_stocks[0].priceCategory.label == "Tarif 1"
        assert created_stocks[0].priceCategory is created_stocks[1].priceCategory
        assert created_stocks[2].price == 30
        assert created_stocks[2].priceCategory.price == 30
        assert created_stocks[2].priceCategory.label == "Tarif 2"
        assert [call.args[0] for call in mocked_async_index_offer_ids.call_args_list] == [
            [offer.id],
            [offer.id],
            [offer.id],
        ]

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_create_event_stocks_with_multi_price(self, mocked_async_index_offer_ids, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        shared_label = offers_factories.PriceCategoryLabelFactory(label="Shared", venue=offer.venue)
        first_price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=shared_label, price=20)
        unique_label = offers_factories.PriceCategoryLabelFactory(label="unique", venue=offer.venue)
        second_price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=unique_label, price=30)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        beginning_later = datetime.datetime.utcnow() + relativedelta(days=11)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "priceCategoryId": first_price_cat.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                },
                {
                    "priceCategoryId": second_price_cat.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                },
                {
                    "priceCategoryId": first_price_cat.id,
                    "beginningDatetime": format_into_utc_date(beginning_later),
                    "bookingLimitDatetime": format_into_utc_date(beginning_later),
                },
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk", json=stock_data)
        assert response.status_code == 201
        created_stocks = db.session.query(offers_models.Stock).order_by(offers_models.Stock.price).all()
        assert len(created_stocks) == 3
        assert db.session.query(offers_models.PriceCategory).count() == 2
        assert db.session.query(offers_models.PriceCategoryLabel).count() == 2
        assert created_stocks[0].price == 20
        assert created_stocks[0].priceCategory.price == 20
        assert created_stocks[0].priceCategory.label == "Shared"
        assert created_stocks[0].priceCategory is created_stocks[1].priceCategory
        assert created_stocks[2].priceCategory is second_price_cat

    def test_avoid_duplication_with_different_quantity(self, client):
        offer = offers_factories.EventOfferFactory()
        beginning = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel=price_cat_label, price=10
        )
        existing_stock = offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=format_into_utc_date(beginning),
            bookingLimitDatetime=format_into_utc_date(beginning),
            priceCategory=price_category,
            price=10,
            quantity=10,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        # First stock should be skipped
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "priceCategoryId": price_category.id,
                    "quantity": 20,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                }
            ],
        }
        response = client.with_session_auth("user@example.com").post("/stocks/bulk", json=stock_data)
        assert response.status_code == 201
        assert response.json["stocks_count"] == 0
        assert existing_stock.quantity == 10

    def should_not_create_duplicated_stock(self, client):
        offer = offers_factories.EventOfferFactory()
        beginning = datetime.datetime.utcnow() + relativedelta(hours=4)
        beginning_later = beginning + relativedelta(days=10)
        price_cat_label_1 = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat_label_2 = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 2")
        price_category_1 = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel=price_cat_label_1, price=10
        )
        price_category_2 = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel=price_cat_label_2, price=20
        )
        offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=format_into_utc_date(beginning),
            bookingLimitDatetime=format_into_utc_date(beginning),
            priceCategory=price_category_1,
            quantity=10,
        )
        offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=format_into_utc_date(beginning_later),
            bookingLimitDatetime=format_into_utc_date(beginning_later),
            priceCategory=price_category_2,
            quantity=20,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        # First stock should be skipped
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "priceCategoryId": price_category_1.id,
                    "quantity": 10,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                },
                {
                    "priceCategoryId": price_category_1.id,
                    "quantity": 10,
                    "beginningDatetime": format_into_utc_date(beginning_later),
                    "bookingLimitDatetime": format_into_utc_date(beginning_later),
                },
                {
                    "priceCategoryId": price_category_2.id,
                    "quantity": 10,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                },
                {
                    "priceCategoryId": price_category_2.id,
                    "quantity": 20,
                    "beginningDatetime": format_into_utc_date(beginning_later),
                    "bookingLimitDatetime": format_into_utc_date(beginning_later),
                },
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk", json=stock_data)

        assert response.status_code == 201
        assert response.json["stocks_count"] == 2


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("pcapi.core.offers.models.Offer.MAX_STOCKS_PER_OFFER", 2)
    def test_create_event_exceed_max_stocks_count(self, mocked_async_index_offer_ids, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        shared_label = offers_factories.PriceCategoryLabelFactory(label="Shared", venue=offer.venue)
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=shared_label, price=20)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "priceCategoryId": price_cat.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                }
                for _ in range(3)
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk", json=stock_data)
        assert response.status_code == 400
        assert response.json["stocks"] == ["Le nombre maximum de stocks par offre est de 2"]

    def test_beginning_datetime_after_booking_limit_datetime(self, client):
        offer = offers_factories.EventOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        bookingLimitDatetime = datetime.datetime.utcnow() + relativedelta(days=10)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(bookingLimitDatetime),
                    "priceCategoryId": price_cat.id,
                    "quantity": 1000,
                },
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk", json=stock_data)

        assert response.status_code == 400

        response_dict = response.json
        assert response_dict == {
            "stocks": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"],
        }

    def test_cannot_create_event_with_wrong_price_category_id(self, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        price_category = offers_factories.PriceCategoryFactory(offer=offer)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                    "priceCategoryId": price_category.id + 1,
                }
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk", json=stock_data)
        assert response.status_code == 400
        assert response.json["price_category_id"] == [f"Le tarif avec l'id {price_category.id + 1} n'existe pas"]

    def test_cannot_create_event_stock_with_price_higher_than_300_euros(self, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        too_high_price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="too_high_price_category", price=310
        )
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                    "priceCategoryId": too_high_price_category.id,
                }
            ],
        }

        # Then
        response = client.with_session_auth("user@example.com").post("/stocks/bulk", json=stock_data)
        assert response.status_code == 400
        assert response.json["priceCategoryId"] == ["Le prix d’une offre ne peut excéder 300 euros."]


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_has_no_rights_and_creating_stock_from_offer_id(self, client, db_session):
        user = users_factories.ProFactory(email="wrong@example.com")
        offer = offers_factories.EventOfferFactory()
        price_category = offers_factories.PriceCategoryFactory(offer=offer)
        offerers_factories.UserOffererFactory(user__email="right@example.com", offerer=offer.venue.managingOfferer)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                    "priceCategoryId": price_category.id + 1,
                },
            ],
        }
        response = client.with_session_auth(user.email).post("/stocks/bulk", json=stock_data)

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }
