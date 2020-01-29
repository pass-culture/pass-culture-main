from datetime import datetime, timedelta
from unittest.mock import patch, call

from algolia.orchestrator import orchestrate_from_offer, \
    orchestrate_delete_expired_offers, orchestrate_from_venue_provider
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_stock, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.human_ids import humanize

TOMORROW = datetime.now() + timedelta(days=1)


class OrchestrateTest:
    @clean_database
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.add_objects')
    @patch('algolia.orchestrator.build_object', return_value={'fake': 'test'})
    def test_should_add_objects_when_objects_are_eligible_and_not_already_indexed_offer_ids(self,
                                                                                            mock_build_object,
                                                                                            mock_add_objects,
                                                                                            mock_delete_objects,
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
        indexing_ids, deleting_ids = orchestrate_from_offer(offer_ids=[offer1.id, offer2.id], indexed_offer_ids=set())

        # Then
        assert mock_build_object.call_count == 2
        mock_add_objects.assert_called_once_with(objects=[
            {'fake': 'test'},
            {'fake': 'test'}
        ])
        mock_delete_objects.assert_not_called()
        assert indexing_ids == [offer1.id, offer2.id]
        assert deleting_ids == []

    @clean_database
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.add_objects')
    def test_should_delete_objects_when_objects_are_not_eligible_and_were_already_indexed(self,
                                                                                          mock_add_objects,
                                                                                          mock_delete_objects,
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
        indexing_ids, deleting_ids = orchestrate_from_offer(offer_ids=[offer1.id, offer2.id],
                                                            indexed_offer_ids={offer1.id})

        # Then
        humanize_offer_ids = [humanize(offer1.id)]
        mock_add_objects.assert_not_called()
        mock_delete_objects.assert_called_once_with(object_ids=humanize_offer_ids)
        assert indexing_ids == []
        assert deleting_ids == [offer1.id]

    @clean_database
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.add_objects')
    def test_should_add_one_object_and_delete_one_object(self,
                                                         mock_add_objects,
                                                         mock_delete_objects,
                                                         app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=10)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=0)
        repository.save(stock1, stock2)

        # When
        indexing_ids, deleting_ids = orchestrate_from_offer(offer_ids=[offer1.id, offer2.id],
                                                            indexed_offer_ids={offer2.id})

        # Then
        mock_add_objects.assert_called_once()
        mock_delete_objects.assert_called_once()
        assert indexing_ids == [offer1.id]
        assert deleting_ids == [offer2.id]

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
        orchestrate_from_offer(offer_ids=[offer.id], is_clear=True)

        # Then
        mocked_clear_objects.assert_called_once_with()
        mocked_add_objects.assert_called_once_with(objects=[
            {'fake': 'test'}
        ])


class OrchestrateFromVenueProviderTest:
    @patch('algolia.orchestrator.build_object')
    @patch('algolia.orchestrator.add_objects')
    @clean_database
    def test_should_index_offers_that_are_not_already_indexed(self, mock_add_objects, mock_build_object, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=10)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=10)
        offer3 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock3 = create_stock(offer=offer3, booking_limit_datetime=TOMORROW, available=10)
        repository.save(stock1, stock2, stock3)
        offer_ids = [offer1.id, offer2.id, offer3.id]
        indexed_offer_ids = set()
        mock_build_object.side_effect = [
            {'fake': 'object'},
            {'fake': 'object'},
            {'fake': 'object'},
        ]

        # When
        indexing_offer_ids, deleting_offer_ids = orchestrate_from_venue_provider(
            offer_ids=offer_ids,
            indexed_offer_ids=indexed_offer_ids
        )

        # Then
        assert mock_add_objects.call_count == 1
        assert mock_add_objects.call_args_list == [
            call(objects=[{'fake': 'object'}, {'fake': 'object'}, {'fake': 'object'}])
        ]
        assert indexing_offer_ids == [offer1.id, offer2.id, offer3.id]
        assert deleting_offer_ids == []

    @patch('algolia.orchestrator.build_object')
    @patch('algolia.orchestrator.add_objects')
    @clean_database
    def test_should_not_index_offers_that_are_already_indexed(
            self,
            mock_add_objects,
            mock_build_object,
            app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=10)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=10)
        offer3 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock3 = create_stock(offer=offer3, booking_limit_datetime=TOMORROW, available=10)
        repository.save(stock1, stock2, stock3)
        offer_ids = [offer1.id, offer2.id, offer3.id]
        indexed_offer_ids = {offer1.id, offer2.id, offer3.id}
        mock_build_object.side_effect = [
            {'fake': 'object'},
            {'fake': 'object'},
            {'fake': 'object'},
        ]

        # When
        indexing_offer_ids, deleting_offer_ids = orchestrate_from_venue_provider(
            offer_ids=offer_ids,
            indexed_offer_ids=indexed_offer_ids
        )

        # Then
        assert mock_add_objects.call_count == 0
        assert indexing_offer_ids == []
        assert deleting_offer_ids == []

    @patch('algolia.orchestrator.delete_objects')
    @clean_database
    def test_should_only_delete_offers_that_are_already_indexed_when_offers_are_no_longer_eligible(
            self,
            mock_delete_objects,
            app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=0)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=0)
        offer3 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock3 = create_stock(offer=offer3, booking_limit_datetime=TOMORROW, available=0)
        repository.save(stock1, stock2, stock3)
        offer_ids = [offer1.id, offer2.id, offer3.id]
        indexed_offer_ids = {offer1.id, offer2.id, offer3.id}

        # When
        indexing_offer_ids, deleting_offer_ids = orchestrate_from_venue_provider(
            offer_ids=offer_ids,
            indexed_offer_ids=indexed_offer_ids
        )

        # Then
        assert mock_delete_objects.call_count == 1
        assert mock_delete_objects.call_args_list == [
            call(object_ids=[humanize(offer1.id), humanize(offer2.id), humanize(offer3.id)])
        ]
        assert indexing_offer_ids == []
        assert deleting_offer_ids == [offer1.id, offer2.id, offer3.id]

class OrchestrateCleanExpiredOffersTest:
    @patch('algolia.orchestrator.delete_objects')
    def test_should_delete_expired_offers_from_algolia_when_at_least_one_offer_id(self,
                                                                                  mock_delete_objects,
                                                                                  app):
        # When
        orchestrate_delete_expired_offers(offer_ids=[1, 2, 3])

        # Then
        assert mock_delete_objects.call_count == 1
        assert mock_delete_objects.call_args_list == [
            call(object_ids=['AE', 'A9', 'AM'])
        ]

    @patch('algolia.orchestrator.delete_objects')
    def test_should_not_delete_expired_offers_from_algolia_when_no_offer_id(self,
                                                                            mock_delete_objects,
                                                                            app):
        # When
        orchestrate_delete_expired_offers(offer_ids=[])

        # Then
        assert mock_delete_objects.call_count == 0
