from unittest.mock import patch

from recommendations_engine import get_offers_for_recommendations_discovery
from repository.offer_queries import order_by_with_criteria
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product


class GetOffersForRecommendationsDiscoveryTest:
    @patch('recommendations_engine.offers.get_active_offers')
    @clean_database
    def test_should_get_active_offers_from_user_department_when_user_is_authenticated(self, get_active_offers, app):
        # Given
        authenticated_user = create_user(departement_code='54')
        pagination_params = {'page': 2, 'seed': 0.1}
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        get_active_offers.return_value = [offer]

        # When
        offers = get_offers_for_recommendations_discovery(limit=5,
                                                          pagination_params=pagination_params,
                                                          user=authenticated_user)

        # Then
        get_active_offers.assert_called_once_with(departement_codes=['54'],
                                                  limit=5,
                                                  order_by=order_by_with_criteria,
                                                  pagination_params=pagination_params,
                                                  user=authenticated_user)
        assert offers == [offer]
