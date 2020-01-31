from datetime import datetime, timedelta
from unittest.mock import patch, call, MagicMock

from freezegun import freeze_time

from algolia.orchestrator import orchestrate_from_offer, \
    orchestrate_delete_expired_offers, orchestrate_from_venue_provider
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_stock, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product
from utils.human_ids import humanize

TOMORROW = datetime.now() + timedelta(days=1)


class OrchestrateFromOfferTest:
    @clean_database
    @patch('algolia.orchestrator.delete_offers_from_hashmap')
    @patch('algolia.orchestrator.add_offer_to_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.add_objects')
    @patch('algolia.orchestrator.build_object', return_value={'fake': 'test'})
    def test_should_add_objects_when_objects_are_eligible_and_not_already_indexed(self,
                                                                                  mock_build_object,
                                                                                  mock_add_objects,
                                                                                  mock_delete_objects,
                                                                                  mock_add_offer_to_hashmap,
                                                                                  mock_delete_offers_from_hashmap,
                                                                                  app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
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
        orchestrate_from_offer(client=client, offer_ids=[offer1.id, offer2.id])

        # Then
        assert mock_build_object.call_count == 2
        mock_add_objects.assert_called_once_with(objects=[
            {'fake': 'test'},
            {'fake': 'test'}
        ])
        assert mock_add_offer_to_hashmap.call_count == 2
        assert mock_add_offer_to_hashmap.call_args_list == [
            call(pipeline=mock_pipeline, offer_details={}, offer_id=offer1.id),
            call(pipeline=mock_pipeline, offer_details={}, offer_id=offer2.id),
        ]
        mock_delete_offers_from_hashmap.assert_not_called()
        mock_delete_objects.assert_not_called()
        mock_pipeline.execute.assert_called_once()
        mock_pipeline.reset.assert_called_once()

    @clean_database
    @patch('algolia.orchestrator.delete_offers_from_hashmap')
    @patch('algolia.orchestrator.get_offer_from_hashmap')
    @patch('algolia.orchestrator.add_offer_to_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.add_objects')
    @patch('algolia.orchestrator.build_object', return_value={'fake': 'test'})
    def test_should_delete_objects_when_objects_are_not_eligible_and_were_already_indexed(self,
                                                                                          mock_build_object,
                                                                                          mock_add_objects,
                                                                                          mock_delete_objects,
                                                                                          mock_add_offer_to_hashmap,
                                                                                          mock_get_offer_from_hashmap,
                                                                                          mock_delete_offers_from_hashmap,
                                                                                          app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=0)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=0)
        repository.save(stock1, stock2)
        mock_get_offer_from_hashmap.side_effect = [
            True,
            True
        ]

        # When
        orchestrate_from_offer(client=client, offer_ids=[offer1.id, offer2.id])

        # Then
        mock_build_object.assert_not_called()
        mock_add_objects.assert_not_called()
        mock_add_offer_to_hashmap.assert_not_called()
        mock_delete_objects.assert_called_once()
        assert mock_delete_objects.call_args_list == [
            call(object_ids=[humanize(offer1.id), humanize(offer2.id)])
        ]
        mock_delete_offers_from_hashmap.assert_called_once()
        assert mock_delete_offers_from_hashmap.call_args_list == [
            call(client=client, offer_ids=[offer1.id, offer2.id])
        ]
        mock_pipeline.execute.assert_not_called()
        mock_pipeline.reset.assert_not_called()

    @clean_database
    @patch('algolia.orchestrator.delete_offers_from_hashmap')
    @patch('algolia.orchestrator.get_offer_from_hashmap')
    @patch('algolia.orchestrator.add_offer_to_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.add_objects')
    @patch('algolia.orchestrator.build_object', return_value={'fake': 'test'})
    def test_should_not_delete_objects_when_objects_are_not_eligible_and_were_not_already_indexed(self,
                                                                                                  mock_build_object,
                                                                                                  mock_add_objects,
                                                                                                  mock_delete_objects,
                                                                                                  mock_add_offer_to_hashmap,
                                                                                                  mock_get_offer_from_hashmap,
                                                                                                  mock_delete_offers_from_hashmap,
                                                                                                  app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=0)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=0)
        repository.save(stock1, stock2)
        mock_get_offer_from_hashmap.side_effect = [
            False,
            False
        ]

        # When
        orchestrate_from_offer(client=client, offer_ids=[offer1.id, offer2.id])

        # Then
        mock_build_object.assert_not_called()
        mock_add_objects.assert_not_called()
        mock_add_offer_to_hashmap.assert_not_called()
        mock_delete_objects.assert_not_called()
        mock_delete_offers_from_hashmap.assert_not_called()
        mock_pipeline.execute.assert_not_called()
        mock_pipeline.reset.assert_not_called()

    @clean_database
    @patch('algolia.orchestrator.clear_objects')
    def test_should_clear_objects_on_demand(self,
                                            mock_clear_objects,
                                            app):
        # Given
        client = MagicMock()

        # When
        orchestrate_from_offer(client=client, offer_ids=[], is_clear=True)

        # Then
        mock_clear_objects.assert_called_once()


