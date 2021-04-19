from pcapi.domain.favorite.favorite import FavoriteDomain
from pcapi.models import Favorite


def to_domain(favorite_sql_entity: Favorite, booking: dict = None) -> FavoriteDomain:
    return FavoriteDomain(
        identifier=favorite_sql_entity.id,
        offer=favorite_sql_entity.offer,
        mediation=favorite_sql_entity.mediation,
        booking=booking,
    )
