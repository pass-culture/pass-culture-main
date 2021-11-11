from unittest import mock

from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database


# FIXME (dbaty, 2021-06-25): review these tests (remove mock of database queries)
class BatchIndexingOffersInAlgoliaFromDatabaseTest:
    @mock.patch("pcapi.repository.offer_queries.get_paginated_active_offer_ids")
    @mock.patch("pcapi.core.search.reindex_offer_ids")
    def test_should_index_offers_once_when_offers_per_page_is_one_and_only_one_page(
        self, mock_reindex_offer_ids, mock_get_paginated_active_offer_ids
    ):
        # Given
        mock_get_paginated_active_offer_ids.side_effect = [[1], []]

        # When
        batch_indexing_offers_in_algolia_from_database(ending_page=None, limit=1, starting_page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 2
        mock_reindex_offer_ids.assert_called_once_with([1])

    @mock.patch("pcapi.repository.offer_queries.get_paginated_active_offer_ids")
    @mock.patch("pcapi.core.search.reindex_offer_ids")
    def test_should_index_offers_twice_when_offers_per_page_is_one_and_two_pages(
        self, mock_reindex_offer_ids, mock_get_paginated_active_offer_ids
    ):
        # Given
        mock_get_paginated_active_offer_ids.side_effect = [[1], [2], []]

        # When
        batch_indexing_offers_in_algolia_from_database(ending_page=None, limit=1, starting_page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 3
        assert mock_reindex_offer_ids.call_args_list == [
            mock.call([1]),
            mock.call([2]),
        ]

    @mock.patch("pcapi.repository.offer_queries.get_paginated_active_offer_ids")
    @mock.patch("pcapi.core.search.reindex_offer_ids")
    def test_should_index_offers_from_first_page_only_when_ending_page_is_provided(
        self, mock_reindex_offer_ids, mock_get_paginated_active_offer_ids
    ):
        # Given
        mock_get_paginated_active_offer_ids.side_effect = [[1], [2], []]

        # When
        batch_indexing_offers_in_algolia_from_database(ending_page=1, limit=1, starting_page=0)

        # Then
        mock_reindex_offer_ids.assert_called_once_with([1])
