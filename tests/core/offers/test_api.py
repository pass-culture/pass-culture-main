import datetime
from unittest import mock

from flask import current_app as app
import pytest

from pcapi import models
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import api
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories
from pcapi.models import api_errors
from pcapi.models.feature import override_features


@pytest.mark.usefixtures("db_session")
class CreateStockTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_create_thing_offer(self, mocked_add_offer_id):
        offer = factories.ThingOfferFactory()

        stock = api.create_stock(offer=offer, price=10)

        assert stock.offer == offer
        assert stock.price == 10
        assert stock.quantity is None
        assert stock.beginningDatetime is None
        assert stock.bookingLimitDatetime is None
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=offer.id)

    def test_create_event_offer(self):
        offer = factories.EventOfferFactory()
        beginning = datetime.datetime(2024, 1, 1, 12, 0, 0)
        booking_limit = datetime.datetime(2024, 1, 1, 9, 0, 0)

        stock = api.create_stock(
            offer=offer,
            price=10,
            quantity=7,
            beginning=beginning,
            booking_limit_datetime=booking_limit,
        )

        assert stock.offer == offer
        assert stock.price == 10
        assert stock.quantity == 7
        assert stock.beginningDatetime == beginning
        assert stock.bookingLimitDatetime == booking_limit

    @override_features(SYNCHRONIZE_ALGOLIA=False)
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_do_not_sync_algolia_if_feature_is_disabled(self, mocked_add_offer_id):
        offer = factories.ThingOfferFactory()

        api.create_stock(offer=offer, price=10, quantity=7)

        mocked_add_offer_id.assert_not_called()

    def test_fail_if_missing_dates(self):
        offer = factories.EventOfferFactory()

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, beginning=None, booking_limit_datetime=None)

        assert "beginningDatetime" in error.value.errors

    def test_fail_if_offer_is_not_editable(self):
        offerer = offerers_factories.ProviderFactory()
        offer = factories.ThingOfferFactory(lastProvider=offerer, idAtProviders="1")

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, beginning=None, booking_limit_datetime=None)

        assert error.value.errors == {"global": ["Les offres importées ne sont pas modifiables"]}


@pytest.mark.usefixtures("db_session")
class EditStockTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_edit_stock_basics(self, mocked_add_offer_id):
        stock = factories.EventStockFactory()

        beginning = datetime.datetime.now() + datetime.timedelta(days=2)
        booking_limit_datetime = datetime.datetime.now() + datetime.timedelta(days=1)
        api.edit_stock(
            stock,
            price=5,
            quantity=20,
            beginning=beginning,
            booking_limit_datetime=booking_limit_datetime,
        )

        stock = models.StockSQLEntity.query.one()
        assert stock.price == 5
        assert stock.quantity == 20
        assert stock.beginningDatetime == beginning
        assert stock.bookingLimitDatetime == booking_limit_datetime
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=stock.offerId)

    @mock.patch("pcapi.domain.user_emails.send_batch_stock_postponement_emails_to_users")
    def test_sends_email_if_beginning_changes(self, mocked_send_email):
        stock = factories.EventStockFactory()
        booking1 = bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock, isCancelled=True)

        beginning = datetime.datetime.now() + datetime.timedelta(days=10)
        api.edit_stock(
            stock,
            price=5,
            quantity=20,
            beginning=beginning,
            booking_limit_datetime=stock.bookingLimitDatetime,
        )

        stock = models.StockSQLEntity.query.one()
        assert stock.beginningDatetime == beginning
        notified_bookings = mocked_send_email.call_args_list[0][0][0]
        assert notified_bookings == [booking1]

    def test_checks_number_of_reservations(self):
        stock = factories.EventStockFactory()
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock, isCancelled=True)

        # With a quantity too low
        quantity = 0
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock,
                price=stock.price,
                quantity=quantity,
                beginning=stock.beginningDatetime,
                booking_limit_datetime=stock.bookingLimitDatetime,
            )
        msg = "Le stock total ne peut être inférieur au nombre de réservations"
        assert error.value.errors["quantity"][0] == msg

        # With enough quantity
        quantity = 2
        api.edit_stock(
            stock,
            price=stock.price,
            quantity=quantity,
            beginning=stock.beginningDatetime,
            booking_limit_datetime=stock.bookingLimitDatetime,
        )
        stock = models.StockSQLEntity.query.one()
        assert stock.quantity == 2

    def test_checks_booking_limit_is_after_beginning(self):
        stock = factories.EventStockFactory()

        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock,
                price=stock.price,
                quantity=stock.quantity,
                beginning=datetime.datetime.now(),
                booking_limit_datetime=datetime.datetime.now() + datetime.timedelta(days=1),
            )
        msg = "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement"
        assert error.value.errors["bookingLimitDatetime"][0] == msg

    def test_cannot_edit_if_provider_is_titelive(self):
        provider = offerers_factories.ProviderFactory(localClass="TiteLiveStocks")
        stock = factories.EventStockFactory(offer__lastProvider=provider, offer__idAtProviders="1")

        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(
                stock,
                price=stock.price,
                quantity=stock.quantity,
                beginning=stock.beginningDatetime,
                booking_limit_datetime=stock.bookingLimitDatetime,
            )
        msg = "Les offres importées ne sont pas modifiables"
        assert error.value.errors["global"][0] == msg

    def test_can_edit_only_some_fields_if_provider_is_allocine(self):
        provider = offerers_factories.ProviderFactory(localClass="AllocineStocks")
        stock = factories.EventStockFactory(
            offer__lastProvider=provider,
            offer__idAtProviders="1",
        )
        initial_beginning = stock.beginningDatetime

        # Try to change everything, including "beginningDatetime" which is forbidden.
        new_booking_limit = datetime.datetime.now() + datetime.timedelta(days=1)
        changes = {
            "price": 5,
            "quantity": 20,
            "beginning": datetime.datetime.now() + datetime.timedelta(days=2),
            "booking_limit_datetime": new_booking_limit,
        }
        with pytest.raises(api_errors.ApiErrors) as error:
            api.edit_stock(stock, **changes)
        msg = "Pour les offres importées, certains champs ne sont pas modifiables"
        assert error.value.errors["global"][0] == msg

        # Try to change everything except "beginningDatetime".
        changes["beginning"] = stock.beginningDatetime
        api.edit_stock(stock, **changes)
        stock = models.StockSQLEntity.query.one()
        assert stock.price == 5
        assert stock.quantity == 20
        assert stock.beginningDatetime == initial_beginning
        assert stock.bookingLimitDatetime == new_booking_limit
        assert set(stock.fieldsUpdated) == {"price", "quantity", "bookingLimitDatetime"}


