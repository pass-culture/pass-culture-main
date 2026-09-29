import sqlalchemy as sa
from flask_login import current_user
from sqlalchemy.dialects.postgresql import insert

from pcapi import settings
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.external.batch.trigger_events import track_offer_added_to_favorites_event
from pcapi.core.favorites.models import FavoriteOffer
from pcapi.core.favorites.repository import get_favorites_for
from pcapi.core.offers.exceptions import OfferNotFound
from pcapi.core.offers.models import Offer
from pcapi.core.offers.repository import get_offer_by_id
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
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
    if settings.MAX_FAVORITES:
        query = (
            db.session.query(
                FavoriteOffer,
            )
            .join(
                FavoriteOffer.offer,
            )
            .filter(
                FavoriteOffer.userId == current_user.id,
                Offer.isPublished,
            )
        )
        if query.count() >= settings.MAX_FAVORITES:
            raise ApiErrors({"code": "MAX_FAVORITES_REACHED"})

    try:
        offer = get_offer_by_id(body.offer_id, load_options={"venue"})
    except OfferNotFound as exception:
        raise ResourceNotFoundError() from exception

    if not (offer.venue.managingOfferer.isActive and offer.venue.managingOfferer.isValidated):
        raise ResourceNotFoundError()

    if not offer.isPublished:
        raise ResourceNotFoundError()

    stmt: sa.sql.dml.ReturningInsert = (
        insert(FavoriteOffer)
        .values({"offerId": body.offer_id, "userId": current_user.id})
        .on_conflict_do_update(
            index_elements=[FavoriteOffer.offerId, FavoriteOffer.userId],
            set_={"offerId": body.offer_id},
        )
        .returning(
            FavoriteOffer.id,
            # xmax is a "system" column that returns the transaction id that modified the row.
            # In case of insertion, no row has been modified → xmax = 0
            sa.literal_column("xmax = 0").label("is_inserted"),
        )
    )
    favorite_ids = db.session.execute(stmt).all()
    favorite_id, inserted = favorite_ids[0]

    if inserted:
        update_external_user(current_user)
        track_offer_added_to_favorites_event(current_user.id, offer)

    favorite_data = get_favorites_for(current_user, favorite_id)[0]
    return serializers.FavoriteResponse(
        id=favorite_data.favorite.id, offer=serializers.FavoriteOfferResponse.build(favorite_data)
    )


@blueprint.native_route("/me/favorites/<int:favorite_id>", methods=["DELETE"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(on_success_status=204, api=blueprint.api)
def delete_favorite(favorite_id: int) -> None:
    favorite = first_or_404(db.session.query(FavoriteOffer).filter_by(id=favorite_id, user=current_user))
    db.session.delete(favorite)
