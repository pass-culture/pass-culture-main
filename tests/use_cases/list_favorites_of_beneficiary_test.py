from unittest.mock import MagicMock

from tests.domain_creators.generic_creators import create_domain_favorite
from model_creators.generic_creators import create_offerer, create_venue
from model_creators.specific_creators import create_offer_with_thing_product

from infrastructure.repository.favorite.favorite_sql_repository import FavoriteSQLRepository
from use_cases.list_favorites_of_beneficiary import ListFavoritesOfBeneficiary


class ListFavoritesOfBeneficiaryTest:
    def setup_method(self):
        self.favorite_repository = FavoriteSQLRepository()
        self.favorite_repository.find_by_beneficiary = MagicMock()
        self.list_favorites_of_beneficiary = ListFavoritesOfBeneficiary(self.favorite_repository)

    def test_should_retrieve_beneficiary_favorites(self, app):
        # Given
        beneficiary_identifier = 111
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        favorite = create_domain_favorite(identifier=1, offer=offer)
        self.favorite_repository.find_by_beneficiary.return_value = [favorite]

        # When
        favorites = self.list_favorites_of_beneficiary.execute(beneficiary_identifier)

        # Then
        self.favorite_repository.find_by_beneficiary.assert_called_once_with(beneficiary_identifier)
        assert favorites == [favorite]
