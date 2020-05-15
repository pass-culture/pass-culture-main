from typing import List
from unittest.mock import patch

from recommendations_engine import give_requested_recommendation_to_user, create_recommendations_for_discovery
from models import Offerer, StockSQLEntity
from repository import repository, discovery_view_queries
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_stock, create_offerer, create_venue, \
    create_recommendation, create_mediation
from tests.model_creators.specific_creators import create_stock_from_offer, create_offer_with_thing_product
from utils.human_ids import humanize


class CreateRecommendationsForDiscoveryTest:
    @clean_database
    def test_does_not_put_mediation_ids_of_inactive_mediations(self, app):
        # Given
        sent_offers_ids = []
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
        discovery_view_queries.refresh(concurrently=False)

        # When
        recommendations = create_recommendations_for_discovery(sent_offers_ids=sent_offers_ids,
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
        sent_offers_ids = []
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
        discovery_view_queries.refresh(concurrently=False)

        # When
        recommendations = create_recommendations_for_discovery(sent_offers_ids=sent_offers_ids,
                                                               user=user)

        # Then
        assert len(recommendations) == 2

    @patch('recommendations_engine.recommendations.get_offers_for_recommendations_discovery')
    def test_should_get_offers_using_pagination_when_query_params_provided(self,
                                                                           get_offers_for_recommendations_discovery,
                                                                           app):
        # Given
        sent_offers_ids = []
        user = create_user()

        # When
        create_recommendations_for_discovery(user=user, sent_offers_ids=sent_offers_ids)

        # Then
        get_offers_for_recommendations_discovery.assert_called_once_with(limit=3,
                                                                         sent_offers_ids=sent_offers_ids,
                                                                         user=user)

    @clean_database
    def test_returns_offer_in_all_ile_de_france_for_user_from_93(self, app):
        # given
        departements_ok = ['75', '77', '78', '91', '92', '93', '94', '95']
        departements_ko = ['34', '973']
        sent_offers_ids = []

        user = create_user(departement_code='93')
        offerer_ok = create_offerer()
        offerer_ko = create_offerer(siren='987654321')
        expected_stocks_recommended = _create_and_save_stock_for_offerer_in_departements(offerer_ok,
                                                                                         departements_ok)
        expected_stocks_not_recommended = _create_and_save_stock_for_offerer_in_departements(offerer_ko,
                                                                                             departements_ko)
        repository.save(user)
        repository.save(*(expected_stocks_recommended + expected_stocks_not_recommended))
        discovery_view_queries.refresh(concurrently=False)

        offer_ids_in_adjacent_department = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(sent_offers_ids=sent_offers_ids,
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
        sent_offers_ids = []

        user = create_user(departement_code='00')
        offerer_ok = create_offerer()
        expected_stocks_recommended = _create_and_save_stock_for_offerer_in_departements(offerer_ok,
                                                                                         departements_ok)
        repository.save(user)
        repository.save(*expected_stocks_recommended)
        discovery_view_queries.refresh(concurrently=False)

        offer_ids_in_all_department = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(limit=10,
                                                               sent_offers_ids=sent_offers_ids,
                                                               user=user)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 5
        assert recommended_offer_ids == offer_ids_in_all_department


class GiveRequestedRecommendationToUserTest:
    @clean_database
    def test_when_recommendation_exists_returns_it(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_ok = create_offer_with_thing_product(venue, thumb_count=0)
        stock = create_stock_from_offer(offer_ok, price=0)
        mediation = create_mediation(offer_ok, is_active=False)
        reco_ok = create_recommendation(offer=offer_ok, user=user, mediation=mediation)
        repository.save(reco_ok, stock)

        # When
        result_reco = give_requested_recommendation_to_user(
            user, offer_ok.id, mediation.id)

        # Then
        assert result_reco.id == reco_ok.id

    @clean_database
    def test_when_recommendation_exists_for_other_user_returns_a_new_one_for_the_current_user(self, app):
        # Given
        user = create_user()
        user2 = create_user(email='john.doe2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_ok = create_offer_with_thing_product(venue, thumb_count=0)
        stock = create_stock_from_offer(offer_ok, price=0)
        mediation = create_mediation(offer_ok, is_active=False)
        reco_ko = create_recommendation(offer=offer_ok, user=user, mediation=mediation)
        repository.save(reco_ko, stock, user2)

        # When
        result_reco = give_requested_recommendation_to_user(
            user2, offer_ok.id, mediation.id)

        # Then
        assert result_reco.id != reco_ko.id
        assert result_reco.offerId == offer_ok.id
        assert result_reco.mediationId == mediation.id
        assert result_reco.userId == user2.id


def _create_and_save_stock_for_offerer_in_departements(offerer: Offerer, departement_codes: List[str]) -> List[
    StockSQLEntity]:
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
