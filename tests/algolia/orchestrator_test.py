from datetime import datetime, timedelta
from unittest.mock import patch, call

from algolia.orchestrator import orchestrate, orchestrate_from_venue_providers
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_stock, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.human_ids import humanize

TOMORROW = datetime.now() + timedelta(days=1)


class OrchestrateTest:
    @clean_database
    @patch('algolia.orchestrator.add_objects')
    @patch('algolia.orchestrator.build_object', return_value={'fake': 'test'})
    def test_should_add_objects_when_objects_are_eligible(self,
                                                          mocked_build_object,
                                                          mocked_add_objects,
                                                          app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=10)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=10)
        offer3 = create_offer_with_thing_product(venue=venue, is_active=False)
        stock3 = create_stock(offer=offer3, booking_limit_datetime=TOMORROW, available=10)
        repository.save(stock1, stock2, stock3)

        # When
        orchestrate(offer_ids=[offer1.id, offer2.id])

        # Then
        assert mocked_build_object.call_count == 2
        mocked_add_objects.assert_called_once_with(objects=[
            {'fake': 'test'},
            {'fake': 'test'}
        ])

    @clean_database
    @patch('algolia.orchestrator.delete_objects')
    def test_should_delete_objects_when_objects_are_not_eligible(self,
                                                                 mocked_delete_objects,
                                                                 app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(venue=venue)
        stock1 = create_stock(offer=offer1, available=0)
        offer2 = create_offer_with_thing_product(venue=venue)
        stock2 = create_stock(offer=offer2, available=0)
        repository.save(stock1, stock2)

        # When
        orchestrate(offer_ids=[offer1.id, offer2.id])

        # Then
        humanize_offer_ids = [humanize(offer1.id), humanize(offer2.id)]
        mocked_delete_objects.assert_called_once_with(object_ids=humanize_offer_ids)

    @clean_database
    @patch('algolia.orchestrator.add_objects')
    @patch('algolia.orchestrator.clear_objects')
    @patch('algolia.orchestrator.build_object', return_value={'fake': 'test'})
    def test_should_clear_objects_on_demand(self,
                                            mocked_build_object,
                                            mocked_clear_objects,
                                            mocked_add_objects,
                                            app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=10)
        repository.save(stock)

        # When
        orchestrate(offer_ids=[offer.id], is_clear=True)

        # Then
        mocked_clear_objects.assert_called_once_with()
        mocked_add_objects.assert_called_once_with(objects=[
            {'fake': 'test'}
        ])


class OrchestrateFromLocalProvidersTest:
    @patch('algolia.orchestrator.ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', return_value=3)
    @patch('algolia.orchestrator.offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id')
    @patch('algolia.orchestrator.orchestrate')
    def test_should_index_offers_in_a_paginated_way(self,
                                                    mock_orchestrate,
                                                    mock_get_paginated_offer_ids_by_venue_id_and_last_provider_id,
                                                    mock_chunk_size,
                                                    app):
        # Given
        mock_get_paginated_offer_ids_by_venue_id_and_last_provider_id.side_effect = [
            [(1,), (2,), (3,)],
            [(4,)],
            [],
            [(5,), (6,), (7,)],
            [(8,)],
            []
        ]
        venue_providers = [
            {'id': 1, 'lastProviderId': '5', 'venueId': 8},
            {'id': 2, 'lastProviderId': '6', 'venueId': 9},
        ]

        # When
        orchestrate_from_venue_providers(venue_providers=venue_providers)

        # Then
        assert mock_get_paginated_offer_ids_by_venue_id_and_last_provider_id.call_count == 6
        assert mock_get_paginated_offer_ids_by_venue_id_and_last_provider_id.call_args_list == [
            call(last_provider_id='5', limit=mock_chunk_size, page=0, venue_id=8),
            call(last_provider_id='5', limit=mock_chunk_size, page=1, venue_id=8),
            call(last_provider_id='5', limit=mock_chunk_size, page=2, venue_id=8),
            call(last_provider_id='6', limit=mock_chunk_size, page=0, venue_id=9),
            call(last_provider_id='6', limit=mock_chunk_size, page=1, venue_id=9),
            call(last_provider_id='6', limit=mock_chunk_size, page=2, venue_id=9)]

        assert mock_orchestrate.call_count == 4
        assert mock_orchestrate.call_args_list == [
            call(offer_ids=[1, 2, 3]),
            call(offer_ids=[4]),
            call(offer_ids=[5, 6, 7]),
            call(offer_ids=[8])
        ]
