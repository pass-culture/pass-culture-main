from typing import Dict

from domain.favorite.favorite import Favorite

from models import FavoriteSQLEntity


def to_domain(favorite_sql_entity: FavoriteSQLEntity, booking: Dict = None) -> Favorite:
    return Favorite(
            identifier=favorite_sql_entity.id,
            offer=favorite_sql_entity.offer,
            mediation=favorite_sql_entity.mediation,
            booking=booking
            )
