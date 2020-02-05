from unittest.mock import patch

from models import Offer
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue, create_offerer
from tests.model_creators.specific_creators import create_offer_with_thing_product
from use_cases.update_an_offer import update_an_offer


class UseCaseTest:
    class UpdateAnOfferTest:
        class WhenTheOfferIsFromAllocine:
            @clean_database
            @patch('use_cases.update_an_offer.redis.add_offer_id')
            def test_keep_track_of_updated_fields_so_they_wont_be_overriden(self, mock_redis, app):
                # Given
                provider = get_provider_by_local_class('AllocineStocks')
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue, last_provider=provider)
                repository.save(offer)

                # When
                modifications = {'isDuo': 'true'}
                update_an_offer(offer, modifications)

                # Then
                offer = Offer.query.one()
                assert offer.fieldsUpdated == ['isDuo']

            @clean_database
            @patch('use_cases.update_an_offer.redis.add_offer_id')
            def test_preserve_updated_fields_so_they_wont_be_overriden(self, mock_redis, app):
                # Given
                provider = get_provider_by_local_class('AllocineStocks')
                offerer = create_offerer()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue, last_provider=provider)
                offer.fieldsUpdated = ['isActive']

                repository.save(offer)

                # When
                modifications = {'isDuo': 'true'}
                update_an_offer(offer, modifications)

                # Then
                offer = Offer.query.one()
                assert offer.fieldsUpdated == ['isDuo', 'isActive']

