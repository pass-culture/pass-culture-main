from datetime import datetime, timedelta

import pytest

from models import ApiErrors, PcObject
from models.pc_object import DeletedRecordException
from models.stock import Stock
from tests.conftest import clean_database
from tests.test_utils import create_stock_with_event_offer, create_offerer, create_venue, \
    create_offer_with_event_product, \
    create_stock_from_offer, create_offer_with_thing_product, create_booking, create_user, create_stock


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
        PcObject.save(stock)

    # then
    assert e.value.errors['endDatetime'] == [
        'La date de fin de l\'événement doit être postérieure à la date de début'
    ]


@clean_database
def test_queryNotSoftDeleted_should_not_return_soft_deleted(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue)
    stock.isSoftDeleted = True
    PcObject.save(stock)

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
    PcObject.save(stock)
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
        PcObject.save(stock)

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
        PcObject.save(stock)

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
    PcObject.save(stock)

    # then
    assert stock.available == 0


@clean_database
def test_available_stocks_can_be_changed_even_when_bookings_with_cancellations_exceed_available(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, available=2, price=0)
    PcObject.save(stock)
    user = create_user()
    cancelled_booking1 = create_booking(user, stock, quantity=1, is_cancelled=True)
    cancelled_booking2 = create_booking(user, stock, quantity=1, is_cancelled=True)
    booking1 = create_booking(user, stock, quantity=1, is_cancelled=False)
    booking2 = create_booking(create_user(email='test@mail.com'), stock, quantity=1, is_cancelled=False)
    PcObject.save(cancelled_booking1, cancelled_booking2, booking1, booking2)
    stock.available = 3

    # When
    try:
        PcObject.save(stock)
    except:
        # Then
        assert False


@clean_database
def test_update_available_stocks_with_value_less_than_number_of_bookings(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, available=2, price=0)
    PcObject.save(stock)
    user = create_user()
    booking = create_booking(user, stock, quantity=2, is_cancelled=False)
    PcObject.save(booking)
    stock.available = 1

    # When
    PcObject.save(stock)

    # Then
    assert Stock.query.get(stock.id).available == 1
