from datetime import datetime

from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy.orm import Load
from sqlalchemy.orm import joinedload

from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.models import FavoriteSQLEntity
from pcapi.models import Mediation
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.models import Venue
from pcapi.models.db import db
from pcapi.repository import transaction
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import favorites as serializers


@blueprint.native_v1.route("/me/favorites", methods=["GET"])
@spectree_serialize(response_model=serializers.PaginatedFavoritesResponse, api=blueprint.api)  # type: ignore
@authenticated_user_required
def get_favorites(user: User) -> serializers.PaginatedFavoritesResponse:
    favorites = (
        db.session.query(
            FavoriteSQLEntity,
            func.min(Stock.price)
            .filter(
                or_(Stock.beginningDatetime >= datetime.utcnow(), Stock.beginningDatetime == None),
                or_(Stock.bookingLimitDatetime >= datetime.utcnow(), Stock.bookingLimitDatetime == None),
            )
            .over(partition_by=Stock.offerId)
            .label("min_price"),
            func.max(Stock.price)
            .filter(
                or_(Stock.beginningDatetime >= datetime.utcnow(), Stock.beginningDatetime == None),
                or_(Stock.bookingLimitDatetime >= datetime.utcnow(), Stock.bookingLimitDatetime == None),
            )
            .over(partition_by=Stock.offerId)
            .label("max_price"),
            func.min(Stock.beginningDatetime)
            .filter(
                or_(Stock.beginningDatetime >= datetime.utcnow(), Stock.beginningDatetime == None),
                or_(Stock.bookingLimitDatetime >= datetime.utcnow(), Stock.bookingLimitDatetime == None),
            )
            .over(partition_by=Stock.offerId)
            .label("min_beginning_datetime"),
            func.max(Stock.beginningDatetime)
            .filter(
                or_(Stock.beginningDatetime >= datetime.utcnow(), Stock.beginningDatetime == None),
                or_(Stock.bookingLimitDatetime >= datetime.utcnow(), Stock.bookingLimitDatetime == None),
            )
            .over(partition_by=Stock.offerId)
            .label("max_beginning_datetime"),
        )
        .options(Load(FavoriteSQLEntity).load_only("id"))
        .join(FavoriteSQLEntity.offer)
        .join(Offer.venue)
        .join(Offer.stocks)
        .filter(
            FavoriteSQLEntity.userId == user.id,
            Stock.isSoftDeleted == False,
            Offer.isActive == True,
        )
        .distinct(FavoriteSQLEntity.id)
        .options(joinedload(FavoriteSQLEntity.offer).load_only(Offer.name, Offer.externalTicketOfficeUrl, Offer.type))
        .options(joinedload(FavoriteSQLEntity.offer).joinedload(Offer.venue).load_only(Venue.latitude, Venue.longitude))
        .options(
            joinedload(FavoriteSQLEntity.offer)
            .joinedload(Offer.mediations)
            .load_only(Mediation.dateCreated, Mediation.isActive, Mediation.thumbCount, Mediation.credit)
        )
        .options(
            joinedload(FavoriteSQLEntity.offer).joinedload(Offer.product).load_only(Product.id, Product.thumbCount)
        )
        .order_by(FavoriteSQLEntity.id)
        .all()
    )

    for fav, min_price, max_price, min_beginning_datetime, max_beginning_datetime in favorites:
        fav.offer.price = None
        fav.offer.startPrice = None
        if min_price == max_price:
            fav.offer.price = min_price
        else:
            fav.offer.startPrice = min_price
        fav.offer.date = None
        fav.offer.startDate = None
        if min_beginning_datetime == max_beginning_datetime:
            fav.offer.date = min_beginning_datetime
        else:
            fav.offer.startDate = min_beginning_datetime
    favorites = [fav for (fav, *_) in favorites]

    paginated_favorites = {
        "page": 1,
        "nbFavorites": len(favorites),
        "favorites": favorites,
    }
    return serializers.PaginatedFavoritesResponse(**paginated_favorites)


@blueprint.native_v1.route("/me/favorites", methods=["POST"])
@spectree_serialize(response_model=serializers.FavoriteResponse, on_error_statuses=[400], api=blueprint.api)  # type: ignore
@authenticated_user_required
def create_favorite(user: User, body: serializers.FavoriteRequest) -> serializers.FavoriteResponse:
    with transaction():
        offer = Offer.query.filter_by(id=body.offerId).first_or_404()

        favorite = FavoriteSQLEntity(
            mediation=offer.activeMediation,
            offer=offer,
            user=user,
        )
        db.session.add(favorite)
        db.session.flush()
        return serializers.FavoriteResponse.from_orm(favorite)


@blueprint.native_v1.route("/me/favorites/<int:favorite_id>", methods=["DELETE"])
@spectree_serialize(on_success_status=204, api=blueprint.api)  # type: ignore
@authenticated_user_required
def delete_favorite(user: User, favorite_id: int) -> None:
    with transaction():
        favorite = FavoriteSQLEntity.query.filter_by(id=favorite_id, user=user).first_or_404()
        db.session.delete(favorite)
