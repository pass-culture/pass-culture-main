from unittest.mock import patch, MagicMock

from models import PcObject
from scripts.algolia_indexing.indexing import indexing_offers_in_algolia, batch_indexing_offers
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer, create_venue, \
    create_stock
from tests.model_creators.specific_creators import create_offer_with_event_product


@patch('scripts.algolia_indexing.indexing.delete_offer_ids')
@patch('scripts.algolia_indexing.indexing.orchestrate')
@patch('scripts.algolia_indexing.indexing.get_offer_ids', return_value=[1, 2, 3])
def test_should_trigger_indexing_using_offer_ids_from_redis(mock_get_offer_ids,
                                                            mock_orchestrate,
                                                            mock_delete_offer_ids):
    # Given
    client = MagicMock()

    # When
    indexing_offers_in_algolia(client=client)

    # Then
    mock_get_offer_ids.assert_called_once()
    mock_orchestrate.assert_called_once_with([1, 2, 3])
    mock_delete_offer_ids.assert_called_once()


class BatchIndexingOffersTest:
    @patch('scripts.algolia_indexing.indexing.orchestrate')
    @clean_database
    def test_should_index_offers_one_time_when_elements_per_page_is_one_and_only_one_page(self, mock_orchestrate, app):
        # Given
        user = create_user(email='admin@example.com')
        offerer = create_offerer()
        user_offerer = create_user_offerer(offerer=offerer, user=user)
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(venue=venue, event_name='Super événement du pass culture')
        stock = create_stock(offer=offer)
        PcObject.save(user_offerer, stock)

        # When
        batch_indexing_offers(limit=1)

        # Then
        count = mock_orchestrate.call_count
        assert count == 1

    @patch('scripts.algolia_indexing.indexing.orchestrate')
    @clean_database
    def test_should_index_offers_two_times_when_elements_per_page_is_one_and_two_pages(self, mock_orchestrate, app):
        # Given
        user = create_user(email='admin@example.com')
        offerer = create_offerer()
        user_offerer = create_user_offerer(offerer=offerer, user=user)
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(venue=venue, event_name='Super événement du pass culture')
        stock1 = create_stock(offer=offer1)
        offer2 = create_offer_with_event_product(venue=venue, event_name='Super événement du pass culture')
        stock2 = create_stock(offer=offer2)
        PcObject.save(user_offerer, stock1, stock2)

        # When
        batch_indexing_offers(limit=1)

        # Then
        count = mock_orchestrate.call_count
        assert count == 2
