import pytest
from typing import List

from models import PcObject, Offerer, Stock
from recommendations_engine import create_recommendations_for_discovery
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_venue, create_thing_offer, create_stock


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
        expected_offer_ids = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(user=user, limit=10)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 8
        assert recommended_offer_ids == expected_offer_ids

    @clean_database
    def test_returns_offer_in_22_25_29_56_for_user_from_29(self, app):
        # given
        departements_ok = ['22', '25', '29', '56']
        departements_ko = ['34', '973', '75']

        user = create_user(departement_code='29')
        offerer_ok = create_offerer()
        offerer_ko = create_offerer(siren='987654321')
        expected_stocks_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ok,
                                                                                           departements_ok)
        expected_stocks_not_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ko,
                                                                                               departements_ko)
        PcObject.check_and_save(user)
        PcObject.check_and_save(*(expected_stocks_recommended + expected_stocks_not_recommended))
        expected_offer_ids = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(user=user, limit=10)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 4
        assert recommended_offer_ids == expected_offer_ids

    @clean_database
    def test_returns_offer_in_54_55_57_67_68_88_for_user_from_67(self, app):
        # given
        departements_ok = ['54', '55', '57', '67', '68', '88']
        departements_ko = ['34', '973', '75']

        user = create_user(departement_code='67')
        offerer_ok = create_offerer()
        offerer_ko = create_offerer(siren='987654321')
        expected_stocks_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ok,
                                                                                           departements_ok)
        expected_stocks_not_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ko,
                                                                                               departements_ko)
        PcObject.check_and_save(user)
        PcObject.check_and_save(*(expected_stocks_recommended + expected_stocks_not_recommended))
        expected_offer_ids = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(user=user, limit=10)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 6
        assert recommended_offer_ids == expected_offer_ids

    @clean_database
    def test_returns_offer_in_11_12_30_34_48_81_for_user_from_34(self, app):
        # given
        departements_ok = ['11', '12', '30', '34', '48', '81']
        departements_ko = ['67', '973', '75']

        user = create_user(departement_code='34')
        offerer_ok = create_offerer()
        offerer_ko = create_offerer(siren='987654321')
        expected_stocks_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ok,
                                                                                           departements_ok)
        expected_stocks_not_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ko,
                                                                                               departements_ko)
        PcObject.check_and_save(user)
        PcObject.check_and_save(*(expected_stocks_recommended + expected_stocks_not_recommended))
        expected_offer_ids = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(user=user, limit=10)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 6
        assert recommended_offer_ids == expected_offer_ids

    @clean_database
    def test_returns_offer_in_97_971_972_973_for_user_from_97(self, app):
        # given
        departements_ok = ['97', '971', '972', '973']
        departements_ko = ['67', '34', '75']

        user = create_user(departement_code='97')
        offerer_ok = create_offerer()
        offerer_ko = create_offerer(siren='987654321')
        expected_stocks_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ok,
                                                                                           departements_ok)
        expected_stocks_not_recommended = _create_and_save_stock_for_offererer_in_departements(offerer_ko,
                                                                                               departements_ko)
        PcObject.check_and_save(user)
        PcObject.check_and_save(*(expected_stocks_recommended + expected_stocks_not_recommended))
        expected_offer_ids = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(user=user, limit=10)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 4
        assert recommended_offer_ids == expected_offer_ids

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
        expected_offer_ids = set([stock.offerId for stock in expected_stocks_recommended])

        #  when
        recommendations = create_recommendations_for_discovery(user=user, limit=10)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 5
        assert recommended_offer_ids == expected_offer_ids

    @clean_database
    def test_returns_offers_only_from_user_departement_for_user_from_remaining_departements(self, app):
        # given
        departements = ['97', '01', '93', '06', '78', '75', '13']

        user = create_user(departement_code='01')
        offerer = create_offerer()
        stocks = _create_and_save_stock_for_offererer_in_departements(offerer,
                                                                      departements)
        PcObject.check_and_save(user)
        PcObject.check_and_save(*stocks)

        #  when
        recommendations = create_recommendations_for_discovery(user=user, limit=10)

        # then
        recommended_offer_ids = set([recommendation.offerId for recommendation in recommendations])
        assert len(recommendations) == 1
        assert recommended_offer_ids == set(
            [stock.offerId for stock in stocks if stock.offer.venue.departementCode == '01'])


def _create_and_save_stock_for_offererer_in_departements(offerer: Offerer, departement_codes: List[str]) -> Stock:
    stock_list = []
    for i, departement_code in enumerate(departement_codes):
        siret = f'{offerer.siren}{99999 - i}'
        venue = create_venue(offerer, postal_code="{:<5}".format(departement_code), siret=siret)
        offer = create_thing_offer(venue)
        stock = create_stock(offer=offer, available=10)
        stock_list.append(stock)
    return stock_list
