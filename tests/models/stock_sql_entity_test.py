from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest
from pytest import approx

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import ApiErrors
from pcapi.models import Stock
from pcapi.models.pc_object import DeletedRecordException
from pcapi.repository import repository


CUSTOM_AUTO_USE_AFTER_EVENT_TIME_DELAY_FOR_TEST = timedelta(hours=72)


@pytest.mark.usefixtures("db_session")
def test_date_modified_should_be_updated_if_quantity_changed(app):
    # given
    offers_factories.ThingStockFactory(dateModified=datetime(2018, 2, 12), quantity=1)

    # when
    stock = Stock.query.first()
    stock.quantity = 10
    repository.save(stock)

    # then
    stock = Stock.query.first()
    assert stock.dateModified.timestamp() == approx(datetime.now().timestamp())


@pytest.mark.usefixtures("db_session")
def test_date_modified_should_not_be_updated_if_price_changed(app):
    # given
    stock = offers_factories.ThingStockFactory(dateModified=datetime(2018, 2, 12), price=1, quantity=1)
    repository.save(stock)

    # when
    stock = Stock.query.first()
    stock.price = 5
    repository.save(stock)

    # then
    stock = Stock.query.first()
    assert stock.dateModified == datetime(2018, 2, 12)


@pytest.mark.usefixtures("db_session")
def test_queryNotSoftDeleted_should_not_return_soft_deleted(app):
    # Given
    offers_factories.EventStockFactory(isSoftDeleted=True)

    # When
    result = Stock.queryNotSoftDeleted().all()

    # Then
    assert not result


@pytest.mark.usefixtures("db_session")
def test_populate_dict_on_soft_deleted_object_raises_DeletedRecordException(app):
    # Given
    stock = offers_factories.EventStockFactory(isSoftDeleted=True)

    # When
    with pytest.raises(DeletedRecordException):
        stock.populate_from_dict({"quantity": 5})


@pytest.mark.usefixtures("db_session")
def test_stock_cannot_have_a_negative_price(app):
    # given
    stock = offers_factories.ThingStockFactory()

    # when
    with pytest.raises(ApiErrors) as e:
        stock.price = -10
        repository.save(stock)

    # then
    assert e.value.errors["price"] is not None


@pytest.mark.usefixtures("db_session")
def test_stock_cannot_have_a_negative_quantity_stock(app):
    # given
    stock = offers_factories.ThingStockFactory()

    # when
    with pytest.raises(ApiErrors) as e:
        stock.quantity = -4
        repository.save(stock)

    # then
    assert e.value.errors["quantity"] == ["La quantité doit être positive."]


@pytest.mark.usefixtures("db_session")
def test_stock_can_have_an_quantity_stock_equal_to_zero(app):
    # when
    stock = offers_factories.ThingStockFactory(quantity=0)

    # then
    assert stock.quantity == 0


@pytest.mark.usefixtures("db_session")
def test_quantity_stocks_can_be_changed_even_when_bookings_with_cancellations_exceed_quantity(app):
    # Given
    stock = offers_factories.ThingStockFactory(quantity=2, price=0)
    user1 = users_factories.BeneficiaryFactory()
    user2 = users_factories.BeneficiaryFactory()

    bookings_factories.BookingFactory(user=user1, stock=stock, isCancelled=True, quantity=1)
    bookings_factories.BookingFactory(user=user1, stock=stock, isCancelled=True, quantity=1)
    bookings_factories.BookingFactory(user=user1, stock=stock, isCancelled=False, quantity=1)
    bookings_factories.BookingFactory(user=user2, stock=stock, isCancelled=False, quantity=1)

    stock.quantity = 3

    # When
    repository.save(stock)

    # Then
    assert Stock.query.get(stock.id).quantity == 3


@pytest.mark.usefixtures("db_session")
def test_should_update_stock_quantity_when_value_is_more_than_sum_of_bookings_quantity(app):
    # Given
    stock = offers_factories.ThingStockFactory(quantity=2, price=0)
    user = users_factories.BeneficiaryFactory()
    bookings_factories.BookingFactory(user=user, stock=stock, isCancelled=False, quantity=2)
    stock.quantity = 3

    # When
    repository.save(stock)

    # Then
    assert Stock.query.get(stock.id).quantity == 3


@pytest.mark.usefixtures("db_session")
def test_should_not_update_quantity_stock_when_value_is_less_than_booking_count(app):
    # given
    user = users_factories.BeneficiaryFactory()
    stock = offers_factories.ThingStockFactory(price=0, quantity=10)
    bookings_factories.BookingFactory(user=user, stock=stock, quantity=5)
    stock.quantity = 4

    # when
    with pytest.raises(ApiErrors) as e:
        repository.save(stock)

    # then
    assert e.value.errors["quantity"] == ["Le stock total ne peut être inférieur au nombre de réservations"]


class IsBookableTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_booking_limit_datetime_has_passed(self):
        # Given
        limit_datetime = datetime.utcnow() - timedelta(days=2)

        # When
        stock = offers_factories.ThingStockFactory(bookingLimitDatetime=limit_datetime)

        # Then
        assert not stock.isBookable

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_offerer_is_not_validated(self):
        # When
        stock = offers_factories.ThingStockFactory(offer__venue__managingOfferer__validationToken="validation_token")

        # Then
        assert not stock.isBookable

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_offerer_is_not_active(self):
        # When
        stock = offers_factories.ThingStockFactory(offer__venue__managingOfferer__isActive=False)

        # Then
        assert not stock.isBookable

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_venue_is_not_validated(self):
        # When
        stock = offers_factories.ThingStockFactory(offer__venue__validationToken="validation_token")

        # Then
        assert not stock.isBookable

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_offer_is_not_active(self):
        # When
        stock = offers_factories.ThingStockFactory(offer__isActive=False)

        # Then
        assert not stock.isBookable

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_stock_is_soft_deleted(self):
        # When
        stock = offers_factories.ThingStockFactory(isSoftDeleted=True)

        # Then
        assert not stock.isBookable

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_offer_is_event_with_passed_begining_datetime(self):
        # Given
        expired_stock_date = datetime.utcnow() - timedelta(days=2)

        # When
        stock = offers_factories.EventStockFactory(beginningDatetime=expired_stock_date)

        # Then
        assert not stock.isBookable

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_no_remaining_stock(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()

        # When
        stock = offers_factories.ThingStockFactory(price=0, quantity=10)
        bookings_factories.BookingFactory(user=user, stock=stock, quantity=10)

        # Then
        assert not stock.isBookable

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_stock_is_unlimited(self):
        # When
        stock = offers_factories.ThingStockFactory(price=0, quantity=None)

        # Then
        assert stock.isBookable

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_stock_requirements_are_fulfilled(self):
        # When
        stock = offers_factories.ThingStockFactory()

        # Then
        assert stock.isBookable


class IsEventExpiredTest:
    @pytest.mark.usefixtures("db_session")
    def test_is_not_expired_when_stock_is_not_an_event(self):
        # When
        stock = offers_factories.ThingStockFactory()

        # Then
        assert stock.isEventExpired is False

    @pytest.mark.usefixtures("db_session")
    def test_is_not_expired_when_stock_is_an_event_in_the_future(self):
        # Given
        three_days_from_now = datetime.utcnow() + timedelta(hours=72)

        # When
        stock = offers_factories.EventStockFactory(beginningDatetime=three_days_from_now)

        # Then
        assert stock.isEventExpired is False

    @pytest.mark.usefixtures("db_session")
    def test_is_expired_when_stock_is_an_event_in_the_past(self):
        # Given
        one_day_in_the_past = datetime.utcnow() - timedelta(hours=24)

        # When
        stock = offers_factories.EventStockFactory(beginningDatetime=one_day_in_the_past)

        # Then
        assert stock.isEventExpired is True


class IsEventDeletableTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.conf.AUTO_USE_AFTER_EVENT_TIME_DELAY", CUSTOM_AUTO_USE_AFTER_EVENT_TIME_DELAY_FOR_TEST)
    def test_is_deletable_when_stock_is_not_an_event(self):
        # When
        stock = offers_factories.ThingStockFactory()

        # Then
        assert stock.isEventDeletable is True

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.conf.AUTO_USE_AFTER_EVENT_TIME_DELAY", CUSTOM_AUTO_USE_AFTER_EVENT_TIME_DELAY_FOR_TEST)
    def test_is_deletable_when_stock_is_an_event_in_the_future(self):
        # Given
        three_days_from_now = datetime.utcnow() + timedelta(hours=72)

        # When
        stock = offers_factories.EventStockFactory(beginningDatetime=three_days_from_now)

        # Then
        assert stock.isEventDeletable is True

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.conf.AUTO_USE_AFTER_EVENT_TIME_DELAY", CUSTOM_AUTO_USE_AFTER_EVENT_TIME_DELAY_FOR_TEST)
    def test_is_deletable_when_stock_is_expired_since_less_than_event_automatic_refund_delay(self):
        # Given
        expired_date_but_not_automaticaly_refunded = (
            datetime.utcnow() - CUSTOM_AUTO_USE_AFTER_EVENT_TIME_DELAY_FOR_TEST + timedelta(1)
        )

        # When
        stock = offers_factories.EventStockFactory(beginningDatetime=expired_date_but_not_automaticaly_refunded)

        # Then
        assert stock.isEventDeletable is True

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.conf.AUTO_USE_AFTER_EVENT_TIME_DELAY", CUSTOM_AUTO_USE_AFTER_EVENT_TIME_DELAY_FOR_TEST)
    def test_is_not_deletable_when_stock_is_expired_since_more_than_event_automatic_refund_delay(self):
        # Given
        expired_date_and_automaticaly_refunded = datetime.utcnow() - CUSTOM_AUTO_USE_AFTER_EVENT_TIME_DELAY_FOR_TEST

        # When
        stock = offers_factories.EventStockFactory(beginningDatetime=expired_date_and_automaticaly_refunded)

        # Then
        assert stock.isEventDeletable is False
