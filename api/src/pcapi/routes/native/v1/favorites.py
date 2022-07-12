from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_
from sqlalchemy import exc
from sqlalchemy import func
from sqlalchemy import not_
from sqlalchemy.orm import Load
from sqlalchemy.orm import joinedload

from pcapi import settings
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import Favorite
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.product import Product
from pcapi.repository import transaction
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import favorites as serializers


def _fill_offer_price(
    offer: Offer,
    min_price: Decimal,
    max_price: Decimal,
) -> None:
    offer.price = None
    offer.startPrice = None
    if min_price == max_price:
        offer.price = min_price
    else:
        offer.startPrice = min_price


def _fill_offer_date(offer: Offer, min_beginning_datetime: datetime, max_beginning_datetime: datetime) -> None:
    offer.date = None
    offer.startDate = None
    if min_beginning_datetime == max_beginning_datetime:
        offer.date = min_beginning_datetime
    else:
        offer.startDate = min_beginning_datetime


def _fill_offer_expired(offer: Offer, non_expired_count: int, active_count: int) -> None:
    if active_count and not non_expired_count:
        offer.isExpired = True
    else:
        offer.isExpired = False


def _fill_favorite_offer(
    favorite: Favorite,
    min_price: Decimal,
    max_price: Decimal,
    min_beginning_datetime: datetime,
    max_beginning_datetime: datetime,
    non_expired_count: int,
    active_count: int,
) -> None:
    offer = favorite.offer
    _fill_offer_price(offer, min_price, max_price)
    _fill_offer_date(offer, min_beginning_datetime, max_beginning_datetime)
    _fill_offer_expired(offer, non_expired_count, active_count)


@blueprint.native_v1.route("/me/favorites/count", methods=["GET"])
@spectree_serialize(response_model=serializers.FavoritesCountResponse, api=blueprint.api)
@authenticated_and_active_user_required
def get_favorites_count(user: User) -> serializers.FavoritesCountResponse:
    return serializers.FavoritesCountResponse(count=Favorite.query.filter_by(user=user).count())


def get_favorites_for(user: User, favorite_id: int | None = None) -> list[Favorite]:
    active_stock_filters = and_(
        Offer.isActive == True,
        Stock.isSoftDeleted == False,
    )
    stock_filters = and_(
        not_(Stock.isEventExpired),
        not_(Stock.hasBookingLimitDatetimePassed),
        active_stock_filters,
    )
    query = (
        db.session.query(
            Favorite,
            func.min(Stock.price).filter(stock_filters).over(partition_by=Stock.offerId).label("min_price"),
            func.max(Stock.price).filter(stock_filters).over(partition_by=Stock.offerId).label("max_price"),
            func.min(Stock.beginningDatetime).filter(stock_filters).over(partition_by=Stock.offerId).label("min_begin"),
            func.max(Stock.beginningDatetime).filter(stock_filters).over(partition_by=Stock.offerId).label("max_begin"),
            # count future active
            func.count(Stock.id).filter(stock_filters).over(partition_by=Stock.offerId).label("non_expired_count"),
            # count all active
            func.count(Stock.id).filter(active_stock_filters).over(partition_by=Stock.offerId).label("active_count"),
        )
        .options(Load(Favorite).load_only("id"))  # type: ignore [attr-defined]
        .join(Favorite.offer)
        .join(Offer.venue)
        .outerjoin(Offer.stocks)
        .filter(Favorite.userId == user.id)
        .distinct(Favorite.id)
        .options(
            joinedload(Favorite.offer).load_only(
                Offer.name,
                Offer.externalTicketOfficeUrl,
                Offer.url,
                Offer.subcategoryId,
                Offer.isActive,
                Offer.validation,
            )
        )
        .options(
            joinedload(Favorite.offer)
            .joinedload(Offer.venue)
            .load_only(Venue.latitude, Venue.longitude, Venue.validationToken)
        )
        .options(
            joinedload(Favorite.offer)
            .joinedload(Offer.venue)
            .joinedload(Venue.managingOfferer)
            .load_only(Offerer.validationToken, Offerer.isActive)
        )
        .options(
            joinedload(Favorite.offer)
            .joinedload(Offer.mediations)
            .load_only(Mediation.dateCreated, Mediation.isActive, Mediation.thumbCount, Mediation.credit)
        )
        .options(joinedload(Favorite.offer).joinedload(Offer.product).load_only(Product.id, Product.thumbCount))
        .options(joinedload(Favorite.offer).joinedload(Offer.stocks))
        .order_by(Favorite.id.desc())
    )

    if favorite_id:
        query = query.filter(Favorite.id == favorite_id)

    favorites = query.all()

    for (
        favorite,
        min_price,
        max_price,
        min_beginning_datetime,
        max_beginning_datetime,
        non_expired_count,
        active_count,
    ) in favorites:
        _fill_favorite_offer(
            favorite=favorite,
            min_price=min_price,
            max_price=max_price,
            min_beginning_datetime=min_beginning_datetime,
            max_beginning_datetime=max_beginning_datetime,
            non_expired_count=non_expired_count,
            active_count=active_count,
        )

    favorites = [fav for (fav, *_) in favorites]

    return favorites


@blueprint.native_v1.route("/me/favorites", methods=["GET"])
@spectree_serialize(response_model=serializers.PaginatedFavoritesResponse, api=blueprint.api)
@authenticated_and_active_user_required
def get_favorites(user: User) -> serializers.PaginatedFavoritesResponse:
    favorites = get_favorites_for(user)

    paginated_favorites = {
        "page": 1,
        "nbFavorites": len(favorites),
        "favorites": favorites,
    }
    return serializers.PaginatedFavoritesResponse(**paginated_favorites)


@blueprint.native_v1.route("/me/favorites", methods=["POST"])
@spectree_serialize(response_model=serializers.FavoriteResponse, on_error_statuses=[400], api=blueprint.api)
@authenticated_and_active_user_required
def create_favorite(user: User, body: serializers.FavoriteRequest) -> serializers.FavoriteResponse:
    if settings.MAX_FAVORITES:
        if Favorite.query.filter_by(user=user).count() >= settings.MAX_FAVORITES:
            raise ApiErrors({"code": "MAX_FAVORITES_REACHED"})

    offer = Offer.query.filter_by(id=body.offerId).first_or_404()
    try:
        with transaction():
            favorite = Favorite(
                mediation=offer.activeMediation,
                offer=offer,
                user=user,
            )
            db.session.add(favorite)
            db.session.flush()
        update_external_user(user)
    except exc.IntegrityError as exception:
        favorite = Favorite.query.filter_by(offerId=body.offerId, userId=user.id).one_or_none()
        if not favorite:
            raise exception

    favorite = get_favorites_for(user, favorite.id)[0]

    return serializers.FavoriteResponse.from_orm(favorite)


@blueprint.native_v1.route("/me/favorites/<int:favorite_id>", methods=["DELETE"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def delete_favorite(user: User, favorite_id: int) -> None:
    with transaction():
        favorite = Favorite.query.filter_by(id=favorite_id, user=user).first_or_404()
        db.session.delete(favorite)
