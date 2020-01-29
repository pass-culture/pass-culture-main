from datetime import datetime
from unittest.mock import patch, MagicMock, call

from freezegun import freeze_time

from repository import repository
from scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer, \
    batch_indexing_offers_in_algolia_by_venue, \
    batch_indexing_offers_in_algolia_from_database, batch_indexing_offers_in_algolia_by_venue_provider, \
    batch_deleting_expired_offers_in_algolia
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_event_product, create_offer_with_thing_product, \
    create_stock_from_offer


class BatchIndexingOffersInAlgoliaByOfferTest:
    @patch('scripts.algolia_indexing.indexing.add_offer_ids_to_set')
    @patch('scripts.algolia_indexing.indexing.delete_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.get_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.delete_offer_ids')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    @patch('scripts.algolia_indexing.indexing.get_offer_ids')
    def test_should_trigger_indexing_using_offer_ids_from_redis(self,
                                                                mock_get_offer_ids,
                                                                mock_orchestrate_from_offer,
                                                                mock_delete_offer_ids,
                                                                mock_get_offer_ids_from_set,
                                                                mock_delete_offer_ids_from_set,
                                                                mock_add_offer_ids_to_set):
        # Given
        client = MagicMock()
        mock_get_offer_ids.return_value = [1, 2, 3, 4]
        mock_get_offer_ids_from_set.return_value = {3, 4}
        mock_orchestrate_from_offer.return_value = [1, 2], [3, 4]

        # When
        batch_indexing_offers_in_algolia_by_offer(client=client)

        # Then
        mock_get_offer_ids.assert_called_once()
        mock_get_offer_ids_from_set.assert_called_once()
        assert mock_orchestrate_from_offer.call_args_list == [
            call(offer_ids=[1, 2, 3, 4], indexed_offer_ids={3, 4})
        ]
        assert mock_add_offer_ids_to_set.call_args_list == [
            call(client=client, offer_ids=[1, 2])
        ]
        assert mock_delete_offer_ids_from_set.call_args_list == [
            call(client=client, offer_ids=[3, 4])
        ]
        mock_delete_offer_ids.assert_called_once()


