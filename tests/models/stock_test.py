from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from pytest import approx

from models import ApiErrors
from models.pc_object import DeletedRecordException
from models.stock import Stock
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue
from tests.model_creators.specific_creators import create_stock_with_event_offer, create_stock_from_offer, \
    create_offer_with_thing_product, create_offer_with_event_product


@clean_database
def test_beginning_datetime_cannot_be_after_end_datetime(app):
    # given
    offer = create_offer_with_thing_product(create_venue(create_offerer()))
    now = datetime.utcnow()
    beginning = now - timedelta(days=5)
    end = beginning - timedelta(days=1)
    stock = create_stock(offer=offer, beginning_datetime=beginning, end_datetime=end)

    # when
    with pytest.raises(ApiErrors) as e:
        repository.save(stock)

    # then
    assert e.value.errors['endDatetime'] == [
        'La date de fin de l’événement doit être postérieure à la date de début'
    ]


@clean_database
def test_date_modified_should_be_updated_if_available_changed(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(offer=offer, date_modified=datetime(2018, 2, 12), available=1)
    repository.save(stock)

    # when
    stock = Stock.query.first()
    stock.available = 10
    repository.save(stock)

    # then
    stock = Stock.query.first()
    assert stock.dateModified.timestamp() == approx(datetime.now().timestamp())


@clean_database
def test_date_modified_should_not_be_updated_if_price_changed(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(offer=offer, date_modified=datetime(2018, 2, 12), available=1, price=1)
    repository.save(stock)

    # when
    stock = Stock.query.first()
    stock.price = 5
    repository.save(stock)

    # then
    stock = Stock.query.first()
    assert stock.dateModified == datetime(2018, 2, 12)


@clean_database
def test_queryNotSoftDeleted_should_not_return_soft_deleted(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue)
    stock.isSoftDeleted = True
    repository.save(stock)

    # When
    result = Stock.queryNotSoftDeleted().all()

    # Then
    assert not result


@clean_database
def test_populate_dict_on_soft_deleted_object_raises_DeletedRecordException(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_from_offer(create_offer_with_event_product(venue))
    stock.isSoftDeleted = True
    repository.save(stock)
    # When
    with pytest.raises(DeletedRecordException):
        stock.populate_from_dict({"available": 5})


@clean_database
def test_stock_cannot_have_a_negative_price(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, price=-10)

    # when
    with pytest.raises(ApiErrors) as e:
        repository.save(stock)

    # then
    assert e.value.errors['global'] is not None


@clean_database
def test_stock_cannot_have_a_negative_available_stock(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, available=-4)

    # when
    with pytest.raises(ApiErrors) as e:
        repository.save(stock)

    # then
    assert e.value.errors['available'] == ["Le stock doit être positif"]


@clean_database
def test_stock_can_have_an_available_stock_equal_to_zero(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, available=0)

    # when
    repository.save(stock)

    # then
    assert stock.available == 0


@clean_database
def test_available_stocks_can_be_changed_even_when_bookings_with_cancellations_exceed_available(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, available=2, price=0)
    repository.save(stock)
    user1 = create_user()
    user2 = create_user(email='test@mail.com')
    cancelled_booking1 = create_booking(user=user1, stock=stock, is_cancelled=True, quantity=1)
    cancelled_booking2 = create_booking(user=user1, stock=stock, is_cancelled=True, quantity=1)
    booking1 = create_booking(user=user1, stock=stock, is_cancelled=False, quantity=1)
    booking2 = create_booking(user=user2, stock=stock, is_cancelled=False, quantity=1)
    repository.save(cancelled_booking1, cancelled_booking2, booking1, booking2)
    stock.available = 3

    # When
    try:
        repository.save(stock)
    except:
        # Then
        assert False


@clean_database
def test_update_available_stocks_even_when_is_less_than_number_of_bookings(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, available=2, price=0)
    repository.save(stock)
    user = create_user()
    booking = create_booking(user=user, stock=stock, is_cancelled=False, quantity=2)
    repository.save(booking)
    stock.available = 1

    # When
    repository.save(stock)

    # Then
    assert Stock.query.get(stock.id).available == 1


class StockRemainingQuantityTest:
    @clean_database
    def test_remaining_quantity_for_stock_is_2_when_there_is_no_booking(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, available=2, price=0)

        # When
        repository.save(stock)

        # Then
        assert Stock.query.get(stock.id).remainingQuantity == 2

    @clean_database
    def test_remaining_quantity_for_stock_is_0_when_there_is_2_bookings(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, available=2, price=0)
        repository.save(stock)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=False, quantity=1)

        # When
        repository.save(booking1, booking2)

        # Then
        assert Stock.query.get(stock.id).remainingQuantity == 0

    @clean_database
    def test_remaining_quantity_for_stock_is_0_when_there_are_2_bookings_not_used(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, available=2, price=0)
        repository.save(stock)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock, is_cancelled=False, is_used=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=False, is_used=False, quantity=1)
        repository.save(booking1, booking2)
        stock.available = 1

        # When
        repository.save(stock)

        # Then
        assert Stock.query.get(stock.id).remainingQuantity == 0

    @clean_database
    def test_remaining_quantity_for_stock_is_1_when_there_are_2_bookings_and_1_is_used_before_last_stock_update(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, available=2, price=0)
        repository.save(stock)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock, date_used=datetime.utcnow() - timedelta(days=1), is_cancelled=False,
                                  is_used=True, quantity=1)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=False, is_used=False, quantity=1)

        # When
        repository.save(booking1, booking2)

        # Then
        assert Stock.query.get(stock.id).remainingQuantity == 1


class IsBookableTest:
    @freeze_time('2019-07-10')
    def test_is_False_when_booking_limit_datetime_is_in_the_past(self):
        # Given
        limit_datetime = datetime(2019, 7, 9)

        # When
        stock = create_stock(booking_limit_datetime=limit_datetime)

        # Then
        assert stock.isBookable is False

    @freeze_time('2019-07-10')
    def test_is_True_when_booking_limit_datetime_is_in_the_future(self):
        # Given
        limit_datetime = datetime(2019, 7, 11)

        # When
        stock = create_stock(booking_limit_datetime=limit_datetime)

        # Then
        assert stock.isBookable is True

    def test_is_True_when_no_booking_datetime_limit(self):
        # When
        stock = create_stock(booking_limit_datetime=None)

        # Then
        assert stock.isBookable is True
