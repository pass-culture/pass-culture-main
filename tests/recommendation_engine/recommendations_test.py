from typing import List

from models import Offerer, Stock
from recommendations_engine import give_requested_recommendation_to_user
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_stock, create_offerer, create_venue, \
    create_recommendation, create_mediation
from tests.model_creators.specific_creators import create_stock_from_offer, create_offer_with_thing_product


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
