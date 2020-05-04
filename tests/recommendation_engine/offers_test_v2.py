from unittest.mock import patch

from recommendations_engine import get_offers_for_recommendations_discovery
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product


class GetOffersForRecommendationsDiscoveryTest:
    @patch('recommendations_engine.offers.get_offers_for_recommendation')
    @clean_database
    def test_should_get_offers_for_recommendation_from_user_department_when_user_is_authenticated(self, get_offers_for_recommendation, app):
        # Given
        seen_recommendation_ids = []
        authenticated_user = create_user(departement_code='54')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        get_offers_for_recommendation.return_value = [offer]

        # When
        offers = get_offers_for_recommendations_discovery(limit=5,
                                                          seen_recommendation_ids=seen_recommendation_ids,
                                                          user=authenticated_user)

        # Then
        get_offers_for_recommendation.assert_called_once_with(departement_codes=['54'],
                                                              limit=5,
                                                              seen_recommendation_ids=seen_recommendation_ids,
                                                              user=authenticated_user)
        assert offers == [offer]
