from unittest.mock import patch, MagicMock, call

from scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer, \
    batch_indexing_offers_in_algolia_by_venue, \
    batch_indexing_offers_in_algolia_from_database, batch_indexing_offers_in_algolia_by_venue_provider, \
    batch_deleting_expired_offers_in_algolia


class BatchIndexingOffersInAlgoliaByOfferTest:
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    @patch('scripts.algolia_indexing.indexing.get_offer_ids_from_list')
    def test_should_index_offers_when_at_least_one_offer_id(self,
                                                            mock_get_offer_ids_from_list,
                                                            mock_orchestrate_from_offer):
        # Given
        client = MagicMock()
        mock_get_offer_ids_from_list.return_value = [1]

        # When
        batch_indexing_offers_in_algolia_by_offer(client=client)

        # Then
        mock_get_offer_ids_from_list.assert_called_once()
        assert mock_orchestrate_from_offer.call_args_list == [
            call(client=client, offer_ids=[1])
        ]

    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    @patch('scripts.algolia_indexing.indexing.get_offer_ids_from_list')
    def test_should_not_trigger_indexing_when_no_offer_id(self,
                                                          mock_get_offer_ids_from_list,
                                                          mock_orchestrate_from_offer):
        # Given
        client = MagicMock()
        mock_get_offer_ids_from_list.return_value = []

        # When
        batch_indexing_offers_in_algolia_by_offer(client=client)

        # Then
        mock_get_offer_ids_from_list.assert_called_once()
        mock_orchestrate_from_offer.assert_not_called()


