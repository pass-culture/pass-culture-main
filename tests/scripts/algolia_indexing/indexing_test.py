from unittest.mock import patch

from scripts.algolia_indexing.indexing import index_offers


@patch('scripts.algolia_indexing.indexing.delete_offer_ids')
@patch('scripts.algolia_indexing.indexing.orchestrate')
@patch('scripts.algolia_indexing.indexing.get_offer_ids', return_value=[1, 2, 3])
def test_should_trigger_indexing_using_offer_ids_from_redis(mock_get_offer_ids,
                                                            mock_orchestrate,
                                                            mock_delete_offer_ids):
    # When
    index_offers()

    # Then
    mock_get_offer_ids.assert_called_once()
    mock_orchestrate.assert_called_once_with([1, 2, 3])
    mock_delete_offer_ids.assert_called_once()
