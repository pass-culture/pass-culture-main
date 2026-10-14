from flask_login import current_user

from pcapi.core.favorites import api as favorites_api
from pcapi.core.favorites.models import FavoriteOffer
from pcapi.core.favorites.repository import get_favorites_for
from pcapi.models import db
from pcapi.models.utils import first_or_404
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
    favorites = get_favorites_for(current_user)

    return serializers.PaginatedFavoritesResponse(
        page=1,
        nb_favorites=len(favorites),
        favorites=[serializers.FavoriteResponse.build(favorite_data) for favorite_data in favorites],
    )


@blueprint.native_route("/me/favorites", methods=["POST"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.FavoriteResponse, on_error_statuses=[400, 404], api=blueprint.api)
def create_favorite(body: serializers.FavoriteRequest) -> serializers.FavoriteResponse:
    favorite_id = favorites_api.create_favorite(current_user, body)
    favorite_data = get_favorites_for(current_user, favorite_id)[0]
    return serializers.FavoriteResponse.build(favorite_data)


@blueprint.native_route("/me/favorites/<int:favorite_id>", methods=["DELETE"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(on_success_status=204, on_error_statuses=[404], api=blueprint.api)
def delete_favorite(favorite_id: int) -> None:
    favorite = first_or_404(db.session.query(FavoriteOffer).filter_by(id=favorite_id, user=current_user))
    db.session.delete(favorite)
