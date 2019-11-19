from unittest.mock import patch

from models import PcObject
from recommendations_engine import create_recommendations_for_discovery, get_offers_for_recommendations_discovery
from repository.offer_queries import order_by_with_criteria
from tests.conftest import clean_database
from tests.recommendation_engine.recommendations_test import _create_and_save_stock_for_offerer_in_departements
from tests.test_utils import create_user, create_offer_with_thing_product, create_venue, create_offerer


class GetOffersForRecommendationsDiscoveryTest:
    @clean_database
    def test_returns_offers_from_any_departement_for_user_from_00(self, app):
        # given
        departements_ok = ['973', '01', '93', '06', '78']

        user = create_user(departement_code='00')
        offerer_ok = create_offerer()
        expected_stocks_recommended = _create_and_save_stock_for_offerer_in_departements(offerer_ok,
                                                                                         departements_ok)
        PcObject.save(user)
        PcObject.save(*expected_stocks_recommended)
        offer_ids_in_adjacent_department = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(limit=10,
                                                               pagination_params={'page': 1, 'seed': 0.5},
                                                               user=user)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 5
        assert recommended_offer_ids == offer_ids_in_adjacent_department

    @patch('recommendations_engine.offers.get_active_offers')
    def test_should_get_active_offers_from_user_department_when_user_is_authenticated(self, get_active_offers):
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
