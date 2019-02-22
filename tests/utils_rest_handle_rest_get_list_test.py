import pytest

from models import Stock, PcObject
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.rest import handle_rest_get_list
from tests.test_utils import create_stock_from_event_occurrence, create_offerer, create_event_occurrence, \
    create_event_offer, create_venue


@clean_database
@pytest.mark.standalone
def test_handle_rest_get_list_should_return_only_not_soft_deleted_stock(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    event_occurrence = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(event_occurrence)
    stock2 = create_stock_from_event_occurrence(event_occurrence)
    stock3 = create_stock_from_event_occurrence(event_occurrence)
    stock4 = create_stock_from_event_occurrence(event_occurrence)
    stock1.isSoftDeleted = True
    PcObject.check_and_save(stock1, stock2, stock3, stock4)

    # When
    request = handle_rest_get_list(Stock)
    # Then
    assert '"id":"{}"'.format(humanize(stock1.id)) not in str(request[0].response)
    assert '"id":"{}"'.format(humanize(stock2.id)) in str(request[0].response)
    assert '"id":"{}"'.format(humanize(stock3.id)) in str(request[0].response)
    assert '"id":"{}"'.format(humanize(stock4.id)) in str(request[0].response)