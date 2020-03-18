from datetime import datetime
from unittest.mock import patch

from recommendations_engine import get_offers_for_recommendations_discovery
from repository.offer_queries import order_by_with_criteria
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product


class GetOffersForRecommendationsDiscoveryTest:
    @patch('recommendations_engine.offers.feature_queries.is_active', return_value=False)
    @patch('recommendations_engine.offers.get_active_offers')
    @clean_database
    def test_should_get_active_offers_from_user_department_when_user_is_authenticated(self, mock_get_active_offers,
                                                                                      mock_is_feature_active,
                                                                                      app):
        # Given
        authenticated_user = create_user(departement_code='54')
        pagination_params = {'page': 2, 'seed': 0.1}
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        mock_get_active_offers.return_value = [offer]

        # When
        offers = get_offers_for_recommendations_discovery(limit=5,
                                                          pagination_params=pagination_params,
                                                          user=authenticated_user)

        # Then
        mock_get_active_offers.assert_called_once_with(departement_codes=['54'],
                                                       limit=5,
                                                       order_by=order_by_with_criteria,
                                                       pagination_params=pagination_params,
                                                       user=authenticated_user)
        assert offers == [offer]

    @patch('recommendations_engine.offers.feature_queries.is_active', return_value=True)
    @patch('recommendations_engine.offers.get_active_offers_with_digital_first')
    @clean_database
    def test_should_get_active_offers_with_digital_first_when_feature_is_active(self,
                                                                                mock_get_active_offers,
                                                                                mock_is_feature_active,
                                                                                app):
        # Given
        authenticated_user = create_user(departement_code='54')
        pagination_params = {'page': 2, 'seed': 0.1}
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        mock_get_active_offers.return_value = [offer]
        end_of_quarantine_date = datetime(year=2020, month=4, day=25)

        # When
        offers = get_offers_for_recommendations_discovery(limit=5,
                                                          pagination_params=pagination_params,
                                                          user=authenticated_user)

        # Then
        mock_get_active_offers.assert_called_once_with(departement_codes=['54'],
                                                       limit=5,
                                                       pagination_params=pagination_params,
                                                       user=authenticated_user,
                                                       end_of_quarantine_date=end_of_quarantine_date)
        assert offers == [offer]
