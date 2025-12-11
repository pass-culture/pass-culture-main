import datetime
import decimal

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask_login import current_user

from pcapi import settings
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.external.batch import track_offer_added_to_favorites_event
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.exceptions import OfferNotFound
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.offers.repository import get_offer_by_id
from pcapi.core.users.models import Favorite
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.utils import first_or_404
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.repository import transaction

from .. import blueprint
from .serialization import favorites as serializers


def _fill_offer_price(
    offer: Offer,
    min_price: decimal.Decimal,
    max_price: decimal.Decimal,
) -> None:
    offer.price = None
    offer.startPrice = None
    if min_price == max_price:
        offer.price = min_price
    else:
        offer.startPrice = min_price


def _fill_offer_date(
    offer: Offer, min_beginning_datetime: datetime.datetime, max_beginning_datetime: datetime.datetime
) -> None:
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
    *,
    favorite: Favorite,
    min_price: decimal.Decimal,
    max_price: decimal.Decimal,
    min_beginning_datetime: datetime.datetime,
    max_beginning_datetime: datetime.datetime,
    non_expired_count: int,
    active_count: int,
) -> None:
    offer = favorite.offer
    _fill_offer_price(offer, min_price, max_price)
    _fill_offer_date(offer, min_beginning_datetime, max_beginning_datetime)
    _fill_offer_expired(offer, non_expired_count, active_count)


def get_favorites_for(user: User, favorite_id: int | None = None) -> list[Favorite]:
    active_stock_filters = sa.and_(Offer.isActive, Stock.isSoftDeleted.is_(False))
    stock_filters = sa.and_(
        sa.not_(Stock.isEventExpired),
        sa.not_(Stock.hasBookingLimitDatetimePassed),
        active_stock_filters,
    )
    query = (
        db.session.query(
            Favorite,
            sa.func.min(Stock.price).filter(stock_filters).over(partition_by=Stock.offerId).label("min_price"),
            sa.func.max(Stock.price).filter(stock_filters).over(partition_by=Stock.offerId).label("max_price"),
            sa.func.min(Stock.beginningDatetime)
            .filter(stock_filters)
            .over(partition_by=Stock.offerId)
            .label("min_begin"),
            sa.func.max(Stock.beginningDatetime)
            .filter(stock_filters)
            .over(partition_by=Stock.offerId)
            .label("max_begin"),
            # count future active
            sa.func.count(Stock.id).filter(stock_filters).over(partition_by=Stock.offerId).label("non_expired_count"),
            # count all active
            sa.func.count(Stock.id).filter(active_stock_filters).over(partition_by=Stock.offerId).label("active_count"),
        )
        .options(sa_orm.Load(Favorite).load_only(Favorite.id))
        .join(Favorite.offer)
        .join(Offer.venue)
        .outerjoin(Offer.stocks)
        .filter(Favorite.userId == user.id)
        .distinct(Favorite.id)
        .options(
            sa_orm.joinedload(Favorite.offer).load_only(
                Offer.name,
                Offer.externalTicketOfficeUrl,
                Offer.url,
                Offer.subcategoryId,
                Offer.validation,
                Offer.publicationDatetime,
                Offer.bookingAllowedDatetime,
            )
        )
        .options(
            sa_orm.joinedload(Favorite.offer)
            .joinedload(Offer.venue)
            .load_only(Venue.publicName, Venue.name)
            .joinedload(Venue.offererAddress)
            .load_only()
            .joinedload(OffererAddress.address)
        )
        .options(
            sa_orm.joinedload(Favorite.offer)
            .joinedload(Offer.venue)
            .joinedload(Venue.managingOfferer)
            .load_only(
                Offerer.validationStatus,
                Offerer.isActive,
                Offerer.name,
            )
        )
        .options(
            sa_orm.joinedload(Favorite.offer)
            .joinedload(Offer.mediations)
            .load_only(Mediation.dateCreated, Mediation.isActive, Mediation.thumbCount, Mediation.credit)
        )
        .options(
            sa_orm.joinedload(Favorite.offer)
            .joinedload(Offer.product)
            .load_only(Product.id, Product.thumbCount)
            .joinedload(Product.productMediations)
        )
        .options(sa_orm.joinedload(Favorite.offer).joinedload(Offer.stocks))
        .options(sa_orm.joinedload(Favorite.offer).joinedload(Offer.offererAddress).joinedload(OffererAddress.address))
        .order_by(Favorite.id.desc())
    )

    if favorite_id:
        query = query.filter(Favorite.id == favorite_id)

    results = query.all()

    for (
        favorite,
        min_price,
        max_price,
        min_beginning_datetime,
        max_beginning_datetime,
        non_expired_count,
        active_count,
    ) in results:
        _fill_favorite_offer(
            favorite=favorite,
            min_price=min_price,
            max_price=max_price,
            min_beginning_datetime=min_beginning_datetime,
            max_beginning_datetime=max_beginning_datetime,
            non_expired_count=non_expired_count,
            active_count=active_count,
        )

    favorites = [fav for (fav, *_) in results]

    return favorites


@blueprint.native_route("/me/favorites", methods=["GET"])
@spectree_serialize(response_model=serializers.PaginatedFavoritesResponse, api=blueprint.api)
@authenticated_and_active_user_required
def get_favorites() -> serializers.PaginatedFavoritesResponse:
    favorites = get_favorites_for(current_user)

    paginated_favorites = {
        "page": 1,
        "nbFavorites": len(favorites),
        "favorites": favorites,
    }
    return serializers.PaginatedFavoritesResponse(**paginated_favorites)  # type: ignore[arg-type]


@blueprint.native_route("/me/favorites", methods=["POST"])
@spectree_serialize(response_model=serializers.FavoriteResponse, on_error_statuses=[400], api=blueprint.api)
@authenticated_and_active_user_required
def create_favorite(body: serializers.FavoriteRequest) -> serializers.FavoriteResponse:
    if settings.MAX_FAVORITES:
        if db.session.query(Favorite).filter_by(user=current_user).count() >= settings.MAX_FAVORITES:
            raise ApiErrors({"code": "MAX_FAVORITES_REACHED"})

    try:
        offer = get_offer_by_id(body.offerId, load_options=["stock"])
        with transaction():
            favorite = Favorite(offer=offer, user=current_user)
            db.session.add(favorite)
    except OfferNotFound as exception:
        raise ResourceNotFoundError() from exception
    except sa.exc.IntegrityError as exception:
        candidate = db.session.query(Favorite).filter_by(offerId=body.offerId, userId=current_user.id).one_or_none()
        if not candidate:
            raise exception
        favorite = candidate
    else:
        update_external_user(current_user)
        track_offer_added_to_favorites_event(current_user.id, offer)

    favorite = get_favorites_for(current_user, favorite.id)[0]
    return serializers.FavoriteResponse.from_orm(favorite)


@blueprint.native_route("/me/favorites/<int:favorite_id>", methods=["DELETE"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def delete_favorite(favorite_id: int) -> None:
    with transaction():
        favorite = first_or_404(db.session.query(Favorite).filter_by(id=favorite_id, user=current_user))
        db.session.delete(favorite)