class OrchestrateFromVenueProviderTest:
    @patch('algolia.orchestrator.delete_offer_ids_from_list')
    @patch('algolia.orchestrator.add_offer_to_hashmap')
    @patch('algolia.orchestrator.get_offer_details_from_hashmap')
    @patch('algolia.orchestrator.get_offer_from_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.build_object')
    @patch('algolia.orchestrator.add_objects')
    @clean_database
    def test_should_index_offers_that_are_not_already_indexed(self,
                                                              mock_add_objects,
                                                              mock_build_object,
                                                              mock_delete_objects,
                                                              mock_get_offer_from_hashmap,
                                                              mock_get_offer_details_from_hashmap,
                                                              mock_add_offer_to_hashmap,
                                                              mock_delete_offer_ids_from_list,
                                                              app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name='super offre 1', venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=1)
        offer2 = create_offer_with_thing_product(thing_name='super offre 2', venue=venue, is_active=True)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=1)
        offer3 = create_offer_with_thing_product(thing_name='super offre 3', venue=venue, is_active=True)
        stock3 = create_stock(offer=offer3, booking_limit_datetime=TOMORROW, available=1)
        repository.save(stock1, stock2, stock3)
        offer_ids = [offer1.id, offer2.id, offer3.id]
        mock_build_object.side_effect = [
            {'fake': 'object'},
            {'fake': 'object'},
            {'fake': 'object'},
        ]
        mock_get_offer_from_hashmap.side_effect = [False, False, False]

        # When
        orchestrate_from_venue_provider(client=client, offer_ids=offer_ids)

        # Then
        assert mock_get_offer_from_hashmap.call_count == 3
        assert mock_get_offer_details_from_hashmap.call_count == 0
        assert mock_add_offer_to_hashmap.call_count == 3
        assert mock_add_offer_to_hashmap.call_args_list == [
            call(pipeline=mock_pipeline, offer_details={'name': 'super offre 1', 'dateRange': []}, offer_id=offer1.id),
            call(pipeline=mock_pipeline, offer_details={'name': 'super offre 2', 'dateRange': []}, offer_id=offer2.id),
            call(pipeline=mock_pipeline, offer_details={'name': 'super offre 3', 'dateRange': []}, offer_id=offer3.id),
        ]
        assert mock_add_objects.call_count == 1
        assert mock_add_objects.call_args_list == [
            call(objects=[{'fake': 'object'}, {'fake': 'object'}, {'fake': 'object'}])
        ]
        assert mock_pipeline.execute.call_count == 1
        assert mock_pipeline.reset.call_count == 1
        assert mock_delete_objects.call_count == 0
        assert mock_delete_offer_ids_from_list.call_count == 1

    @patch('algolia.orchestrator.delete_offer_ids_from_list')
    @patch('algolia.orchestrator.delete_offers_from_hashmap')
    @patch('algolia.orchestrator.add_offer_to_hashmap')
    @patch('algolia.orchestrator.get_offer_details_from_hashmap')
    @patch('algolia.orchestrator.get_offer_from_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.build_object')
    @patch('algolia.orchestrator.add_objects')
    @clean_database
    def test_should_delete_offers_that_are_already_indexed(self,
                                                           mock_add_objects,
                                                           mock_build_object,
                                                           mock_delete_objects,
                                                           mock_get_offer_from_hashmap,
                                                           mock_get_offer_details_from_hashmap,
                                                           mock_add_offer_to_hashmap,
                                                           mock_delete_offers_from_hashmap,
                                                           mock_delete_offer_ids_from_list,
                                                           app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name='super offre 1', venue=venue, is_active=False)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=1)
        offer2 = create_offer_with_thing_product(thing_name='super offre 2', venue=venue, is_active=False)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=1)
        offer3 = create_offer_with_thing_product(thing_name='super offre 3', venue=venue, is_active=False)
        stock3 = create_stock(offer=offer3, booking_limit_datetime=TOMORROW, available=1)
        repository.save(stock1, stock2, stock3)
        offer_ids = [offer1.id, offer2.id, offer3.id]
        mock_get_offer_from_hashmap.side_effect = [True, True, True]

        # When
        orchestrate_from_venue_provider(client=client, offer_ids=offer_ids)

        # Then
        assert mock_get_offer_from_hashmap.call_count == 3
        assert mock_build_object.call_count == 0
        assert mock_add_objects.call_count == 0
        assert mock_get_offer_details_from_hashmap.call_count == 0
        assert mock_add_offer_to_hashmap.call_count == 0
        assert mock_delete_objects.call_count == 1
        assert mock_delete_objects.call_args_list == [
            call(object_ids=[humanize(offer1.id), humanize(offer2.id), humanize(offer3.id)])
        ]
        assert mock_delete_offers_from_hashmap.call_count == 1
        assert mock_delete_offers_from_hashmap.call_args_list == [
            call(client=client, offer_ids=[offer1.id, offer2.id, offer3.id])
        ]
        assert mock_pipeline.execute.call_count == 0
        assert mock_pipeline.reset.call_count == 0
        assert mock_delete_offer_ids_from_list.call_count == 1

    @patch('algolia.orchestrator.delete_offer_ids_from_list')
    @patch('algolia.orchestrator.delete_offers_from_hashmap')
    @patch('algolia.orchestrator.get_offer_from_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @clean_database
    def test_should_not_delete_offers_that_are_not_already_indexed(self,
                                                                   mock_delete_objects,
                                                                   mock_get_offer_from_hashmap,
                                                                   mock_delete_offers_from_hashmap,
                                                                   mock_delete_offer_ids_from_list,
                                                                   app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name='super offre 1', venue=venue, is_active=False)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=1)
        offer2 = create_offer_with_thing_product(thing_name='super offre 2', venue=venue, is_active=False)
        stock2 = create_stock(offer=offer2, booking_limit_datetime=TOMORROW, available=1)
        repository.save(stock1, stock2)
        offer_ids = [offer1.id, offer2.id]
        mock_get_offer_from_hashmap.side_effect = [False, False]

        # When
        orchestrate_from_venue_provider(client=client, offer_ids=offer_ids)

        # Then
        assert mock_get_offer_from_hashmap.call_count == 2
        assert mock_delete_objects.call_count == 0
        assert mock_delete_offers_from_hashmap.call_count == 0
        assert mock_delete_offer_ids_from_list.call_count == 1

    @patch('algolia.orchestrator.delete_offer_ids_from_list')
    @patch('algolia.orchestrator.add_offer_to_hashmap')
    @patch('algolia.orchestrator.get_offer_details_from_hashmap')
    @patch('algolia.orchestrator.get_offer_from_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.build_object')
    @patch('algolia.orchestrator.add_objects')
    @clean_database
    def test_should_reindex_offers_that_are_already_indexed_only_if_offer_name_changed(self,
                                                                                       mock_add_objects,
                                                                                       mock_build_object,
                                                                                       mock_delete_objects,
                                                                                       mock_get_offer_from_hashmap,
                                                                                       mock_get_offer_details_from_hashmap,
                                                                                       mock_add_offer_to_hashmap,
                                                                                       mock_delete_offer_ids_from_list,
                                                                                       app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name='super offre 1', venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=1)
        repository.save(stock1)
        offer_ids = [offer1.id]
        mock_build_object.side_effect = [
            {'fake': 'object'},
        ]
        mock_get_offer_from_hashmap.return_value = True
        mock_get_offer_details_from_hashmap.return_value = {'name': 'une autre super offre', 'dateRange': []}

        # When
        orchestrate_from_venue_provider(client=client, offer_ids=offer_ids)

        # Then
        assert mock_get_offer_from_hashmap.call_count == 1
        assert mock_get_offer_details_from_hashmap.call_count == 1
        assert mock_add_offer_to_hashmap.call_count == 1
        assert mock_add_offer_to_hashmap.call_args_list == [
            call(pipeline=mock_pipeline, offer_details={'name': 'super offre 1', 'dateRange': []}, offer_id=offer1.id),
        ]
        assert mock_add_objects.call_count == 1
        assert mock_add_objects.call_args_list == [
            call(objects=[{'fake': 'object'}])
        ]
        assert mock_pipeline.execute.call_count == 1
        assert mock_pipeline.reset.call_count == 1
        assert mock_delete_objects.call_count == 0
        assert mock_delete_offer_ids_from_list.call_count == 1

    @patch('algolia.orchestrator.delete_offer_ids_from_list')
    @patch('algolia.orchestrator.add_offer_to_hashmap')
    @patch('algolia.orchestrator.get_offer_details_from_hashmap')
    @patch('algolia.orchestrator.get_offer_from_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.build_object')
    @patch('algolia.orchestrator.add_objects')
    @clean_database
    def test_should_not_reindex_offers_that_are_already_indexed_if_offer_name_has_not_changed(self,
                                                                                             mock_add_objects,
                                                                                             mock_build_object,
                                                                                             mock_delete_objects,
                                                                                             mock_get_offer_from_hashmap,
                                                                                             mock_get_offer_details_from_hashmap,
                                                                                             mock_add_offer_to_hashmap,
                                                                                             mock_delete_offer_ids_from_list,
                                                                                             app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name='super offre 1', venue=venue, is_active=True)
        stock1 = create_stock(offer=offer1, booking_limit_datetime=TOMORROW, available=1)
        repository.save(stock1)
        offer_ids = [offer1.id]
        mock_build_object.side_effect = [
            {'fake': 'object'},
        ]
        mock_get_offer_from_hashmap.return_value = True
        mock_get_offer_details_from_hashmap.return_value = {'name': 'super offre 1', 'dateRange': []}

        # When
        orchestrate_from_venue_provider(client=client, offer_ids=offer_ids)

        # Then
        assert mock_get_offer_from_hashmap.call_count == 1
        assert mock_get_offer_details_from_hashmap.call_count == 1
        assert mock_add_offer_to_hashmap.call_count == 0
        assert mock_add_objects.call_count == 0
        assert mock_pipeline.execute.call_count == 0
        assert mock_pipeline.reset.call_count == 0
        assert mock_delete_objects.call_count == 0
        assert mock_delete_offer_ids_from_list.call_count == 1

    @patch('algolia.orchestrator.delete_offer_ids_from_list')
    @patch('algolia.orchestrator.add_offer_to_hashmap')
    @patch('algolia.orchestrator.get_offer_details_from_hashmap')
    @patch('algolia.orchestrator.get_offer_from_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.build_object')
    @patch('algolia.orchestrator.add_objects')
    @clean_database
    @freeze_time('2019-01-01 12:00:00')
    def test_should_reindex_offers_that_are_already_indexed_only_if_stocks_are_changed(self,
                                                                                       mock_add_objects,
                                                                                       mock_build_object,
                                                                                       mock_delete_objects,
                                                                                       mock_get_offer_from_hashmap,
                                                                                       mock_get_offer_details_from_hashmap,
                                                                                       mock_add_offer_to_hashmap,
                                                                                       mock_delete_offer_ids_from_list,
                                                                                       app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_event_product(date_created=datetime(2019, 1, 1),
                                                event_name='super offre 1',
                                                venue=venue,
                                                is_active=True)
        stock = create_stock(available=1,
                             beginning_datetime=datetime(2019, 1, 5),
                             booking_limit_datetime=datetime(2019, 1, 3),
                             end_datetime=datetime(2019, 1, 7),
                             offer=offer)
        repository.save(stock)
        offer_ids = [offer.id]
        mock_build_object.side_effect = [
            {'fake': 'object'},
        ]
        mock_get_offer_from_hashmap.return_value = True
        mock_get_offer_details_from_hashmap.return_value = {'name': 'super offre 1',
                                                            'dateRange': ['2018-01-01 10:00:00', '2018-01-05 12:00:00']}

        # When
        orchestrate_from_venue_provider(client=client, offer_ids=offer_ids)

        # Then
        assert mock_get_offer_from_hashmap.call_count == 1
        assert mock_get_offer_details_from_hashmap.call_count == 1
        assert mock_add_offer_to_hashmap.call_count == 1
        assert mock_add_offer_to_hashmap.call_args_list == [
            call(pipeline=mock_pipeline,
                 offer_details={'name': 'super offre 1', 'dateRange': ['2019-01-05 00:00:00', '2019-01-07 00:00:00']},
                 offer_id=offer.id),
        ]
        assert mock_add_objects.call_count == 1
        assert mock_add_objects.call_args_list == [
            call(objects=[{'fake': 'object'}])
        ]
        assert mock_pipeline.execute.call_count == 1
        assert mock_pipeline.reset.call_count == 1
        assert mock_delete_objects.call_count == 0
        assert mock_delete_offer_ids_from_list.call_count == 1

    @patch('algolia.orchestrator.delete_offer_ids_from_list')
    @patch('algolia.orchestrator.add_offer_to_hashmap')
    @patch('algolia.orchestrator.get_offer_details_from_hashmap')
    @patch('algolia.orchestrator.get_offer_from_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    @patch('algolia.orchestrator.build_object')
    @patch('algolia.orchestrator.add_objects')
    @clean_database
    @freeze_time('2019-01-01 12:00:00')
    def test_should_not_reindex_offers_that_are_already_indexed_if_stocks_are_not_changed(self,
                                                                                          mock_add_objects,
                                                                                          mock_build_object,
                                                                                          mock_delete_objects,
                                                                                          mock_get_offer_from_hashmap,
                                                                                          mock_get_offer_details_from_hashmap,
                                                                                          mock_add_offer_to_hashmap,
                                                                                          mock_delete_offer_ids_from_list,
                                                                                          app):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_event_product(date_created=datetime(2019, 1, 1),
                                                event_name='super offre 1',
                                                venue=venue,
                                                is_active=True)
        stock = create_stock(available=1,
                             beginning_datetime=datetime(2019, 1, 5),
                             booking_limit_datetime=datetime(2019, 1, 3),
                             end_datetime=datetime(2019, 1, 7),
                             offer=offer)
        repository.save(stock)
        offer_ids = [offer.id]
        mock_build_object.side_effect = [
            {'fake': 'object'},
        ]
        mock_get_offer_from_hashmap.return_value = True
        mock_get_offer_details_from_hashmap.return_value = {'name': 'super offre 1',
                                                            'dateRange': ['2019-01-05 00:00:00', '2019-01-07 00:00:00']}

        # When
        orchestrate_from_venue_provider(client=client, offer_ids=offer_ids)

        # Then
        assert mock_get_offer_from_hashmap.call_count == 1
        assert mock_get_offer_details_from_hashmap.call_count == 1
        assert mock_add_offer_to_hashmap.call_count == 0
        assert mock_add_objects.call_count == 0
        assert mock_pipeline.execute.call_count == 0
        assert mock_pipeline.reset.call_count == 0
        assert mock_delete_objects.call_count == 0
        assert mock_delete_offer_ids_from_list.call_count == 1


class OrchestrateDeleteExpiredOffersTest:
    @patch('algolia.orchestrator.delete_offers_from_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    def test_should_delete_expired_offers_from_algolia_when_at_least_one_offer_id(self,
                                                                                  mock_delete_objects,
                                                                                  mock_delete_offers_from_hashmap,
                                                                                  app):
        # Given
        client = MagicMock()

        # When
        orchestrate_delete_expired_offers(client=client, offer_ids=[1, 2, 3])

        # Then
        assert mock_delete_objects.call_count == 1
        assert mock_delete_objects.call_args_list == [
            call(object_ids=['AE', 'A9', 'AM'])
        ]
        assert mock_delete_offers_from_hashmap.call_count == 1
        assert mock_delete_offers_from_hashmap.call_args_list == [
            call(client=client, offer_ids=[1, 2, 3])
        ]

    @patch('algolia.orchestrator.delete_offers_from_hashmap')
    @patch('algolia.orchestrator.delete_objects')
    def test_should_not_delete_expired_offers_from_algolia_when_no_offer_id(self,
                                                                            mock_delete_objects,
                                                                            mock_delete_offers_from_hashmap,
                                                                            app):
        # Given
        client = MagicMock()

        # When
        orchestrate_delete_expired_offers(client=client, offer_ids=[])

        # Then
        assert mock_delete_objects.call_count == 0
        assert mock_delete_offers_from_hashmap.call_count == 0
