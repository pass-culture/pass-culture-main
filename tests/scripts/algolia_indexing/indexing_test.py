from datetime import datetime
from unittest import mock

from freezegun import freeze_time
import pytest
import redis

import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_settings
from pcapi.scripts.algolia_indexing.indexing import batch_deleting_expired_offers_in_algolia
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_venue
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database
from pcapi.scripts.algolia_indexing.indexing import batch_processing_offer_ids_in_error


# FIXME (dbaty, 2021-04-28): the lack of Redis in tests makes these
# tests painful to write and read.
@override_settings(REDIS_OFFER_IDS_CHUNK_SIZE=3)
@mock.patch("pcapi.scripts.algolia_indexing.indexing.process_eligible_offers")
class BatchIndexingOffersInAlgoliaByOfferTest:
    def test_cron_behaviour(self, mocked_process_eligible_offers):
        queue = list(range(1, 9))  # 8 items: 1..8

        def fake_pop(client):
            popped = []
            for _i in range(3):  # overriden REDIS_OFFER_IDS_CHUNK_SIZE
                try:
                    popped.append(queue.pop(0))
                except IndexError:  # queue is empty
                    break
            return popped

        def fake_len(self, queue_name):
            return len(queue)

        redis_client = redis.Redis()
        with mock.patch("pcapi.scripts.algolia_indexing.indexing.pop_offer_ids", fake_pop):
            with mock.patch("redis.Redis.llen", fake_len):
                batch_indexing_offers_in_algolia_by_offer(redis_client)

        # First run pops and indexes 1, 2, 3. Second run pops and
        # indexes 4, 5, 6. And stops because there are less than
        # REDIS_OFFER_IDS_CHUNK_SIZE items left in the queue.
        assert mocked_process_eligible_offers.mock_calls == [
            mock.call(
                client=redis_client,
                offer_ids=[1, 2, 3],
                from_provider_update=False,
            ),
            mock.call(
                client=redis_client,
                offer_ids=[4, 5, 6],
                from_provider_update=False,
            ),
        ]
        assert queue == [7, 8]

    def test_command_behaviour(self, mocked_process_eligible_offers):
        queue = list(range(1, 9))  # 8 items: 1..8

        def fake_pop(client):
            popped = []
            for _i in range(3):  # overriden REDIS_OFFER_IDS_CHUNK_SIZE
                try:
                    popped.append(queue.pop(0))
                except IndexError:  # queue is empty
                    break
            return popped

        def fake_len(self, queue_name):
            return len(queue)

        redis_client = redis.Redis()
        with mock.patch("pcapi.scripts.algolia_indexing.indexing.pop_offer_ids", fake_pop):
            with mock.patch("redis.Redis.llen", fake_len):
                batch_indexing_offers_in_algolia_by_offer(redis_client, stop_only_when_empty=True)

        # First run pops and indexes 1, 2, 3. Second run pops and
        # indexes 4, 5, 6. Third run pops 7, 8 and stop because the
        # queue is empty.
        assert mocked_process_eligible_offers.mock_calls == [
            mock.call(
                client=redis_client,
                offer_ids=[1, 2, 3],
                from_provider_update=False,
            ),
            mock.call(
                client=redis_client,
                offer_ids=[4, 5, 6],
                from_provider_update=False,
            ),
            mock.call(
                client=redis_client,
                offer_ids=[7, 8],
                from_provider_update=False,
            ),
        ]
        assert queue == []


class BatchIndexingOffersInAlgoliaByVenueTest:
    @mock.patch("pcapi.settings.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE", 1)
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.delete_venue_ids")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.process_eligible_offers")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.get_venue_ids")
    def test_should_index_offers_when_at_least_one_venue(
        self,
        mock_get_venue_ids,
        mock_process_eligible_offers,
        mock_get_paginated_offer_ids_by_venue_id,
        mock_delete_venue_ids,
        app,
    ):
        # Given
        client = mock.MagicMock()
        mock_get_venue_ids.return_value = [10]
        mock_get_paginated_offer_ids_by_venue_id.side_effect = [[(1,), (2,)], []]

        # When
        batch_indexing_offers_in_algolia_by_venue(client=client)

        # Then
        assert mock_get_paginated_offer_ids_by_venue_id.call_count == 2
        assert mock_process_eligible_offers.call_count == 1
        assert mock_process_eligible_offers.call_args_list == [
            mock.call(client=client, offer_ids=[1, 2], from_provider_update=False)
        ]
        assert mock_delete_venue_ids.call_count == 1

    @mock.patch("pcapi.settings.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE", 1)
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.delete_venue_ids")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_offer_ids_by_venue_id")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.process_eligible_offers")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.get_venue_ids")
    def test_should_not_trigger_indexing_when_no_venue(
        self,
        mock_get_venue_ids,
        mock_process_eligible_offers,
        mock_get_paginated_offer_ids_by_venue_id,
        mock_delete_venue_ids,
        app,
    ):
        # Given
        client = mock.MagicMock()
        mock_get_venue_ids.return_value = []

        # When
        batch_indexing_offers_in_algolia_by_venue(client=client)

        # Then
        mock_get_paginated_offer_ids_by_venue_id.assert_not_called()
        mock_process_eligible_offers.assert_not_called()
        mock_delete_venue_ids.assert_not_called()


