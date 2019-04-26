from datetime import datetime, timedelta
import pytest
from sqlalchemy.exc import InternalError

from models import Stock, ApiErrors, PcObject
from models.db import db
from models.pc_object import DeletedRecordException, serialize
from models.stock import Stock
from tests.conftest import clean_database
from tests.test_utils import create_stock_with_event_offer, create_offerer, create_venue, create_event_offer, \
    create_stock_from_offer, create_thing_offer, create_booking, create_user, create_stock, create_stock_with_thing_offer
from utils.human_ids import humanize

@clean_database
@pytest.mark.standalone
def test_beginning_datetime_cannot_be_after_end_datetime(app):
    # given
    offer = create_thing_offer(create_venue(create_offerer()))
    now = datetime.utcnow()
    beginning = now - timedelta(days=5)
    end = beginning - timedelta(days=1)
    stock = create_stock(offer=offer, beginning_datetime=beginning, end_datetime=end)

    # when
    with pytest.raises(ApiErrors) as e:
        PcObject.check_and_save(stock)

    # then
    assert e.value.errors['endDatetime'] == [
        'La date de fin de l\'événement doit être postérieure à la date de début'
    ]


@clean_database
@pytest.mark.standalone
def test_queryNotSoftDeleted_should_not_return_soft_deleted(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue)
    stock.isSoftDeleted = True
    PcObject.check_and_save(stock)

    # When
    result = Stock.queryNotSoftDeleted().all()

    # Then
    assert not result


@clean_database
@pytest.mark.standalone
def test_populate_dict_on_soft_deleted_object_raises_DeletedRecordException(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_from_offer(create_event_offer(venue))
    stock.isSoftDeleted = True
    PcObject.check_and_save(stock)
    # When
    with pytest.raises(DeletedRecordException):
        stock.populateFromDict({"available": 5})


@clean_database
@pytest.mark.standalone
def test_stock_cannot_have_a_negative_price(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock = create_stock_from_offer(offer, price=-10)

    # when
    with pytest.raises(ApiErrors) as e:
        PcObject.check_and_save(stock)

    # then
    assert e.value.errors['global'] is not None


@clean_database
@pytest.mark.standalone
def test_stock_cannot_have_a_negative_available_stock(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock = create_stock_from_offer(offer, available=-4)

    # when
    with pytest.raises(ApiErrors) as e:
        PcObject.check_and_save(stock)

    # then
    assert e.value.errors['available']  == ["Le stock doit être positif"]


@clean_database
@pytest.mark.standalone
def test_stock_can_have_an_available_stock_equal_to_zero(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock = create_stock_from_offer(offer, available=0)

    # when
    PcObject.check_and_save(stock)

    # then
    assert stock.available == 0


@clean_database
@pytest.mark.standalone
def test_available_stocks_can_be_changed_even_when_bookings_with_cancellations_exceed_available(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock = create_stock_from_offer(offer, available=2, price=0)
    PcObject.check_and_save(stock)
    user = create_user()
    cancelled_booking1 = create_booking(user, stock, quantity=1, is_cancelled=True)
    cancelled_booking2 = create_booking(user, stock, quantity=1, is_cancelled=True)
    booking1 = create_booking(user, stock, quantity=1, is_cancelled=False)
    booking2 = create_booking(create_user(email='test@mail.com'), stock, quantity=1, is_cancelled=False)
    PcObject.check_and_save(cancelled_booking1, cancelled_booking2, booking1, booking2)
    stock.available = 3

    # When
    try:
        PcObject.check_and_save(stock)
    except:
        # Then
        assert False


@clean_database
@pytest.mark.standalone
def test_available_stocks_cannot_be_changed_when_exceeding_bookings_quantity_2(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock = create_stock_from_offer(offer, available=2, price=0)
    PcObject.check_and_save(stock)
    user = create_user()
    booking = create_booking(user, stock, quantity=2, is_cancelled=False)
    PcObject.check_and_save(booking)
    stock.available = 1

    # When
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(stock)


@clean_database
@pytest.mark.standalone
def test_update_stock_when_stock_is_event(app):
    # Given
    beginning_datetime = datetime(2019, 2, 14)
    booking_limit_datetime = beginning_datetime - timedelta(days=2)
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, price=69)
    PcObject.check_and_save(stock)

    
    data = {    
        "beginningDatetime": serialize(beginning_datetime),
        "offerId": humanize(stock.offer.id),
        "bookingLimitDatetime": serialize(booking_limit_datetime),
        "price": 666
    } 

    # When
    stock.update_stock(data)

    # Then
    db.session.refresh(stock)
    assert stock.price == 666
    assert stock.beginningDatetime == beginning_datetime
    assert stock.bookingLimitDatetime == booking_limit_datetime


@clean_database
@pytest.mark.standalone
def test_does_not_update_stock_limit_datetime_when_not_specified(app):
    # Given
    booking_limit_datetime = datetime(2019, 1, 14)
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_thing_offer(offerer, venue, price=13, booking_limit_datetime=booking_limit_datetime)
    PcObject.check_and_save(stock)

    
    data = {    
        "offerId": humanize(stock.offer.id),
        "price": 666
    } 

    # When
    stock.update_stock(data)

    # Then
    db.session.refresh(stock)
    assert stock.price == 666
    assert stock.bookingLimitDatetime == booking_limit_datetime


@clean_database
@pytest.mark.standalone
def test_update_booking_limit_datetime_to_none_when_stock_is_thing_and_booking_limit_datetime_in_payload(app):
    # Given
    booking_limit_datetime = datetime.utcnow()
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_thing_offer(offerer, venue, booking_limit_datetime=booking_limit_datetime, price=13)
    PcObject.check_and_save(stock)

    
    data = {    
        "offerId": humanize(stock.offer.id),
        "bookingLimitDatetime": None,
        "price": 666
    } 

    # When
    stock.update_stock(data)

    # Then
    db.session.refresh(stock)
    assert stock.price == 666
    assert stock.bookingLimitDatetime is None


@clean_database
@pytest.mark.standalone
def test_update_booking_limit_datetime_to_new_date_for_thing_stock(app):
    # Given
    updated_booking_limit_datetime = datetime.utcnow()
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_thing_offer(offerer, venue, price=13, booking_limit_datetime=updated_booking_limit_datetime)
    PcObject.check_and_save(stock)

    
    data = {    
        "offerId": humanize(stock.offer.id),
        "bookingLimitDatetime": serialize(updated_booking_limit_datetime),
        "price": 666
    } 

    # When
    stock.update_stock(data)
    
    # Then
    db.session.refresh(stock)
    assert stock.price == 666
    assert stock.bookingLimitDatetime == updated_booking_limit_datetime

