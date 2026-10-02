from flask_login import current_user

from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.external.batch.trigger_events import track_offer_added_to_favorites_event
from pcapi.core.favorites import api
from pcapi.core.favorites import exceptions as favorites_exceptions
from pcapi.core.favorites.api import get_favorite_offers_for
from pcapi.core.favorites.api import set_offer_as_favorite
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.exceptions import OfferNotFound
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.api_errors import resource_not_found_error
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import favorites as serializers


@blueprint.native_route("/me/favorites", methods=["GET"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.PaginatedFavoritesResponse, api=blueprint.api)
def get_favorites() -> serializers.PaginatedFavoritesResponse:
    favorites = api.get_favorite_offers_for(current_user)

    return serializers.PaginatedFavoritesResponse(
        page=1,
        nb_favorites=len(favorites),
        favorites=[
            serializers.FavoriteResponse(
                id=favorite_data.favorite.id,
                offer=serializers.FavoriteOfferResponse.build(favorite_data),
            )
            for favorite_data in favorites
        ],
    )


@blueprint.native_route("/me/favorites", methods=["POST"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.FavoriteResponse, on_error_statuses=[400], api=blueprint.api)
def create_favorite(body: serializers.FavoriteRequest) -> serializers.FavoriteResponse:
    should_track = True

    try:
        set_offer_as_favorite(current_user, body.offer_id)
    except favorites_exceptions.AlreadyAsFavorite:
        should_track = False
    except favorites_exceptions.MaxFavoritesReached:
        raise ApiErrors({"code": "MAX_FAVORITES_REACHED"})
    except OfferNotFound as exception:
        raise ResourceNotFoundError() from exception
    except favorites_exceptions.InactiveOffer:
        raise ResourceNotFoundError()

    if should_track:
        update_external_user(current_user)
        offer = offers_repository.get_offer_by_id(body.offer_id)
        track_offer_added_to_favorites_event(current_user.id, offer)

    favorite_data = get_favorite_offers_for(current_user, offer_id=body.offer_id)[0]

    return serializers.FavoriteResponse(
        id=favorite_data.favorite.id,
        offer=serializers.FavoriteOfferResponse.build(favorite_data),
    )


@blueprint.native_route("/me/favorites/<int:favorite_id>", methods=["DELETE"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(on_success_status=204, api=blueprint.api)
def delete_favorite(favorite_id: int) -> None:
    try:
        api.delete_favorite_offer(current_user, favorite_id)
    except favorites_exceptions.FavoriteNotFound:
        raise resource_not_found_error()
