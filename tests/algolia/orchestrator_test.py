from unittest.mock import patch

from algolia.orchestrator import orchestrate
from models import PcObject
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_stock, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.human_ids import humanize


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
        stock1 = create_stock(offer=offer1, available=10)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(offer=offer2, available=10)
        PcObject.save(stock1, stock2)
        offer_ids = [offer1.id, offer2.id]

        # When
        orchestrate(offer_ids)

        # Then
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
        offer1 = create_offer_with_thing_product(venue=venue, idx=1)
        stock1 = create_stock(offer=offer1, available=0)
        offer2 = create_offer_with_thing_product(venue=venue, idx=2)
        stock2 = create_stock(offer=offer2, available=0)
        PcObject.save(stock1, stock2)
        offer_ids = [1, 2]

        # When
        orchestrate(offer_ids)

        # Then
        humanize_offer_ids = [humanize(1), humanize(2)]
        mocked_delete_objects.assert_called_once_with(object_ids=humanize_offer_ids)
