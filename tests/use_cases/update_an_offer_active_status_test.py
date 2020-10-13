from unittest.mock import patch

from pcapi.models.feature import FeatureToggle
from pcapi.model_creators.generic_creators import create_offerer, create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.use_cases.update_an_offer_active_status import update_an_offer_active_status


class UpdateAnOfferActiveStatusTest:
    class ActivateAnOfferTest:
        @patch('pcapi.use_cases.update_an_offer_active_status.repository.save')
        def test_should_update_is_active_property_for_offer(self, mocked_save, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, is_active=False)

            # When
            update_an_offer_active_status(offer, True)

            # Then
            assert mocked_save.call_args[0][0].isActive == True

        @patch('pcapi.use_cases.update_an_offer_active_status.repository.save')
        @patch('pcapi.use_cases.update_an_offer_active_status.feature_queries.is_active', return_value=True)
        @patch('pcapi.use_cases.update_an_offer_active_status.redis.add_offer_id')
        def test_should_synchronize_updated_offer_with_algolia(self, mocked_add_offer_to_redis, mocked_feature_is_active, mocked_save, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, idx=1, is_active=False)

            # When
            update_an_offer_active_status(offer, True)

            # Then
            mocked_feature_is_active.assert_called_once_with(FeatureToggle.SYNCHRONIZE_ALGOLIA)
            assert mocked_add_offer_to_redis.call_args[1]['offer_id'] == offer.id


        @patch('pcapi.use_cases.update_an_offer_active_status.repository.save')
        @patch('pcapi.use_cases.update_an_offer_active_status.feature_queries.is_active', return_value=False)
        @patch('pcapi.use_cases.update_an_offer_active_status.redis.add_offer_id')
        def test_should_not_synchronize_updated_offer_with_algolia_when_feature_is_disabled(self, mocked_add_offer_to_redis, mocked_feature_is_active, mocked_save, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, idx=1, is_active=False)

            # When
            update_an_offer_active_status(offer, True)

            # Then
            mocked_add_offer_to_redis.assert_not_called()

    class DeactivateAnOfferTest:
        @patch('pcapi.use_cases.update_an_offer_active_status.repository.save')
        def test_should_update_is_active_property_for_offer(self, mocked_save, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, is_active=True)

            # When
            update_an_offer_active_status(offer, False)

            # Then
            assert mocked_save.call_args[0][0].isActive == False