class BatchIndexingOffersInAlgoliaFromDatabaseTest:
    @patch('scripts.algolia_indexing.indexing.delete_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.add_offer_ids_to_set')
    @patch('scripts.algolia_indexing.indexing.get_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    @clean_database
    def test_should_index_offers_one_time_when_offers_per_page_is_one_and_only_one_page(self,
                                                                                        mock_orchestrate_from_offer,
                                                                                        mock_get_offer_ids_from_set,
                                                                                        mock_add_offer_ids_to_set,
                                                                                        mock_delete_offer_ids_from_set,
                                                                                        app):
        # Given
        client = MagicMock()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(is_active=True, venue=venue)
        repository.save(offer)
        mock_get_offer_ids_from_set.return_value = {}
        mock_orchestrate_from_offer.side_effect = [
            [[offer.id], []],
        ]

        # When
        batch_indexing_offers_in_algolia_from_database(client=client, limit=1, page=0)

        # Then
        mock_orchestrate_from_offer.assert_called_once()
        assert mock_orchestrate_from_offer.call_args_list == [
            call(offer_ids=[offer.id], indexed_offer_ids={}),
        ]
        mock_add_offer_ids_to_set.assert_called_once()
        assert mock_add_offer_ids_to_set.call_args_list == [
            call(client=client, offer_ids=[offer.id]),
        ]
        mock_delete_offer_ids_from_set.assert_not_called()

    @patch('scripts.algolia_indexing.indexing.delete_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.add_offer_ids_to_set')
    @patch('scripts.algolia_indexing.indexing.get_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    @clean_database
    def test_should_index_offers_two_times_when_offers_per_page_is_one_and_two_pages(self,
                                                                                     mock_orchestrate_from_offer,
                                                                                     mock_get_offer_ids_from_set,
                                                                                     mock_add_offer_ids_to_set,
                                                                                     mock_delete_offer_ids_from_set,
                                                                                     app):
        # Given
        client = MagicMock()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        repository.save(offer1, offer2)
        mock_get_offer_ids_from_set.return_value = {}
        mock_orchestrate_from_offer.side_effect = [
            [[offer1.id], []],
            [[], [offer2.id]],
        ]

        # When
        batch_indexing_offers_in_algolia_from_database(client=client, limit=1, page=0)

        # Then
        assert mock_orchestrate_from_offer.call_count == 2
        assert mock_orchestrate_from_offer.call_args_list == [
            call(offer_ids=[offer1.id], indexed_offer_ids={}),
            call(offer_ids=[offer2.id], indexed_offer_ids={})
        ]
        mock_add_offer_ids_to_set.assert_called_once()
        assert mock_add_offer_ids_to_set.call_args_list == [
            call(client=client, offer_ids=[offer1.id]),
        ]
        mock_delete_offer_ids_from_set.assert_called_once()


class BatchIndexingOffersInAlgoliaByVenueProviderTest:
    @patch('scripts.algolia_indexing.indexing.delete_venue_providers')
    @patch('scripts.algolia_indexing.indexing.delete_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.add_offer_ids_to_set')
    @patch('scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 3)
    @patch('scripts.algolia_indexing.indexing.get_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_venue_provider')
    @patch('scripts.algolia_indexing.indexing.get_venue_providers')
    def test_should_trigger_indexing_using_venue_providers_from_redis(self,
                                                                      mock_get_venue_providers,
                                                                      mock_orchestrate_from_venue_provider,
                                                                      mock_get_paginated_offer_ids,
                                                                      mock_get_offer_ids_from_set,
                                                                      mock_add_offer_ids_to_set,
                                                                      mock_delete_offer_ids_from_set,
                                                                      mock_delete_venue_providers):
        # Given
        client = MagicMock()
        mock_get_venue_providers.return_value = [
            {'id': 1, 'providerId': 2, 'venueId': 5},
            {'id': 2, 'providerId': 6, 'venueId': 7}
        ]
        mock_get_offer_ids_from_set.return_value = {1, 2, 3}
        mock_get_paginated_offer_ids.side_effect = [
            [(1,), (2,), (3,)],
            [(4,)],
            [],
            [(5,), (6,), (7,)],
            [(8,)],
            []
        ]
        mock_orchestrate_from_venue_provider.side_effect = [
            [[1, 2, 3], []],
            [[4], []],
            [[5, 6, 7], []],
            [[8], []],
        ]

        # When
        batch_indexing_offers_in_algolia_by_venue_provider(client=client)

        # Then
        mock_get_venue_providers.assert_called_once()
        mock_get_offer_ids_from_set.assert_called_once()
        assert mock_get_paginated_offer_ids.call_count == 6
        assert mock_orchestrate_from_venue_provider.call_count == 4
        assert mock_orchestrate_from_venue_provider.call_args_list == [
            call(indexed_offer_ids={1, 2, 3}, offer_ids=[1, 2, 3]),
            call(indexed_offer_ids={1, 2, 3}, offer_ids=[4]),
            call(indexed_offer_ids={1, 2, 3}, offer_ids=[5, 6, 7]),
            call(indexed_offer_ids={1, 2, 3}, offer_ids=[8])
        ]
        assert mock_add_offer_ids_to_set.call_count == 4
        assert mock_add_offer_ids_to_set.call_args_list == [
            call(client=client, offer_ids=[1, 2, 3]),
            call(client=client, offer_ids=[4]),
            call(client=client, offer_ids=[5, 6, 7]),
            call(client=client, offer_ids=[8]),
        ]
        mock_delete_offer_ids_from_set.assert_not_called()
        mock_delete_venue_providers.assert_called_once()


class BatchIndexingOffersInAlgoliaByVenueTest:
    @patch('scripts.algolia_indexing.indexing.delete_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.add_offer_ids_to_set')
    @patch('scripts.algolia_indexing.indexing.get_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE', 1)
    @patch('scripts.algolia_indexing.indexing.delete_venue_ids')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_offer')
    @patch('scripts.algolia_indexing.indexing.get_venue_ids')
    @clean_database
    def test_should_index_each_offer_of_each_venue(self,
                                                   mock_get_venue_ids,
                                                   mock_orchestrate_from_offer,
                                                   mock_delete_venue_ids,
                                                   mock_get_offer_ids_from_set,
                                                   mock_add_offer_ids_to_set,
                                                   mock_delete_offer_ids_from_set,
                                                   app):
        # Given
        client = MagicMock()
        offerer = create_offerer()
        venue1 = create_venue(offerer=offerer, idx=666)
        venue2 = create_venue(offerer=offerer, idx=13, siret='123654987')
        offer1 = create_offer_with_event_product(venue=venue1)
        offer2 = create_offer_with_event_product(venue=venue2)
        offer3 = create_offer_with_event_product(venue=venue2)
        repository.save(offer1, offer2, offer3)
        mock_get_venue_ids.return_value = [13, 666]
        mock_get_offer_ids_from_set.return_value = {1, 2, 3}
        mock_orchestrate_from_offer.side_effect = [
            [[offer1.id], []],
            [[offer2.id], []],
            [[offer3.id], [4]],
        ]

        # When
        batch_indexing_offers_in_algolia_by_venue(client=client)

        # Then
        assert mock_orchestrate_from_offer.call_count == 3
        assert mock_orchestrate_from_offer.call_args_list == [
            call(indexed_offer_ids={1, 2, 3}, offer_ids=[offer2.id]),
            call(indexed_offer_ids={1, 2, 3}, offer_ids=[offer3.id]),
            call(indexed_offer_ids={1, 2, 3}, offer_ids=[offer1.id])
        ]
        assert mock_add_offer_ids_to_set.call_count == 3
        assert mock_add_offer_ids_to_set.call_args_list == [
            call(client=client, offer_ids=[offer1.id]),
            call(client=client, offer_ids=[offer2.id]),
            call(client=client, offer_ids=[offer3.id])
        ]
        assert mock_delete_offer_ids_from_set.call_count == 1
        assert mock_delete_offer_ids_from_set.call_args_list == [
            call(client=client, offer_ids=[4])
        ]
        assert mock_delete_venue_ids.call_count == 1


@freeze_time('2020-01-01 10:00:00')
class BatchDeletingExpiredOffersInAlgoliaTest:
    @patch('scripts.algolia_indexing.indexing.delete_offer_ids_from_set')
    @patch('scripts.algolia_indexing.indexing.ALGOLIA_DELETING_OFFERS_CHUNK_SIZE', 1)
    @patch('scripts.algolia_indexing.indexing.orchestrate_delete_expired_offers')
    @clean_database
    def test_should_delete_expired_offers_in_a_paginated_way(self,
                                                             mock_orchestrate_delete_expired_offers,
                                                             mock_delete_offer_ids_from_set,
                                                             app):
        # Given
        client = MagicMock()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=True, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=True, venue=venue)
        stock1 = create_stock_from_offer(booking_limit_datetime=datetime(2019, 12, 21, 0, 0, 0), offer=offer1)
        stock2 = create_stock_from_offer(booking_limit_datetime=datetime(2019, 12, 22, 0, 0, 0), offer=offer2)
        stock3 = create_stock_from_offer(booking_limit_datetime=datetime(2019, 12, 23, 0, 0, 0), offer=offer3)
        stock4 = create_stock_from_offer(booking_limit_datetime=datetime(2019, 12, 24, 0, 0, 0), offer=offer4)
        repository.save(stock1, stock2, stock3, stock4)

        # When
        batch_deleting_expired_offers_in_algolia(client=client)

        # Then
        assert mock_orchestrate_delete_expired_offers.call_count == 4
        assert mock_orchestrate_delete_expired_offers.call_args_list == [
            call(offer_ids=[offer1.id]),
            call(offer_ids=[offer2.id]),
            call(offer_ids=[offer3.id]),
            call(offer_ids=[offer4.id])
        ]
        assert mock_delete_offer_ids_from_set.call_args_list == [
            call(client=client, offer_ids=[offer1.id]),
            call(client=client, offer_ids=[offer2.id]),
            call(client=client, offer_ids=[offer3.id]),
            call(client=client, offer_ids=[offer4.id]),
        ]
