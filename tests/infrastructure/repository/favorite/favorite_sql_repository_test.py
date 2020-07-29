from domain.favorite.favorite import Favorite

from infrastructure.repository.favorite.favorite_sql_repository import FavoriteSQLRepository

from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_user, \
    create_venue, create_mediation, create_favorite
from tests.model_creators.specific_creators import create_offer_with_thing_product


class FindByBeneficiaryTest:
    def setup_method(self):
        self.favorite_sql_repository = FavoriteSQLRepository()

    @clean_database
    def test_returns_a_list_of_beneficiary_favorites(self, app):
        # given
        beneficiary = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer_1 = create_offer_with_thing_product(venue=venue)
        mediation_1 = create_mediation(offer=offer_1)
        favorite_1 = create_favorite(mediation=mediation_1, offer=offer_1, user=beneficiary)
        offer_2 = create_offer_with_thing_product(venue=venue)
        favorite_2 = create_favorite(offer=offer_2, user=beneficiary)
        repository.save(favorite_1, favorite_2)

        # when
        favorites = self.favorite_sql_repository.find_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 2
        assert isinstance(favorites[0], Favorite)
        assert isinstance(favorites[1], Favorite)

    @clean_database
    def test_should_not_return_favorites_of_other_beneficiary(self, app):
        # given
        beneficiary = create_user()
        other_beneficiary = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        mediation = create_mediation(offer=offer)
        favorite = create_favorite(mediation=mediation, offer=offer, user=other_beneficiary)
        repository.save(favorite)

        # when
        favorites = self.favorite_sql_repository.find_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 0
