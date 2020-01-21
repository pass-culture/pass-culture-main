from unittest.mock import patch, MagicMock, call

from models import PcObject
from scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer, batch_indexing_offers_in_algolia_by_venue, \
    batch_indexing_offers_in_algolia_from_database, batch_indexing_offers_in_algolia_by_venue_provider
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_event_product


class BatchIndexingOffersInAlgoliaByOfferTest:
    @patch('scripts.algolia_indexing.indexing.delete_offer_ids')
    @patch('scripts.algolia_indexing.indexing.orchestrate')
    @patch('scripts.algolia_indexing.indexing.get_offer_ids', return_value=[1, 2, 3])
    def test_should_trigger_indexing_using_offer_ids_from_redis(self,
                                                                mock_get_offer_ids,
                                                                mock_orchestrate,
                                                                mock_delete_offer_ids):
        # Given
        client = MagicMock()

        # When
        batch_indexing_offers_in_algolia_by_offer(client=client)

        # Then
        mock_get_offer_ids.assert_called_once()
        mock_orchestrate.assert_called_once_with(offer_ids=[1, 2, 3])
        mock_delete_offer_ids.assert_called_once()


class BatchIndexingOffersInAlgoliaFromDatabaseTest:
    @patch('scripts.algolia_indexing.indexing.orchestrate')
    @clean_database
    def test_should_index_offers_one_time_when_offers_per_page_is_one_and_only_one_page(self, mock_orchestrate, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(venue=venue)
        PcObject.save(offer)

        # When
        batch_indexing_offers_in_algolia_from_database(limit=1)

        # Then
        assert mock_orchestrate.call_count == 1
        call_args_list = mock_orchestrate.call_args_list
        assert call_args_list == [
            call(offer_ids=[offer.id])
        ]

    @patch('scripts.algolia_indexing.indexing.orchestrate')
    @clean_database
    def test_should_index_offers_two_times_when_offers_per_page_is_one_and_two_pages(self, mock_orchestrate, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(venue=venue)
        offer2 = create_offer_with_event_product(venue=venue)
        PcObject.save(offer1, offer2)

        # When
        batch_indexing_offers_in_algolia_from_database(limit=1)

        # Then
        assert mock_orchestrate.call_count == 2
        call_args_list = mock_orchestrate.call_args_list
        assert call_args_list == [
            call(offer_ids=[offer1.id]),
            call(offer_ids=[offer2.id])
        ]


class BatchIndexingOffersInAlgoliaByVenueTest:
    @patch('scripts.algolia_indexing.indexing.delete_venue_ids')
    @patch('scripts.algolia_indexing.indexing.orchestrate')
    @patch('scripts.algolia_indexing.indexing.get_venue_ids', return_value=[13, 666])
    @clean_database
    def test_should_index_each_offer_of_each_venue(self,
                                                   mock_get_venue_ids,
                                                   mock_orchestrate,
                                                   mock_delete_venue_ids,
                                                   app):
        # Given
        client = MagicMock()
        offerer = create_offerer()
        venue1 = create_venue(offerer=offerer, idx=666)
        venue2 = create_venue(offerer=offerer, idx=13, siret=123654987)
        offer1 = create_offer_with_event_product(venue=venue1)
        offer2 = create_offer_with_event_product(venue=venue2)
        offer3 = create_offer_with_event_product(venue=venue2)
        PcObject.save(offer1, offer2, offer3)

        # When
        batch_indexing_offers_in_algolia_by_venue(client=client, limit=1)

        # Then
        assert mock_orchestrate.call_count == 3
        call_args_list = mock_orchestrate.call_args_list
        assert call_args_list == [
            call(offer_ids=[offer2.id]),
            call(offer_ids=[offer3.id]),
            call(offer_ids=[offer1.id])
        ]
        assert mock_delete_venue_ids.call_count == 1


class BatchIndexingOffersInAlgoliaByVenueProviderTest:
    @patch('scripts.algolia_indexing.indexing.delete_venue_providers')
    @patch('scripts.algolia_indexing.indexing.orchestrate_from_venue_providers')
    @patch('scripts.algolia_indexing.indexing.get_venue_providers', return_value=[
        {'id': 1, 'lastProviderId': 2, 'venueId': 5},
        {'id': 2, 'lastProviderId': 6, 'venueId': 7}
    ])
    def test_should_trigger_indexing_using_venue_providers_from_redis(self,
                                                                      mock_get_venue_providers,
                                                                      mock_orchestrate,
                                                                      mock_delete_venue_providers):
        # Given
        client = MagicMock()

        # When
        batch_indexing_offers_in_algolia_by_venue_provider(client=client)

        # Then
        mock_get_venue_providers.assert_called_once()
        mock_orchestrate.assert_called_once_with(venue_providers=[
            {'id': 1, 'lastProviderId': 2, 'venueId': 5},
            {'id': 2, 'lastProviderId': 6, 'venueId': 7}
        ])
        mock_delete_venue_providers.assert_called_once()
