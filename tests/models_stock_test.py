import pytest

from models import Stock, ApiErrors, PcObject
from models.pc_object import DeletedRecordException
from tests.conftest import clean_database
from utils.test_utils import create_stock_with_event_offer, create_offerer, create_venue, create_event_offer, \
    create_event_occurrence, create_stock_from_offer


@clean_database
@pytest.mark.standalone
def test_stock_cannot_have_eventOccurrence_and_offer(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    event_offer = create_event_offer(venue)
    event_occurrence = create_event_occurrence(event_offer)
    stock = Stock()
    stock.offerer = offerer
    stock.price = 0
    stock.eventOccurrence = event_occurrence
    stock.offer = event_offer

    # When
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(stock)


@clean_database
@pytest.mark.standalone
def test_stock_needs_eventOccurrence_or_offer(app):
    # Given
    offerer = create_offerer()
    stock = Stock()
    stock.offerer = offerer
    stock.price = 0

    # When
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(stock)


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
    query = Stock.queryNotSoftDeleted().all()

    print(query)

    # Then
    assert len(query) == 0


@clean_database
@pytest.mark.standalone
def test_populate_dict_with_is_soft_deleted_raises_DeletedRecordException(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_from_offer(offerer, create_offer)
    # When
    with pytest.raises(DeletedRecordException):
        stock.populateFromDict({"isSoftDeleted": True})
