from pcapi.core.favorites import exceptions
from pcapi.core.favorites import models
from pcapi.core.favorites import repository
from pcapi.core.offers import repository as offers_repository
from pcapi.core.users import models as users_models


def get_favorite_offers_for(
    user: users_models.User,
    favorite_id: int | None = None,
    offer_id: int | None = None,
) -> list[models.FavoriteOfferData]:
    return repository.get_favorite_offers_for(user, favorite_id, offer_id)


def set_offer_as_favorite(
    user: users_models.User,
    offer_id: int,
) -> models.FavoriteOffer:
    if repository.has_reached_max_favorites_for("offer", user):
        raise exceptions.MaxFavoritesReached

    offer = offers_repository.get_offer_by_id(offer_id, load_options={"venue"})

    if not (offer.venue.managingOfferer.isActive and offer.venue.managingOfferer.isValidated):
        raise exceptions.InactiveOffer

    if not offer.isPublished:
        raise exceptions.InactiveOffer

    fav, is_inserted = repository.create_favorite_offer(user, offer)
    if not is_inserted:
        raise exceptions.AlreadyAsFavorite

    return fav


def delete_favorite_offer(
    user: users_models.User,
    favorite_id: int,
) -> None:
    favorite = repository.get_favorite_offers_for(user, favorite_id=favorite_id)
    if not favorite:
        raise exceptions.FavoriteNotFound

    repository.delete_favorite("offer", favorite_id)
