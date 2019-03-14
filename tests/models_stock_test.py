from datetime import datetime, timedelta
import pytest
from sqlalchemy.exc import InternalError

from models import Stock, ApiErrors, PcObject
from models.pc_object import DeletedRecordException
from tests.conftest import clean_database
from tests.test_utils import create_stock_with_event_offer, create_offerer, create_venue, create_event_offer, \
    create_stock_from_offer, create_thing_offer, create_booking, create_user, create_stock


@pytest.mark.standalone
@clean_database
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
    with pytest.raises(InternalError):
        PcObject.check_and_save(stock)
