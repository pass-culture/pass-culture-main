from unittest.mock import patch, call

from pcapi.models.feature import FeatureToggle
from pcapi.model_creators.generic_creators import create_offerer, create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.use_cases.update_offers_active_status import update_offers_active_status, update_all_offers_active_status
from pcapi.domain.pro_offers.offers_status_filters import OffersStatusFilters


class UpdateOffersIsActiveStatusTest:
    class ActivateOffersTest:
        @patch('pcapi.use_cases.update_offers_active_status.update_offers_is_active_status')
        def test_should_update_is_active_property_for_given_offers(self, mocked_update, app):
            # Given
            offers_id = [1, 2]

            # When
            update_offers_active_status(offers_id, True)

            # Then
            assert mocked_update.call_args[0][0] == offers_id
            assert mocked_update.call_args[0][1] == True

        @patch('pcapi.use_cases.update_offers_active_status.update_offers_is_active_status')
        @patch('pcapi.use_cases.update_offers_active_status.feature_queries.is_active', return_value=True)
        @patch('pcapi.use_cases.update_offers_active_status.redis.add_offer_id')
        def test_should_synchronize_updated_offers_with_algolia(self, mocked_add_offer_to_redis, mocked_feature_is_active, mocked_update, app):
            # Given
            offers_id = [1, 2]

            # When
            update_offers_active_status(offers_id, True)

            # Then
            mocked_feature_is_active.assert_called_once_with(FeatureToggle.SYNCHRONIZE_ALGOLIA)
            assert mocked_add_offer_to_redis.call_args_list == [
                call(client=app.redis_client, offer_id=offers_id[0]),
                call(client=app.redis_client, offer_id=offers_id[1])
            ]


        @patch('pcapi.use_cases.update_offers_active_status.update_offers_is_active_status')
        @patch('pcapi.use_cases.update_offers_active_status.feature_queries.is_active', return_value=False)
        @patch('pcapi.use_cases.update_offers_active_status.redis.add_offer_id')
        def test_should_not_synchronize_updated_offer_with_algolia_when_feature_is_disabled(self, mocked_add_offer_to_redis, mocked_feature_is_active, mocked_update, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue, idx=1, is_active=False)

            # When
            update_offers_active_status(offer, True)

            # Then
            mocked_add_offer_to_redis.assert_not_called()

    class DeactivateOffersTest:
        @patch('pcapi.use_cases.update_offers_active_status.update_offers_is_active_status')
        def test_should_update_is_active_property_for_offer(self, mocked_update, app):
            # Given
            offers_id = [1, 2]

            # When
            update_offers_active_status(offers_id, False)

            # Then
            assert mocked_update.call_args[0][0] == offers_id
            assert mocked_update.call_args[0][1] == False

class UpdateAllOffersIsActiveStatusTest:
    @patch('pcapi.use_cases.update_offers_active_status.get_all_offers_id_by_filters')
    @patch('pcapi.use_cases.update_offers_active_status.update_offers_is_active_status')
    @patch('pcapi.use_cases.update_offers_active_status.feature_queries.is_active', return_value=True)
    @patch('pcapi.use_cases.update_offers_active_status.redis.add_offer_id')
    def test_should_get_all_offers_filtered_by_params_and_call_update(self, mocked_add_offer_to_redis, mocked_feature_is_active, mocked_update, mocked_get, app):
        # Given
        mocked_get.return_value = [1, 2]
        status_filters = OffersStatusFilters()

        # When
        update_all_offers_active_status(user_id=12, user_is_admin=True, is_active=True, status_filters=status_filters)

        # Then
        mocked_get.assert_called_once_with(12, True, None, status_filters, None, None)
        mocked_update.assert_called_once_with([1, 2], True)
        mocked_feature_is_active.assert_called_once_with(FeatureToggle.SYNCHRONIZE_ALGOLIA)
        assert mocked_add_offer_to_redis.call_args_list == [
            call(client=app.redis_client, offer_id=1),
            call(client=app.redis_client, offer_id=2)
        ]