@pytest.mark.usefixtures("db_session")
class DeleteStockTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_delete_stock_basics(self, mocked_add_offer_id):
        stock = factories.EventStockFactory()

        api.delete_stock(stock)

        stock = models.StockSQLEntity.query.one()
        assert stock.isSoftDeleted
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=stock.offerId)

    @mock.patch("pcapi.domain.user_emails.send_batch_cancellation_emails_to_users")
    @mock.patch("pcapi.domain.user_emails.send_offerer_bookings_recap_email_after_offerer_cancellation")
    def test_delete_stock_cancel_bookings_and_send_emails(self, mocked_send_to_beneficiaries, mocked_send_to_offerer):
        stock = factories.EventStockFactory()
        booking1 = bookings_factories.BookingFactory(stock=stock)
        booking2 = bookings_factories.BookingFactory(stock=stock, isCancelled=True)
        booking3 = bookings_factories.BookingFactory(stock=stock, isUsed=True)

        api.delete_stock(stock)

        stock = models.StockSQLEntity.query.one()
        assert stock.isSoftDeleted
        booking1 = models.Booking.query.get(booking1.id)
        assert booking1.isCancelled
        booking2 = models.Booking.query.get(booking2.id)
        assert booking2.isCancelled  # unchanged
        booking3 = models.Booking.query.get(booking3.id)
        assert not booking3.isCancelled  # unchanged

        notified_bookings_beneficiaries = mocked_send_to_beneficiaries.call_args_list[0][0][0]
        notified_bookings_offerers = mocked_send_to_offerer.call_args_list[0][0][0]
        assert notified_bookings_beneficiaries == notified_bookings_offerers
        assert notified_bookings_beneficiaries == [booking1]

    def test_can_delete_if_stock_from_allocine(self):
        provider = offerers_factories.ProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = factories.StockFactory(offer=offer)

        api.delete_stock(stock)

        stock = models.StockSQLEntity.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_stock_from_titelive(self):
        provider = offerers_factories.ProviderFactory(localClass="TiteLiveStocks")
        offer = factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = factories.StockFactory(offer=offer)

        with pytest.raises(api_errors.ApiErrors) as error:
            api.delete_stock(stock)
        msg = "Les offres importées ne sont pas modifiables"
        assert error.value.errors["global"][0] == msg

        stock = models.StockSQLEntity.query.one()
        assert not stock.isSoftDeleted

    def test_can_delete_if_event_ended_recently(self):
        recently = datetime.datetime.now() - datetime.timedelta(days=1)
        stock = factories.EventStockFactory(beginningDatetime=recently)

        api.delete_stock(stock)
        stock = models.StockSQLEntity.query.one()
        assert stock.isSoftDeleted

    def test_cannot_delete_if_too_late(self):
        too_long_ago = datetime.datetime.now() - datetime.timedelta(days=3)
        stock = factories.EventStockFactory(beginningDatetime=too_long_ago)

        with pytest.raises(exceptions.TooLateToDeleteStock):
            api.delete_stock(stock)
        stock = models.StockSQLEntity.query.one()
        assert not stock.isSoftDeleted
