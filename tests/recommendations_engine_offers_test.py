import pytest
from typing import List

from models import PcObject, Offerer, Stock
from recommendations_engine import create_recommendations_for_discovery
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_venue, create_offer_with_thing_product, create_stock


@pytest.mark.standalone
class CreateRecommendationsForDiscoveryTest:
    @clean_database
    def test_returns_offer_in_all_ile_de_france_for_user_from_93(self, app):
        # given
        departements_ok = ['75', '77', '78', '91', '92', '93', '94', '95']
        departements_ko = ['34', '973']

        user = create_user(departement_code='93')
        offerer_ok = create_offerer()
        offerer_ko = create_offerer(siren='987654321')
        expected_stocks_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ok,
                                                                                           departements_ok)
        expected_stocks_not_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ko,
                                                                                               departements_ko)
        PcObject.check_and_save(user)
        PcObject.check_and_save(*(expected_stocks_recommended + expected_stocks_not_recommended))
        offer_ids_in_adjacent_department = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(user=user, limit=10)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 8
        assert recommended_offer_ids == offer_ids_in_adjacent_department

    @clean_database
    def test_returns_offers_from_any_departement_for_user_from_00(self, app):
        # given
        departements_ok = ['97', '01', '93', '06', '78']

        user = create_user(departement_code='00')
        offerer_ok = create_offerer()
        expected_stocks_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ok,
                                                                                           departements_ok)
        PcObject.check_and_save(user)
        PcObject.check_and_save(*expected_stocks_recommended)
        offer_ids_in_adjacent_department = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(user=user, limit=10)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 5
        assert recommended_offer_ids == offer_ids_in_adjacent_department


def _create_and_save_stock_for_offererer_in_departements(offerer: Offerer, departement_codes: List[str]) -> Stock:
    stock_list = []
    for i, departement_code in enumerate(departement_codes):
        siret = f'{offerer.siren}{99999 - i}'
        venue = create_venue(offerer, postal_code="{:<5}".format(departement_code), siret=siret)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, available=10)
        stock_list.append(stock)
    return stock_list
