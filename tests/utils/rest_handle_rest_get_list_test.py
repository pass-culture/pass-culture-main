import pytest

from models import ApiErrors, StockSQLEntity
from repository import repository
import pytest
from model_creators.generic_creators import create_offerer, create_venue
from model_creators.specific_creators import create_stock_from_event_occurrence, create_offer_with_event_product, \
    create_event_occurrence
from utils.human_ids import humanize
from utils.rest import handle_rest_get_list


class HandleRestGetListTest:
    @pytest.mark.usefixtures("db_session")
    def test_return_only_not_soft_deleted_stock(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer)
        stock1 = create_stock_from_event_occurrence(event_occurrence)
        stock2 = create_stock_from_event_occurrence(event_occurrence)
        stock3 = create_stock_from_event_occurrence(event_occurrence)
        stock4 = create_stock_from_event_occurrence(event_occurrence)
        stock1.isSoftDeleted = True
        repository.save(stock1, stock2, stock3, stock4)

        # When
        request = handle_rest_get_list(StockSQLEntity)

        # Then
        assert '"id":"{}"'.format(humanize(stock1.id)) not in str(request[0].response)
        assert '"id":"{}"'.format(humanize(stock2.id)) in str(request[0].response)
        assert '"id":"{}"'.format(humanize(stock3.id)) in str(request[0].response)
        assert '"id":"{}"'.format(humanize(stock4.id)) in str(request[0].response)

    @pytest.mark.usefixtures("db_session")
    def test_check_order_by(self, app):
        # When
        with pytest.raises(ApiErrors) as e:
            handle_rest_get_list(StockSQLEntity, order_by='(SELECT * FROM "user")')

        # Then
        assert 'order_by' in e.value.errors
