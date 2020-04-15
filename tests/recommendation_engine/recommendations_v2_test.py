from typing import List
from unittest.mock import patch

from models import Offerer, Stock
from models.discovery_view import DiscoveryView
from recommendations_engine import create_recommendations_for_discovery_v2
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_mediation, \
    create_offerer, create_recommendation, \
    create_stock, create_user, create_venue
from tests.model_creators.specific_creators import \
    create_offer_with_thing_product, create_stock_from_offer
from utils.human_ids import humanize


class CreateRecommendationsForDiscoveryTest:
    @clean_database
    def test_does_not_put_mediation_ids_of_inactive_mediations(self, app):
        # Given
        seen_recommendation_ids = []
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        stock1 = create_stock_from_offer(offer1, price=0)
        mediation1 = create_mediation(offer1, is_active=False)
        offer2 = create_offer_with_thing_product(venue)
        stock2 = create_stock_from_offer(offer2, price=0)
        mediation2 = create_mediation(offer2, is_active=False)
        mediation3 = create_mediation(offer2, is_active=True)
        repository.save(user, stock1, mediation1, stock2, mediation2, mediation3)
        DiscoveryView.refresh(concurrently=False)

        # When
        recommendations = create_recommendations_for_discovery_v2(seen_recommendation_ids=seen_recommendation_ids,
                                                                  user=user)

        # Then
        mediations = list(map(lambda x: x.mediationId, recommendations))
        assert len(recommendations) == 1
        assert mediation3.id in mediations
        assert humanize(mediation2.id) not in mediations
        assert humanize(mediation1.id) not in mediations

    @clean_database
    def test_should_include_recommendations_on_offers_previously_displayed_in_search_results(
            self, app):
        # Given
        seen_recommendation_ids = []
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, thumb_count=0)
        stock1 = create_stock_from_offer(offer1, price=0)
        mediation1 = create_mediation(offer1, is_active=True)
        offer2 = create_offer_with_thing_product(venue, thumb_count=0)
        stock2 = create_stock_from_offer(offer2, price=0)
        mediation2 = create_mediation(offer2, is_active=True)

        recommendation = create_recommendation(offer=offer2, user=user, mediation=mediation2, search="bla")

        repository.save(user, stock1, mediation1, stock2, mediation2, recommendation)
        DiscoveryView.refresh(concurrently=False)

        # When
        recommendations = create_recommendations_for_discovery_v2(seen_recommendation_ids=seen_recommendation_ids, user=user)

        # Then
        assert len(recommendations) == 2

    @patch('recommendations_engine.recommendations.get_offers_for_recommendations_discovery_v2')
    def test_should_get_offers_using_pagination_when_query_params_provided(self,
                                                                           get_offers_for_recommendations_discovery_v2,
                                                                           app):
        # Given
        seen_recommendation_ids = []
        user = create_user()

        # When
        create_recommendations_for_discovery_v2(user=user, seen_recommendation_ids=seen_recommendation_ids)

        # Then
        get_offers_for_recommendations_discovery_v2.assert_called_once_with(limit=3,
                                                                            seen_recommendation_ids=seen_recommendation_ids,
                                                                            user=user)

    @clean_database
    def test_returns_offer_in_all_ile_de_france_for_user_from_93(self, app):
        # given
        departements_ok = ['75', '77', '78', '91', '92', '93', '94', '95']
        departements_ko = ['34', '973']
        seen_recommendation_ids = []

        user = create_user(departement_code='93')
        offerer_ok = create_offerer()
        offerer_ko = create_offerer(siren='987654321')
        expected_stocks_recommended = _create_and_save_stock_for_offerer_in_departements(offerer_ok,
                                                                                         departements_ok)
        expected_stocks_not_recommended = _create_and_save_stock_for_offerer_in_departements(offerer_ko,
                                                                                             departements_ko)
        repository.save(user)
        repository.save(*(expected_stocks_recommended + expected_stocks_not_recommended))
        DiscoveryView.refresh(concurrently=False)

        offer_ids_in_adjacent_department = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery_v2(seen_recommendation_ids=seen_recommendation_ids,
                                                                  limit=10,
                                                                  user=user)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 8
        assert recommended_offer_ids == offer_ids_in_adjacent_department

    @clean_database
    def test_returns_offers_from_any_departement_for_user_from_00(self, app):
        # given
        departements_ok = ['97', '01', '93', '06', '78']
        seen_recommendation_ids = []

        user = create_user(departement_code='00')
        offerer_ok = create_offerer()
        expected_stocks_recommended = _create_and_save_stock_for_offerer_in_departements(offerer_ok,
                                                                                         departements_ok)
        repository.save(user)
        repository.save(*expected_stocks_recommended)
        DiscoveryView.refresh(concurrently=False)

        offer_ids_in_all_department = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery_v2(limit=10,
                                                                  seen_recommendation_ids=seen_recommendation_ids,
                                                                  user=user)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 5
        assert recommended_offer_ids == offer_ids_in_all_department


def _create_and_save_stock_for_offerer_in_departements(offerer: Offerer, departement_codes: List[str]) -> List[Stock]:
    stock_list = []

    for index, departement_code in enumerate(departement_codes):
        siret = f'{offerer.siren}{99999 - index}'
        venue = create_venue(offerer, postal_code="{:5}".format(departement_code), siret=siret)
        offer = create_offer_with_thing_product(venue)
        mediation = create_mediation(offer)
        repository.save(mediation)
        stock = create_stock(quantity=10, offer=offer)
        stock_list.append(stock)
    return stock_list