class BatchIndexingOffersInAlgoliaByVenueProviderTest:
    @patch('scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 3)
    @patch('scripts.algolia_indexing.indexing.delete_venue_providers_from_list')
    @patch('scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_venue_provider')
    @patch('scripts.algolia_indexing.indexing.get_venue_providers_from_list')
    def test_should_index_offers_when_at_least_one_venue_providers(self,
                                                                   mock_get_venue_providers_from_list,
                                                                   mock_orchestrate_from_venue_provider,
                                                                   mock_get_paginated_offer_ids,
                                                                   mock_delete_venue_providers_from_list):
        # Given
        client = MagicMock()
        mock_get_venue_providers_from_list.return_value = [
            {'id': 1, 'providerId': 2, 'venueId': 5},
            {'id': 2, 'providerId': 6, 'venueId': 7}
        ]
        mock_get_paginated_offer_ids.side_effect = [
            [(1,), (2,), (3,)],
            [(4,)],
            [],
            [(5,), (6,), (7,)],
            [(8,)],
            []
        ]

        # When
        batch_indexing_offers_in_algolia_by_venue_provider(client=client)

        # Then
        mock_get_venue_providers_from_list.assert_called_once()
        assert mock_get_paginated_offer_ids.call_count == 6
        assert mock_orchestrate_from_venue_provider.call_count == 4
        assert mock_orchestrate_from_venue_provider.call_args_list == [
            call(client=client, offer_ids=[1, 2, 3]),
            call(client=client, offer_ids=[4]),
            call(client=client, offer_ids=[5, 6, 7]),
            call(client=client, offer_ids=[8])
        ]
        mock_delete_venue_providers_from_list.assert_called_once()

    @patch('scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 3)
    @patch('scripts.algolia_indexing.indexing.delete_venue_providers_from_list')
    @patch('scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_venue_provider')
    @patch('scripts.algolia_indexing.indexing.get_venue_providers_from_list')
    def test_should_not_trigger_indexing_when_no_venue_providers(self,
                                                                 mock_get_venue_providers_from_list,
                                                                 mock_orchestrate_from_venue_provider,
                                                                 mock_get_paginated_offer_ids,
                                                                 mock_delete_venue_providers_from_list):
        # Given
        client = MagicMock()
        mock_get_venue_providers_from_list.return_value = []

        # When
        batch_indexing_offers_in_algolia_by_venue_provider(client=client)

        # Then
        mock_get_venue_providers_from_list.assert_called_once()
        mock_get_paginated_offer_ids.assert_not_called()
        mock_orchestrate_from_venue_provider.assert_not_called()
        mock_delete_venue_providers_from_list.assert_not_called()


class BatchIndexingOffersInAlgoliaByVenueTest:
    @patch('scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE', 1)
    @patch('scripts.algolia_indexing.indexing.delete_venue_ids_from_list')
    @patch('scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    @patch('scripts.algolia_indexing.indexing.get_venue_ids_from_list')
    def test_should_index_offers_when_at_least_one_venue(self,
                                                         mock_get_venue_ids_from_list,
                                                         mock_orchestrate_from_offer,
                                                         mock_get_paginated_offer_ids_by_venue_id,
                                                         mock_delete_venue_ids_from_list,
                                                         app):
        # Given
        client = MagicMock()
        mock_get_venue_ids_from_list.return_value = [10]
        mock_get_paginated_offer_ids_by_venue_id.side_effect = [
            [(1,), (2,)],
            []
        ]

        # When
        batch_indexing_offers_in_algolia_by_venue(client=client)

        # Then
        assert mock_get_paginated_offer_ids_by_venue_id.call_count == 2
        assert mock_orchestrate_from_offer.call_count == 1
        assert mock_orchestrate_from_offer.call_args_list == [
            call(client=client, offer_ids=[1, 2])
        ]
        assert mock_delete_venue_ids_from_list.call_count == 1

    @patch('scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE', 1)
    @patch('scripts.algolia_indexing.indexing.delete_venue_ids_from_list')
    @patch('scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    @patch('scripts.algolia_indexing.indexing.get_venue_ids_from_list')
    def test_should_not_trigger_indexing_when_no_venue(self,
                                                       mock_get_venue_ids_from_list,
                                                       mock_orchestrate_from_offer,
                                                       mock_get_paginated_offer_ids_by_venue_id,
                                                       mock_delete_venue_ids_from_list,
                                                       app):
        # Given
        client = MagicMock()
        mock_get_venue_ids_from_list.return_value = []

        # When
        batch_indexing_offers_in_algolia_by_venue(client=client)

        # Then
        mock_get_paginated_offer_ids_by_venue_id.assert_not_called()
        mock_orchestrate_from_offer.assert_not_called()
        mock_delete_venue_ids_from_list.assert_not_called()


class BatchIndexingOffersInAlgoliaFromDatabaseTest:
    @patch('scripts.algolia_indexing.indexing.offer_queries.get_paginated_active_offer_ids')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    def test_should_index_offers_one_time_when_offers_per_page_is_one_and_only_one_page(self,
                                                                                        mock_orchestrate_from_offer,
                                                                                        mock_get_paginated_active_offer_ids,
                                                                                        app):
        # Given
        client = MagicMock()
        mock_get_paginated_active_offer_ids.side_effect = [
            [(1,)],
            []
        ]

        # When
        batch_indexing_offers_in_algolia_from_database(client=client, limit=1, page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 2
        assert mock_orchestrate_from_offer.call_count == 1
        assert mock_orchestrate_from_offer.call_args_list == [
            call(client=client, offer_ids=[1])
        ]

    @patch('scripts.algolia_indexing.indexing.offer_queries.get_paginated_active_offer_ids')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    def test_should_index_offers_two_times_when_offers_per_page_is_one_and_two_pages(self,
                                                                                     mock_orchestrate_from_offer,
                                                                                     mock_get_paginated_active_offer_ids,
                                                                                     app):
        # Given
        client = MagicMock()
        mock_get_paginated_active_offer_ids.side_effect = [
            [(1,)],
            [(2,)],
            []
        ]

        # When
        batch_indexing_offers_in_algolia_from_database(client=client, limit=1, page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 3
        assert mock_orchestrate_from_offer.call_count == 2
        assert mock_orchestrate_from_offer.call_args_list == [
            call(client=client, offer_ids=[1]),
            call(client=client, offer_ids=[2])
        ]


class BatchDeletingExpiredOffersInAlgoliaTest:
    @patch('scripts.algolia_indexing.indexing.ALGOLIA_DELETING_OFFERS_CHUNK_SIZE', 1)
    @patch('scripts.algolia_indexing.indexing.offer_queries.get_paginated_expired_offer_ids')
    @patch('scripts.algolia_indexing.indexing.orchestrate_delete_expired_offers')
    def test_should_delete_expired_offers_in_a_paginated_way(self,
                                                             mock_orchestrate_delete_expired_offers,
                                                             mock_get_paginated_expired_offer_ids,
                                                             app):
        # Given
        client = MagicMock()
        mock_get_paginated_expired_offer_ids.side_effect = [
            [(1,)],
            [(2,)],
            [],
        ]

        # When
        batch_deleting_expired_offers_in_algolia(client=client)

        # Then
        assert mock_orchestrate_delete_expired_offers.call_count == 2
