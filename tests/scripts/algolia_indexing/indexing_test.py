from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

from freezegun import freeze_time

from pcapi.scripts.algolia_indexing.indexing import _process_venue_provider
from pcapi.scripts.algolia_indexing.indexing import batch_deleting_expired_offers_in_algolia
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_venue
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_venue_provider
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database
from pcapi.scripts.algolia_indexing.indexing import batch_processing_offer_ids_in_error


class BatchIndexingOffersInAlgoliaByOfferTest:
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_offer_ids')
    @patch('pcapi.scripts.algolia_indexing.indexing.get_offer_ids')
    def test_should_index_offers_when_at_least_one_offer_id(self,
                                                            mock_get_offer_ids,
                                                            mock_delete_offer_ids,
                                                            mock_process_eligible_offers):
        # Given
        client = MagicMock()
        mock_get_offer_ids.return_value = [1]

        # When
        batch_indexing_offers_in_algolia_by_offer(client=client)

        # Then
        mock_get_offer_ids.assert_called_once()
        mock_delete_offer_ids.assert_called_once()
        assert mock_process_eligible_offers.call_args_list == [
            call(client=client, offer_ids=[1], from_provider_update=False)
        ]

    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_offer_ids')
    @patch('pcapi.scripts.algolia_indexing.indexing.get_offer_ids')
    def test_should_not_trigger_indexing_when_no_offer_id(self,
                                                          mock_get_offer_ids,
                                                          mock_delete_offer_ids,
                                                          mock_process_eligible_offers):
        # Given
        client = MagicMock()
        mock_get_offer_ids.return_value = []

        # When
        batch_indexing_offers_in_algolia_by_offer(client=client)

        # Then
        mock_get_offer_ids.assert_called_once()
        mock_delete_offer_ids.assert_not_called()
        mock_process_eligible_offers.assert_not_called()