class BatchIndexingOffersInAlgoliaFromDatabaseTest:
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_active_offer_ids")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.process_eligible_offers")
    def test_should_index_offers_once_when_offers_per_page_is_one_and_only_one_page(
        self, mock_process_eligible_offers, mock_get_paginated_active_offer_ids, app
    ):
        # Given
        client = mock.MagicMock()
        mock_get_paginated_active_offer_ids.side_effect = [[(1,)], []]

        # When
        batch_indexing_offers_in_algolia_from_database(client=client, ending_page=None, limit=1, starting_page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 2
        assert mock_process_eligible_offers.call_count == 1
        assert mock_process_eligible_offers.call_args_list == [
            mock.call(client=client, offer_ids=[1], from_provider_update=False)
        ]

    @mock.patch("pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_active_offer_ids")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.process_eligible_offers")
    def test_should_index_offers_twice_when_offers_per_page_is_one_and_two_pages(
        self, mock_process_eligible_offers, mock_get_paginated_active_offer_ids, app
    ):
        # Given
        client = mock.MagicMock()
        mock_get_paginated_active_offer_ids.side_effect = [[(1,)], [(2,)], []]

        # When
        batch_indexing_offers_in_algolia_from_database(client=client, ending_page=None, limit=1, starting_page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 3
        assert mock_process_eligible_offers.call_count == 2
        assert mock_process_eligible_offers.call_args_list == [
            mock.call(client=client, offer_ids=[1], from_provider_update=False),
            mock.call(client=client, offer_ids=[2], from_provider_update=False),
        ]

    @mock.patch("pcapi.scripts.algolia_indexing.indexing.offer_queries.get_paginated_active_offer_ids")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.process_eligible_offers")
    def test_should_index_offers_from_first_page_only_when_ending_page_is_provided(
        self, mock_process_eligible_offers, mock_get_paginated_active_offer_ids, app
    ):
        # Given
        client = mock.MagicMock()
        mock_get_paginated_active_offer_ids.side_effect = [[(1,)], [(2,)], []]

        # When
        batch_indexing_offers_in_algolia_from_database(client=client, ending_page=1, limit=1, starting_page=0)

        # Then
        assert mock_get_paginated_active_offer_ids.call_count == 1
        assert mock_process_eligible_offers.call_count == 1
        assert mock_process_eligible_offers.call_args_list == [
            mock.call(client=client, offer_ids=[1], from_provider_update=False),
        ]


@freeze_time("2020-01-05 10:00:00")
@pytest.mark.usefixtures("db_session")
class BatchDeletingExpiredOffersInAlgoliaTest:
    @override_settings(ALGOLIA_DELETING_OFFERS_CHUNK_SIZE=2)
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.delete_expired_offers")
    def test_default_run(self, mock_delete_expired_offers):
        # Given
        client = "fake redis client"
        offers_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 2, 12, 0))
        stock1 = offers_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 3, 12, 0))
        stock2 = offers_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 3, 12, 0))
        stock3 = offers_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 4, 12, 0))
        offers_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 5, 12, 0))

        # When
        batch_deleting_expired_offers_in_algolia(client=client)

        # Then
        assert mock_delete_expired_offers.mock_calls == [
            mock.call(client=client, offer_ids=[stock1.offerId, stock2.offerId]),
            mock.call(client=client, offer_ids=[stock3.offerId]),
        ]

    @mock.patch("pcapi.scripts.algolia_indexing.indexing.delete_expired_offers")
    def test_run_unlimited(self, mock_delete_expired_offers):
        client = "fake redis client"
        # more than 2 days ago, must be processed
        stock1 = offers_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 2, 12, 0))
        # today, must be ignored
        offers_factories.StockFactory(bookingLimitDatetime=datetime(2020, 1, 5, 12, 0))

        # When
        batch_deleting_expired_offers_in_algolia(client=client, process_all_expired=True)

        # Then
        assert mock_delete_expired_offers.mock_calls == [
            mock.call(client=client, offer_ids=[stock1.offerId]),
        ]


class BatchProcessingOfferIdsInErrorTest:
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.get_offer_ids_in_error")
    def test_should_retrieve_offer_ids_in_error(self, mock_get_offer_ids_in_error):
        # Given
        client = mock.MagicMock()
        mock_get_offer_ids_in_error.return_value = []

        # When
        batch_processing_offer_ids_in_error(client=client)

        # Then
        mock_get_offer_ids_in_error.assert_called_once()

    @mock.patch("pcapi.scripts.algolia_indexing.indexing.delete_offer_ids_in_error")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.process_eligible_offers")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.get_offer_ids_in_error")
    def test_should_delete_offer_ids_in_error_when_at_least_one_offer_id(
        self, mock_get_offer_ids_in_error, mock_process_eligible_offers, mock_delete_offer_ids_in_error
    ):
        # Given
        client = mock.MagicMock()
        mock_get_offer_ids_in_error.return_value = [1]

        # When
        batch_processing_offer_ids_in_error(client=client)

        # Then
        mock_get_offer_ids_in_error.assert_called_once_with(client=client)
        mock_process_eligible_offers.assert_called_once_with(client=client, offer_ids=[1], from_provider_update=False)
        mock_delete_offer_ids_in_error.assert_called_once_with(client=client)

    @mock.patch("pcapi.scripts.algolia_indexing.indexing.delete_offer_ids_in_error")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.process_eligible_offers")
    @mock.patch("pcapi.scripts.algolia_indexing.indexing.get_offer_ids_in_error")
    def test_should_not_delete_offer_ids_in_error_when_no_offer_id(
        self, mock_get_offer_ids_in_error, mock_process_eligible_offers, mock_delete_offer_ids_in_error
    ):
        # Given
        client = mock.MagicMock()
        mock_get_offer_ids_in_error.return_value = []

        # When
        batch_processing_offer_ids_in_error(client=client)

        # Then
        mock_get_offer_ids_in_error.assert_called_once_with(client=client)
        mock_delete_offer_ids_in_error.assert_not_called()
        mock_process_eligible_offers.assert_not_called()
