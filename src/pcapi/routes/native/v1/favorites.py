from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import not_
from sqlalchemy.orm import Load
from sqlalchemy.orm import joinedload

from pcapi import settings
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.models import Favorite
from pcapi.models import Mediation
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.models import Venue
from pcapi.models.api_errors import ApiErrors
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
    stock_filters = and_(
        not_(Stock.isEventExpired),
        not_(Stock.hasBookingLimitDatetimePassed),
        Offer.isActive == True,
        Stock.isSoftDeleted == False,
    )
    favorites = (
        db.session.query(
            Favorite,
            func.min(Stock.price).filter(stock_filters).over(partition_by=Stock.offerId).label("min_price"),
            func.max(Stock.price).filter(stock_filters).over(partition_by=Stock.offerId).label("max_price"),
            func.min(Stock.beginningDatetime).filter(stock_filters).over(partition_by=Stock.offerId).label("min_begin"),
            func.max(Stock.beginningDatetime).filter(stock_filters).over(partition_by=Stock.offerId).label("max_begin"),
            # count active
            func.count(Stock.id).filter(stock_filters).over(partition_by=Stock.offerId).label("active_stock_count"),
        )
        .options(Load(Favorite).load_only("id"))
        .join(Favorite.offer)
        .join(Offer.venue)
        .outerjoin(Offer.stocks)
        .outerjoin(Stock.bookings)
        .filter(Favorite.userId == user.id)
        .distinct(Favorite.id)
        .options(joinedload(Favorite.offer).load_only(Offer.name, Offer.externalTicketOfficeUrl, Offer.type))
        .options(joinedload(Favorite.offer).joinedload(Offer.venue).load_only(Venue.latitude, Venue.longitude))
        .options(
            joinedload(Favorite.offer)
            .joinedload(Offer.mediations)
            .load_only(Mediation.dateCreated, Mediation.isActive, Mediation.thumbCount, Mediation.credit)
        )
        .options(joinedload(Favorite.offer).joinedload(Offer.product).load_only(Product.id, Product.thumbCount))
        # TODO(xordoquy): drop this join and aggregate on stock
        .options(joinedload(Favorite.offer).joinedload(Offer.stocks).joinedload(Stock.bookings))
        .order_by(Favorite.id.desc())
        .all()
    )

    for fav, min_price, max_price, min_beginning_datetime, max_beginning_datetime, active_stock_count in favorites:
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
        fav.offer.isExpired = not active_stock_count
        fav.offer.isExhausted = True
        # TODO(xordoquy): improve performance here
        for stock in fav.offer.stocks:
            if stock.isSoftDeleted:
                continue
            if stock.quantity is None or stock.remainingQuantity > 0:
                fav.offer.isExhausted = False
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
    if settings.MAX_FAVORITES:
        if Favorite.query.filter_by(user=user).count() >= settings.MAX_FAVORITES:
            raise ApiErrors({"code": "MAX_FAVORITES_REACHED"})
    with transaction():
        offer = Offer.query.filter_by(id=body.offerId).first_or_404()

        favorite = Favorite(
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
        favorite = Favorite.query.filter_by(id=favorite_id, user=user).first_or_404()
        db.session.delete(favorite)