class BatchIndexingOffersInAlgoliaByVenueProviderTest:
    @patch('pcapi.scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 3)
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_venue_providers')
    @patch('pcapi.scripts.algolia_indexing.indexing.get_venue_providers')
    def test_should_index_offers_when_at_least_one_venue_provider(self,
                                                                  mock_get_venue_providers,
                                                                  mock_delete_venue_providers,
                                                                  mock_process_eligible_offers,
                                                                  mock_get_paginated_offer_ids):
        # Given
        client = MagicMock()
        mock_get_venue_providers.return_value = [
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
        mock_get_venue_providers.assert_called_once()
        mock_delete_venue_providers.assert_called_once()
        assert mock_get_paginated_offer_ids.call_count == 6
        assert mock_process_eligible_offers.call_count == 4
        assert mock_process_eligible_offers.call_args_list == [
            call(client=client, from_provider_update=True, offer_ids=[1, 2, 3]),
            call(client=client, from_provider_update=True, offer_ids=[4]),
            call(client=client, from_provider_update=True, offer_ids=[5, 6, 7]),
            call(client=client, from_provider_update=True, offer_ids=[8])
        ]

    @patch('pcapi.scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 3)
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_venue_providers')
    @patch('pcapi.scripts.algolia_indexing.indexing.get_venue_providers')
    def test_should_not_trigger_indexing_when_no_venue_providers(self,
                                                                 mock_get_venue_providers,
                                                                 mock_delete_venue_providers,
                                                                 mock_process_eligible_offers,
                                                                 mock_get_paginated_offer_ids):
        # Given
        client = MagicMock()
        mock_get_venue_providers.return_value = []

        # When
        batch_indexing_offers_in_algolia_by_venue_provider(client=client)

        # Then
        mock_get_venue_providers.assert_called_once()
        mock_delete_venue_providers.assert_not_called()
        mock_get_paginated_offer_ids.assert_not_called()
        mock_process_eligible_offers.assert_not_called()


class BatchIndexingOffersInAlgoliaByVenueTest:
    @patch('pcapi.scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE', 1)
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_venue_ids')
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    @patch('pcapi.scripts.algolia_indexing.indexing.get_venue_ids')
    def test_should_index_offers_when_at_least_one_venue(self,
                                                         mock_get_venue_ids,
                                                         mock_process_eligible_offers,
                                                         mock_get_paginated_offer_ids_by_venue_id,
                                                         mock_delete_venue_ids,
                                                         app):
        # Given
        client = MagicMock()
        mock_get_venue_ids.return_value = [10]
        mock_get_paginated_offer_ids_by_venue_id.side_effect = [
            [(1,), (2,)],
            []
        ]

        # When
        batch_indexing_offers_in_algolia_by_venue(client=client)

        # Then
        assert mock_get_paginated_offer_ids_by_venue_id.call_count == 2
        assert mock_process_eligible_offers.call_count == 1
        assert mock_process_eligible_offers.call_args_list == [
            call(client=client, offer_ids=[1, 2], from_provider_update=False)
        ]
        assert mock_delete_venue_ids.call_count == 1

    @patch('pcapi.scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE', 1)
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_venue_ids')
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    @patch('pcapi.scripts.algolia_indexing.indexing.get_venue_ids')
    def test_should_not_trigger_indexing_when_no_venue(self,
                                                       mock_get_venue_ids,
                                                       mock_process_eligible_offers,
                                                       mock_get_paginated_offer_ids_by_venue_id,
                                                       mock_delete_venue_ids,
                                                       app):
        # Given
        client = MagicMock()
        mock_get_venue_ids.return_value = []

        # When
        batch_indexing_offers_in_algolia_by_venue(client=client)

        # Then
        mock_get_paginated_offer_ids_by_venue_id.assert_not_called()
        mock_process_eligible_offers.assert_not_called()
        mock_delete_venue_ids.assert_not_called()


class BatchIndexingOffersInAlgoliaFromDatabaseTest:
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_active_offer_ids')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    def test_should_index_offers_once_when_offers_per_page_is_one_and_only_one_page(self,
                                                                                    mock_process_eligible_offers,
                                                                                    mock_get_paginated_active_offer_ids,
                                                                                    app):
        # Given
        client = MagicMock()
        mock_get_paginated_active_offer_ids.side_effect = [
            [(1,)],
            []
        ]

        # When
        batch_indexing_offers_in_algolia_from_database(client=client, ending_page=None, limit=1, starting_page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 2
        assert mock_process_eligible_offers.call_count == 1
        assert mock_process_eligible_offers.call_args_list == [
            call(client=client, offer_ids=[1], from_provider_update=False)
        ]

    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_active_offer_ids')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    def test_should_index_offers_twice_when_offers_per_page_is_one_and_two_pages(self,
                                                                                 mock_process_eligible_offers,
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
        batch_indexing_offers_in_algolia_from_database(client=client, ending_page=None, limit=1, starting_page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 3
        assert mock_process_eligible_offers.call_count == 2
        assert mock_process_eligible_offers.call_args_list == [
            call(client=client, offer_ids=[1], from_provider_update=False),
            call(client=client, offer_ids=[2], from_provider_update=False)
        ]

    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_active_offer_ids')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    def test_should_index_offers_from_first_page_only_when_ending_page_is_provided(self,
                                                                                   mock_process_eligible_offers,
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
        batch_indexing_offers_in_algolia_from_database(client=client, ending_page=1, limit=1, starting_page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 1
        assert mock_process_eligible_offers.call_count == 1
        assert mock_process_eligible_offers.call_args_list == [
            call(client=client, offer_ids=[1], from_provider_update=False),
        ]


@freeze_time('2020-01-01 10:00:00')
class BatchDeletingExpiredOffersInAlgoliaTest:
    @patch('pcapi.scripts.algolia_indexing.indexing.ALGOLIA_DELETING_OFFERS_CHUNK_SIZE', 1)
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_given_booking_limit_datetime_interval')
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_expired_offers')
    def test_should_retrieve_expired_offers_in_two_days_interval_by_default(self,
                                                             mock_delete_expired_offers,
                                                             mock_get_paginated_offer_ids_given_booking_limit_datetime_interval,
                                                             app):
        # Given
        client = MagicMock()

        # When
        batch_deleting_expired_offers_in_algolia(client=client)

        # Then
        assert mock_get_paginated_offer_ids_given_booking_limit_datetime_interval.call_count == 1
        assert mock_get_paginated_offer_ids_given_booking_limit_datetime_interval.call_args_list == [
            call(from_date=datetime(2019, 12, 30, 10, 0, 0), limit=1, page=0, to_date=datetime(2019, 12, 31, 10, 0, 0)),
        ]

    @patch('pcapi.scripts.algolia_indexing.indexing.ALGOLIA_DELETING_OFFERS_CHUNK_SIZE', 1)
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_given_booking_limit_datetime_interval')
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_expired_offers')
    def test_should_retrieve_all_expired_offers_if_requested(self,
                                                             mock_delete_expired_offers,
                                                             mock_get_paginated_offer_ids_given_booking_limit_datetime_interval,
                                                             app):
        # Given
        client = MagicMock()

        # When
        batch_deleting_expired_offers_in_algolia(client=client, process_all_expired=True)

        # Then
        assert mock_get_paginated_offer_ids_given_booking_limit_datetime_interval.call_count == 1
        assert mock_get_paginated_offer_ids_given_booking_limit_datetime_interval.call_args_list == [
            call(from_date=datetime(2000, 1, 1, 0, 0, 0), limit=1, page=0, to_date=datetime(2019, 12, 31, 10, 0, 0)),
        ]

    @patch('pcapi.scripts.algolia_indexing.indexing.ALGOLIA_DELETING_OFFERS_CHUNK_SIZE', 1)
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_given_booking_limit_datetime_interval')
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_expired_offers')
    def test_should_delete_expired_offers_in_a_paginated_way(self,
                                                             mock_delete_expired_offers,
                                                             mock_get_paginated_offer_ids_given_booking_limit_datetime_interval,
                                                             app):
        # Given
        client = MagicMock()
        mock_get_paginated_offer_ids_given_booking_limit_datetime_interval.side_effect = [
            [(1,)],
            [(2,)],
            [],
        ]

        # When
        batch_deleting_expired_offers_in_algolia(client=client)

        # Then
        assert mock_delete_expired_offers.call_count == 2


class BatchProcessingOfferIdsInErrorTest:
    @patch('pcapi.scripts.algolia_indexing.indexing.get_offer_ids_in_error')
    def test_should_retrieve_offer_ids_in_error(self, mock_get_offer_ids_in_error):
        # Given
        client = MagicMock()
        mock_get_offer_ids_in_error.return_value = []

        # When
        batch_processing_offer_ids_in_error(client=client)

        # Then
        mock_get_offer_ids_in_error.assert_called_once()

    @patch('pcapi.scripts.algolia_indexing.indexing.delete_offer_ids_in_error')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    @patch('pcapi.scripts.algolia_indexing.indexing.get_offer_ids_in_error')
    def test_should_delete_offer_ids_in_error_when_at_least_one_offer_id(self,
                                                                         mock_get_offer_ids_in_error,
                                                                         mock_process_eligible_offers,
                                                                         mock_delete_offer_ids_in_error):
        # Given
        client = MagicMock()
        mock_get_offer_ids_in_error.return_value = [1]

        # When
        batch_processing_offer_ids_in_error(client=client)

        # Then
        mock_get_offer_ids_in_error.assert_called_once_with(client=client)
        mock_process_eligible_offers.assert_called_once_with(client=client, offer_ids=[1], from_provider_update=False)
        mock_delete_offer_ids_in_error.assert_called_once_with(client=client)

    @patch('pcapi.scripts.algolia_indexing.indexing.delete_offer_ids_in_error')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    @patch('pcapi.scripts.algolia_indexing.indexing.get_offer_ids_in_error')
    def test_should_not_delete_offer_ids_in_error_when_no_offer_id(self,
                                                                   mock_get_offer_ids_in_error,
                                                                   mock_process_eligible_offers,
                                                                   mock_delete_offer_ids_in_error):
        # Given
        client = MagicMock()
        mock_get_offer_ids_in_error.return_value = []

        # When
        batch_processing_offer_ids_in_error(client=client)

        # Then
        mock_get_offer_ids_in_error.assert_called_once_with(client=client)
        mock_delete_offer_ids_in_error.assert_not_called()
        mock_process_eligible_offers.assert_not_called()


class ProcessVenueProviderTest:
    @patch('pcapi.scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 3)
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_venue_provider_currently_in_sync')
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id')
    @patch('pcapi.scripts.algolia_indexing.indexing.process_eligible_offers')
    def test_should_index_offers_when_at_least_one_venue_provider(self,
                                                                  mock_process_eligible_offers,
                                                                  mock_get_paginated_offer_ids,
                                                                  mock_delete_venue_provider_currently_in_sync):
        # Given
        client = MagicMock()
        mock_get_paginated_offer_ids.side_effect = [
            [(1,), (2,), (3,)],
            [(4,)],
            [],
        ]

        # When
        _process_venue_provider(client=client, venue_provider_id=1, provider_id='2', venue_id=5)

        # Then
        assert mock_get_paginated_offer_ids.call_count == 3
        assert mock_process_eligible_offers.call_count == 2
        assert mock_process_eligible_offers.call_args_list == [
            call(client=client, offer_ids=[1, 2, 3], from_provider_update=True),
            call(client=client, offer_ids=[4], from_provider_update=True),
        ]
        mock_delete_venue_provider_currently_in_sync.assert_called_once_with(
            client=client,
            venue_provider_id=1
        )

    @patch('pcapi.scripts.algolia_indexing.indexing.ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 3)
    @patch('pcapi.scripts.algolia_indexing.indexing.delete_venue_provider_currently_in_sync')
    @patch('pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id',
           return_value=Exception)
    def test_should_delete_venue_provider_currently_in_sync_when_exception_is_raised(self,
                                                                                     mock_get_paginated_offer_ids,
                                                                                     mock_delete_venue_provider_currently_in_sync):
        # Given
        client = MagicMock()

        # When
        _process_venue_provider(client=client, venue_provider_id=1, provider_id='2', venue_id=5)

        # Then
        assert mock_get_paginated_offer_ids.call_count == 1
        mock_delete_venue_provider_currently_in_sync.assert_called_once_with(
            client=client,
            venue_provider_id=1
        )
