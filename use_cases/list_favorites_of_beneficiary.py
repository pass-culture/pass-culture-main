from typing import List

from domain.favorite.favorite_repository import FavoriteRepository
from models import FavoriteSQLEntity


class ListFavoritesOfBeneficiary:
    def __init__(self, favorite_repository: FavoriteRepository):
        self.favorite_repository = favorite_repository

    def execute(self, beneficiary_identifier: int) -> List[FavoriteSQLEntity]:
        return self.favorite_repository.find_by_beneficiary(beneficiary_identifier)
