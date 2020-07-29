from typing import List

from domain.favorite.favorite import Favorite
from domain.favorite.favorite_repository import FavoriteRepository


class ListFavoritesOfBeneficiary:
    def __init__(self, favorite_repository: FavoriteRepository):
        self.favorite_repository = favorite_repository

    def execute(self, beneficiary_identifier: int) -> List[Favorite]:
        return self.favorite_repository.find_by_beneficiary(beneficiary_identifier)
