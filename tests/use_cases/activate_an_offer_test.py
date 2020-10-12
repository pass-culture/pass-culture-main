from unittest.mock import MagicMock

from pcapi.connectors import redis
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository, feature_queries
from pcapi.model_creators.generic_creators import create_offerer, create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.use_cases.activate_an_offer import activate_an_offer


class ActivateAnOfferTest:
    def test_should_update_is_active_property_for_offer(self, app):
        # Given
        repository.save = MagicMock()

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=False)

        # When
        activate_an_offer(offer)

        # Then
        assert repository.save.call_args[0][0].isActive == True

    def test_should_synchronize_updated_offer_with_algolia(self, app):
        # Given
        repository.save = MagicMock()
        feature_queries.is_active = MagicMock(return_value=True)
        redis.add_offer_id = MagicMock()

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, idx=1, is_active=False)

        # When
        activate_an_offer(offer)

        # Then
        assert redis.add_offer_id.call_args[1]['offer_id'] == offer.id
        feature_queries.is_active.assert_called_once_with(FeatureToggle.SYNCHRONIZE_ALGOLIA)

    def test_should_not_synchronize_updated_offer_with_algolia_when_feature_is_disabled(self, app):
        # Given
        repository.save = MagicMock()
        feature_queries.is_active = MagicMock(return_value=False)
        redis.add_offer_id = MagicMock()

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, idx=1, is_active=False)

        # When
        activate_an_offer(offer)

        # Then
        redis.add_offer_id.assert_not_called()
