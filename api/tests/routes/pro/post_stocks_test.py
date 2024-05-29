import dataclasses
import datetime
from decimal import Decimal
from unittest import mock
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core import search
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional import sendinblue_template_ids
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import Stock
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    @patch("pcapi.core.search.async_index_offer_ids")
    def test_create_one_product_stock(self, mocked_async_index_offer_ids, client):
        # Given
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [{"price": 20}],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 201
        assert response.json["stocks_count"] == 1
        assert len(Stock.query.all()) == len(stock_data["stocks"])
        created_stock = Stock.query.first()

        assert offer.id == created_stock.offerId
        assert created_stock.price == 20
        assert offer.isActive is False
        assert offers_models.PriceCategory.query.count() == 0
        assert offers_models.PriceCategoryLabel.query.count() == 0
        assert offer.validation == OfferValidationStatus.DRAFT
        assert len(mails_testing.outbox) == 0  # Mail sent during fraud validation
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=search.IndexationReason.STOCK_CREATION,
        )

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_create_event_stocks(self, mocked_async_index_offer_ids, client):
        # Given
        offer = offers_factories.EventOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        first_label = offers_factories.PriceCategoryLabelFactory(label="Tarif 1", venue=offer.venue)
        second_label = offers_factories.PriceCategoryLabelFactory(label="Tarif 2", venue=offer.venue)
        first_price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=first_label, price=20)
        second_price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=second_label, price=30)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)

        # When
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

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 201

        assert response.json["stocks_count"] == len(stock_data["stocks"])

        created_stocks = Stock.query.order_by(Stock.price).all()
        assert len(created_stocks) == 3
        assert offers_models.PriceCategory.query.count() == 2
        assert offers_models.PriceCategoryLabel.query.count() == 2
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
        # Given
        offer = offers_factories.EventOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        shared_label = offers_factories.PriceCategoryLabelFactory(label="Shared", venue=offer.venue)
        first_price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=shared_label, price=20)
        unique_label = offers_factories.PriceCategoryLabelFactory(label="unique", venue=offer.venue)
        second_price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=unique_label, price=30)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        beginning_later = datetime.datetime.utcnow() + relativedelta(days=11)

        # When
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

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 201
        created_stocks = Stock.query.order_by(Stock.price).all()
        assert len(created_stocks) == 3
        assert offers_models.PriceCategory.query.count() == 2
        assert offers_models.PriceCategoryLabel.query.count() == 2
        assert created_stocks[0].price == 20
        assert created_stocks[0].priceCategory.price == 20
        assert created_stocks[0].priceCategory.label == "Shared"
        assert created_stocks[0].priceCategory is created_stocks[1].priceCategory
        assert created_stocks[2].priceCategory is second_price_cat

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_edit_one_stock(self, mocked_async_index_offer_ids, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        existing_stock = offers_factories.StockFactory(offer=offer, price=10, quantity=10)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [{"id": existing_stock.id, "price": 20, "quantity": 10}],
        }

        client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        created_stock = Stock.query.first()
        assert offer.id == created_stock.offerId
        assert created_stock.price == 20
        assert len(Stock.query.all()) == 1
        assert offers_models.PriceCategory.query.count() == 0
        assert offers_models.PriceCategoryLabel.query.count() == 0

    def test_do_not_edit_one_stock_when_duplicated(self, client):
        offer = offers_factories.EventOfferFactory()
        beginning = datetime.datetime.utcnow()
        tomorrow = beginning + relativedelta(days=1)
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
        offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=format_into_utc_date(tomorrow),
            bookingLimitDatetime=format_into_utc_date(beginning),
            priceCategory=price_category,
            price=10,
            quantity=10,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "priceCategoryId": price_category.id,
                    "price": 10,
                    "quantity": 10,
                    "beginningDatetime": format_into_utc_date(tomorrow),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                }
            ],
        }
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        assert response.status_code == 201
        assert existing_stock.beginningDatetime == beginning  # didn't change

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
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        # First stock should be skipped
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "priceCategoryId": price_category.id,
                    "price": 10,
                    "quantity": 20,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                }
            ],
        }
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 201
        assert response.json["stocks_count"] == 0
        assert existing_stock.quantity == 10

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_edit_one_event_stock_using_price_category(self, mocked_async_index_offer_ids, client):
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.EventOfferFactory(
            isActive=False,
            validation=OfferValidationStatus.DRAFT,
            priceCategories=[],
            venue=venue,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel__venue=venue)
        existing_stock = offers_factories.StockFactory(offer=offer, price=10, priceCategory=None)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                    "priceCategoryId": price_category.id,
                }
            ],
        }
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.json["stocks_count"] == len(stock_data["stocks"])
        created_stock = Stock.query.first()
        assert offer.id == created_stock.offerId
        assert price_category.price == created_stock.price
        assert len(Stock.query.all()) == 1
        assert offers_models.PriceCategory.query.count() == 1
        assert offers_models.PriceCategoryLabel.query.count() == 1

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_edit_one_event_stock_created_with_price_category(self, mocked_async_index_offer_ids, client):
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.EventOfferFactory(
            isActive=False,
            validation=OfferValidationStatus.DRAFT,
            venue=venue,
        )
        old_price_category = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel__venue=venue)
        new_price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__venue=venue, price=25
        )

        existing_stock = offers_factories.StockFactory(offer=offer, price=10, priceCategory=old_price_category)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                    "priceCategoryId": new_price_category.id,
                }
            ],
        }
        client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        created_stock = Stock.query.first()
        assert offer.id == created_stock.offerId
        assert len(Stock.query.all()) == 1
        assert created_stock.priceCategory == new_price_category
        assert created_stock.price == 25

    def test_create_one_stock_with_activation_codes(self, client):
        # Given
        offer = offers_factories.DigitalOfferFactory(url="https://chartreu.se")
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        activation_codes = ["AZ3", "3ZE"]

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "price": 20,
                    "quantity": 30,
                    "activationCodes": activation_codes,
                    "bookingLimitDatetime": "2021-06-15T23:59:59Z",
                    "activationCodesExpirationDatetime": "2021-06-22T23:59:59Z",
                }
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 201

        assert response.json["stocks_count"] == len(stock_data["stocks"])

        created_stock: Stock = Stock.query.first()
        assert offer.id == created_stock.offerId
        assert created_stock.price == 20
        assert created_stock.quantity == 2  # Same as the activation codes length
        assert [activation_code.code for activation_code in created_stock.activationCodes] == activation_codes
        for activation_code in created_stock.activationCodes:
            assert activation_code.expirationDate == datetime.datetime(2021, 6, 22, 23, 59, 59)

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_upsert_multiple_stocks(self, mocked_async_index_offer_ids, client):
        # Given
        offer = offers_factories.ThingOfferFactory()
        existing_stock = offers_factories.StockFactory(offer=offer, price=10)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        booking_limit_datetime = datetime.datetime(2019, 2, 14)

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "price": 20,
                    "quantity": None,
                    "bookingLimitDatetime": format_into_utc_date(booking_limit_datetime),
                },
                {
                    "price": 30,
                    "quantity": None,
                    "bookingLimitDatetime": format_into_utc_date(booking_limit_datetime),
                },
                {
                    "price": 40,
                    "quantity": 0,
                    "bookingLimitDatetime": format_into_utc_date(booking_limit_datetime),
                },
            ],
        }
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 201

        response_dict = response.json
        assert response_dict["stocks_count"] == len(stock_data["stocks"])
        created_stocks = Stock.query.all()
        for idx, result_stock_id in enumerate(created_stocks):
            expected_stock = stock_data["stocks"][idx]
            result_stock = Stock.query.filter_by(id=result_stock_id.id).one()
            assert result_stock.price == expected_stock["price"]
            assert result_stock.quantity == expected_stock["quantity"]
            assert result_stock.bookingLimitDatetime == booking_limit_datetime

        assert [call.args[0] for call in mocked_async_index_offer_ids.call_args_list] == [
            [offer.id],
            [offer.id],
            [offer.id],
        ]

    def test_sends_email_if_beginning_date_changes_on_edition(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer, bookingEmail="venue@postponed.net")
        offer = offers_factories.EventOfferFactory(venue=venue, bookingEmail="offer@bookingemail.fr")
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)
        existing_stock = offers_factories.EventStockFactory(offer=offer, priceCategory=price_cat)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "priceCategoryId": price_cat.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                },
            ],
        }
        bookings_factories.BookingFactory(stock=existing_stock, user__email="beneficiary@bookingEmail.fr")
        bookings_factories.CancelledBookingFactory(stock=existing_stock)

        # When
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 201
        stock = offers_models.Stock.query.one()
        assert stock.beginningDatetime == beginning
        assert stock.bookingLimitDatetime == beginning

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            sendinblue_template_ids.TransactionalEmail.EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO.value
        )
        assert mails_testing.outbox[0]["To"] == "venue@postponed.net"
        assert mails_testing.outbox[1]["template"] == dataclasses.asdict(
            sendinblue_template_ids.TransactionalEmail.BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[1]["To"] == "beneficiary@bookingEmail.fr"

    @mock.patch("pcapi.core.bookings.api.update_cancellation_limit_dates")
    def should_update_bookings_cancellation_limit_date_on_delayed_event(
        self, mock_update_cancellation_limit_dates, client
    ):
        now = datetime.datetime.utcnow()
        event_in_4_days = now + relativedelta(days=4)
        event_reported_in_10_days = now + relativedelta(days=10)
        offer = offers_factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)

        existing_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=event_in_4_days, priceCategory=price_cat
        )
        booking = bookings_factories.BookingFactory(stock=existing_stock, dateCreated=now)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "priceCategoryId": price_cat.id,
                    "beginningDatetime": format_into_utc_date(event_reported_in_10_days),
                    "bookingLimitDatetime": format_into_utc_date(existing_stock.bookingLimitDatetime),
                },
            ],
        }

        # When
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 201
        mock_update_cancellation_limit_dates.assert_called_once_with([booking], event_reported_in_10_days)

    def should_invalidate_booking_token_when_event_is_reported(self, client):
        # Given
        now = datetime.datetime.utcnow()
        booking_made_3_days_ago = now - relativedelta(days=3)
        event_in_4_days = now + relativedelta(days=4)
        event_reported_in_10_days = now + relativedelta(days=10)
        offer = offers_factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)

        existing_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=event_in_4_days, priceCategory=price_cat
        )
        booking = bookings_factories.UsedBookingFactory(stock=existing_stock, dateCreated=booking_made_3_days_ago)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "priceCategoryId": price_cat.id,
                    "beginningDatetime": format_into_utc_date(event_reported_in_10_days),
                    "bookingLimitDatetime": format_into_utc_date(existing_stock.bookingLimitDatetime),
                },
            ],
        }

        # When
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 201
        updated_booking = bookings_models.Booking.query.filter_by(id=booking.id).one()
        assert updated_booking.status is not bookings_models.BookingStatus.USED
        assert updated_booking.dateUsed is None
        assert updated_booking.cancellationLimitDate == booking.cancellationLimitDate

    def should_not_invalidate_booking_token_when_event_is_reported_in_less_than_48_hours(self, client):
        # Given
        now = datetime.datetime.utcnow()
        date_used_in_48_hours = now + relativedelta(days=2)
        event_in_3_days = now + relativedelta(days=3)
        event_reported_in_less_48_hours = now + relativedelta(days=1)
        offer = offers_factories.EventOfferFactory(bookingEmail="test@bookingEmail.fr")
        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)

        existing_stock = offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=event_in_3_days,
            priceCategory=price_cat,
            bookingLimitDatetime=now,
        )
        booking = bookings_factories.UsedBookingFactory(
            stock=existing_stock, dateCreated=now, dateUsed=date_used_in_48_hours
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "priceCategoryId": price_cat.id,
                    "beginningDatetime": format_into_utc_date(event_reported_in_less_48_hours),
                    "bookingLimitDatetime": format_into_utc_date(existing_stock.bookingLimitDatetime),
                },
            ],
        }

        # When
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 201
        updated_booking = bookings_models.Booking.query.filter_by(id=booking.id).one()
        assert updated_booking.status is bookings_models.BookingStatus.USED
        assert updated_booking.dateUsed == date_used_in_48_hours

    def test_update_thing_stock_without_booking_limit_date(self, client):
        # We allow nullable bookingLimitDate for thing Stock.
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        booking_limit = datetime.datetime(2019, 2, 14)
        existing_stock = offers_factories.StockFactory(offer=offer, price=10, bookingLimitDatetime=booking_limit)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [{"price": 20, "id": existing_stock.id}],
        }

        client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        created_stock = Stock.query.first()
        assert offer.id == created_stock.offerId
        assert created_stock.price == 20
        assert created_stock.bookingLimitDatetime is None

    @pytest.mark.parametrize("subcategoryId", offers_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES)
    def should_show_as_ongoing_when_stock_is_no_longer_free_for_automatically_used_subcategories(
        self, client, subcategoryId
    ):
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategoryId)
        existing_stock = offers_factories.StockFactory(offer=offer, price=0)
        booking = bookings_factories.UsedBookingFactory(stock=existing_stock)

        offerers_factories.UserOffererFactory(
            user__email="userofferer@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [{"id": existing_stock.id, "price": 20}],
        }

        response = client.with_session_auth("userofferer@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 201

        response = client.with_token(booking.user.email).get("/native/v1/bookings")
        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["id"] == booking.id
        assert not response.json["ended_bookings"]

    def test_update_event_stock_quantity(self, client):
        beginning = datetime.datetime.utcnow()
        offer = offers_factories.EventOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        price_category_1 = offers_factories.PriceCategoryFactory(offer=offer, price=10)
        existing_stock = offers_factories.EventStockFactory(
            offer=offer,
            beginningDatetime=format_into_utc_date(beginning),
            bookingLimitDatetime=format_into_utc_date(beginning),
            priceCategory=price_category_1,
            quantity=20,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "priceCategoryId": price_category_1.id,
                    "id": existing_stock.id,
                    "quantity": 42,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                }
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        assert response.status_code == 201
        created_stock = Stock.query.first()
        assert offer.id == created_stock.offerId
        assert created_stock.quantity == 42

    def should_not_create_duplicated_stock(self, client):
        # Given
        offer = offers_factories.EventOfferFactory()
        beginning = datetime.datetime.utcnow()
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
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
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

        # When
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        # Then
        assert response.status_code == 201
        assert response.json["stocks_count"] == 2


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_missing_offer_id(self, client):
        # Given
        offer = offers_factories.ThingOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        booking_limit_datetime = datetime.datetime(2019, 2, 14)

        # When
        stock_data = {
            "stocks": [
                {
                    "quantity": -2,
                    "price": 0,
                    "bookingLimitDatetime": format_into_utc_date(booking_limit_datetime),
                },
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 400
        assert response.json == {
            "offerId": ["Ce champ est obligatoire"],
            "stocks.0.id": ["Ce champ est obligatoire"],
            "stocks.0.quantity": [
                "Saisissez un nombre supérieur ou égal à 0",
                "Saisissez un nombre supérieur ou égal à 0",
            ],
        }

    def test_update_thing_stock_without_price(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        existing_stock = offers_factories.StockFactory(offer=offer)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        stock_data = {
            "offerId": offer.id,
            "stocks": [{"quantity": 20, "id": existing_stock.id}],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        assert response.json["price"] == ["Le prix est obligatoire pour les offres produit"]

    def test_exceed_max_stock_quantity(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        existing_stock = offers_factories.StockFactory(offer=offer, price=10)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [{"id": existing_stock.id, "price": 20, "quantity": 1234567890987654}],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        assert response.json["stocks.0.quantity"] == [
            "ensure this value is less than or equal to 1000000",
            "ensure this value is less than or equal to 1000000",
        ]

    def test_update_product_stock_without_price_is_forbidden(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        existing_stock = offers_factories.StockFactory(offer=offer)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        stock_data = {
            "offerId": offer.id,
            "stocks": [{"quantity": 20, "id": existing_stock.id}],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        assert response.json["price"] == ["Le prix est obligatoire pour les offres produit"]

    def test_patch_non_approved_offer_fails(self, client):
        pending_validation_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)
        stock = offers_factories.StockFactory(offer=pending_validation_offer)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=pending_validation_offer.venue.managingOfferer,
        )
        stock_data = {
            "offerId": pending_validation_offer.id,
            "stocks": [{"id": stock.id, "price": 20}],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_invalid_activation_codes_expiration_datetime(self, client):
        # Given
        offer = offers_factories.DigitalOfferFactory(url="https://chartreu.se")
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "price": 20,
                    "activationCodes": ["AZ3"],
                    "bookingLimitDatetime": "2021-06-15T02:59:59Z",
                    "activationCodesExpirationDatetime": "2021-06-16T02:59:59Z",
                }
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 400
        assert response.json["activationCodesExpirationDatetime"] == [
            (
                "La date limite de validité des codes d'activation doit être ultérieure"
                " d'au moins 7 jours à la date limite de réservation"
            )
        ]

    def test_invalid_booking_limit_datetime(self, client):
        # Given
        offer = offers_factories.DigitalOfferFactory(url="https://chartreu.se")
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        existing_stock = offers_factories.StockFactory(offer=offer)
        offers_factories.ActivationCodeFactory(
            expirationDate=datetime.datetime(2020, 5, 2, 23, 59, 59),
            stock=existing_stock,
        )
        offers_factories.ActivationCodeFactory(
            expirationDate=datetime.datetime(2020, 5, 2, 23, 59, 59),
            stock=existing_stock,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "bookingLimitDatetime": "2020-05-2T23:59:59Z",
                    "price": 20.0,
                }
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 400
        assert response.json["activationCodesExpirationDatetime"] == [
            (
                "La date limite de validité des codes d'activation doit être ultérieure"
                " d'au moins 7 jours à la date limite de réservation"
            )
        ]

    def test_when_offer_is_not_digital(self, client):
        # Given
        offer = offers_factories.ThingOfferFactory(url=None)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "price": 20,
                    "activationCodes": ["AZ3"],
                    "bookingLimitDatetime": "2021-06-15T02:59:59Z",
                    "activationCodesExpirationDatetime": "2021-07-15T02:59:59Z",
                }
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 400
        assert response.json["global"] == ["Impossible de créer des codes d'activation sur une offre non-numérique"]

    def test_when_stock_does_not_belong_to_offer(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        existing_stock = offers_factories.StockFactory(price=10)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_data = {
            "offerId": offer.id,
            "stocks": [{"id": existing_stock.id, "price": 20}],
        }
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 400
        assert response.json == {"stock_id": [f"Le stock avec l'id {existing_stock.id} n'existe pas"]}

    @pytest.mark.parametrize("price_str", [float("NaN"), float("inf"), float("-inf")])
    def test_create_one_stock_with_invalid_prices(self, price_str, client):
        # Given
        offer = offers_factories.ThingOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [{"price": float(price_str)}],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 400

        response_dict = response.json
        assert response_dict == {
            "stocks.0.id": ["Ce champ est obligatoire"],
            "stocks.0.price": [
                "La valeur n'est pas un nombre décimal valide",
                "La valeur n'est pas un nombre décimal valide",
            ],
        }

    @pytest.mark.parametrize("is_update", [False, True])
    def test_beginning_datetime_after_booking_limit_datetime(self, is_update, client):
        # Given
        offer = offers_factories.EventOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        price_cat_label = offers_factories.PriceCategoryLabelFactory(venue=offer.venue, label="Tarif 1")
        price_cat = offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=price_cat_label, price=10)

        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "beginningDatetime": "2022-06-11T08:00:00Z",
                    "bookingLimitDatetime": "2022-06-12T21:59:59Z",
                    "priceCategoryId": price_cat.id,
                    "quantity": 1000,
                },
            ],
        }

        if is_update:
            stock = offers_factories.EventStockFactory(offer=offer, priceCategory=price_cat)
            stock_data["stocks"][0]["id"] = stock.id

        # When
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 400

        response_dict = response.json
        assert response_dict == {
            "stocks": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"],
        }

    def test_cannot_create_event_without_price_category(self, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "price": 20,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                }
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 400
        assert response.json["price_category_id"] == ["Le tarif est obligatoire pour les offres évènement"]

    def test_cannot_create_event_with_wrong_price_category_id(self, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        price_category = offers_factories.PriceCategoryFactory(offer=offer)
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "price": 20,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                    "priceCategoryId": price_category.id + 1,
                }
            ],
        }

        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 400
        assert response.json["price_category_id"] == [f"Le tarif avec l'id {price_category.id + 1} n'existe pas"]

    def test_cannot_update_stock_with_price_higher_than_300_euros(self, client):
        offer = offers_factories.OfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        existing_stock = offers_factories.StockFactory(offer=offer, price=300)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        too_high_price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="too_high_price_category", price=310
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "price": too_high_price_category.price,
                }
            ],
        }

        # Then
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 400
        assert response.json["price300"] == ["Le prix d’une offre ne peut excéder 300 euros."]

    def test_cannot_update_stock_with_price_outside_of_price_limitation_rule(self, client):
        offers_factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories_v2.ACHAT_INSTRUMENT.id, rate=Decimal("0.5")
        )
        offer = offers_factories.OfferFactory(
            isActive=False,
            subcategoryId=subcategories_v2.ACHAT_INSTRUMENT.id,
            lastValidationPrice=Decimal("100"),
        )
        existing_stock = offers_factories.StockFactory(offer=offer, price=120)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "price": 151,
                }
            ],
        }

        # Then
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 400
        assert response.json["priceLimitationRule"] == [
            "Le prix indiqué est invalide, veuillez créer une nouvelle offre"
        ]

    def test_cannot_update_event_stock_with_price_higher_than_300_euros(self, client):
        offer = offers_factories.EventOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        positive_price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="positive_price", price=10
        )
        too_high_price_category = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="too_high_price_category", price=310
        )
        beginning = datetime.datetime.utcnow() + relativedelta(days=10)
        existing_stock = offers_factories.EventStockFactory(
            offer=offer, priceCategoryId=positive_price_category.id, beginningDatetime=beginning
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "id": existing_stock.id,
                    "beginningDatetime": format_into_utc_date(beginning),
                    "bookingLimitDatetime": format_into_utc_date(beginning),
                    "priceCategoryId": too_high_price_category.id,
                }
            ],
        }

        # Then
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        assert response.status_code == 400
        assert response.json["priceCategoryId"] == ["Le prix d’une offre ne peut excéder 300 euros."]


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_has_no_rights_and_creating_stock_from_offer_id(self, client, db_session):
        # Given
        user = users_factories.ProFactory(email="wrong@example.com")
        offer = offers_factories.ThingOfferFactory()
        offerers_factories.UserOffererFactory(user__email="right@example.com", offerer=offer.venue.managingOfferer)
        booking_datetime = datetime.datetime.utcnow()

        # When
        stock_data = {
            "offerId": offer.id,
            "stocks": [
                {
                    "quantity": 10,
                    "price": 0,
                    "bookingLimitDatetime": format_into_utc_date(booking_datetime),
                },
            ],
        }
        response = client.with_session_auth(user.email).post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }
