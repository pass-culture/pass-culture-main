from typing import List

from pcapi.domain.favorite.favorite import FavoriteDomain
from pcapi.domain.favorite.favorite_repository import FavoriteRepository


class ListFavoritesOfBeneficiary:
    def __init__(self, favorite_repository: FavoriteRepository):
        self.favorite_repository = favorite_repository

    def execute(self, beneficiary_identifier: int) -> List[FavoriteDomain]:
        return self.favorite_repository.find_by_beneficiary(beneficiary_identifier)
