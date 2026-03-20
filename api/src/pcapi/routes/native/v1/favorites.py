import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask_login import current_user

from pcapi import settings
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.external.batch.trigger_events import track_offer_added_to_favorites_event
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
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import favorites as serializers


def get_favorites_for(user: User, favorite_id: int | None = None) -> list[serializers.FavoriteData]:
    active_stock_filters = sa.and_(Offer.isActive, Stock.isSoftDeleted.is_(False))
    stock_filters = sa.and_(
        sa.not_(Stock.isEventExpired),
        sa.not_(Stock.hasBookingLimitDatetimePassed),
        active_stock_filters,
    )
    query = (
        sa.select(
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
            # count active stocks of active offers
            sa.func.count(Stock.id).filter(stock_filters).over(partition_by=Stock.offerId).label("active_stocks"),
            # count favorites of active offers
            sa.func.count(Stock.id)
            .filter(active_stock_filters)
            .over(partition_by=Stock.offerId)
            .label("active_offers"),
        )
        .join(Favorite.offer)
        .outerjoin(Offer.stocks)
        .options(sa_orm.load_only(Favorite.id))
        .options(
            sa_orm.joinedload(Favorite.offer)
            .load_only(
                Offer.name,
                Offer.externalTicketOfficeUrl,
                Offer.url,
                Offer.subcategoryId,
                Offer.validation,
                Offer.publicationDatetime,
                Offer.bookingAllowedDatetime,
            )
            .options(
                sa_orm.joinedload(Offer.venue)
                .load_only(Venue.publicName, Venue.name)
                .options(sa_orm.joinedload(Venue.offererAddress).load_only().joinedload(OffererAddress.address))
                .options(
                    sa_orm.joinedload(Venue.managingOfferer).load_only(
                        Offerer.validationStatus, Offerer.isActive, Offerer.name
                    )
                )
            )
            .options(
                sa_orm.joinedload(Offer.mediations).load_only(
                    Mediation.dateCreated, Mediation.isActive, Mediation.thumbCount, Mediation.credit
                )
            )
            .options(
                sa_orm.joinedload(Offer.product)
                .load_only(Product.id, Product.thumbCount)
                .joinedload(Product.productMediations)
            )
            .options(
                sa_orm.contains_eager(Offer.stocks).load_only(
                    Stock.beginningDatetime,
                    Stock.bookingLimitDatetime,
                    Stock.isSoftDeleted,
                    Stock.quantity,
                    Stock.dnBookedQuantity,
                )
            )
            .options(sa_orm.joinedload(Offer.offererAddress).joinedload(OffererAddress.address))
        )
        .filter(Favorite.userId == user.id)
        .order_by(Favorite.id.desc())
    )

    if favorite_id:
        query = query.filter(Favorite.id == favorite_id)

    results = db.session.execute(query).unique().all()

    return [
        serializers.FavoriteData(
            favorite=favorite,
            price=min_price if min_price == max_price else None,
            start_price=min_price if min_price != max_price else None,
            date=start_date if start_date == end_date else None,
            start_date=start_date if start_date != end_date else None,
            is_expired=active_offers and not active_stocks,
        )
        for (favorite, min_price, max_price, start_date, end_date, active_stocks, active_offers) in results
    ]


@blueprint.native_route("/me/favorites", methods=["GET"])
@spectree_serialize(response_model=serializers.PaginatedFavoritesResponse, api=blueprint.api)
@authenticated_and_active_user_required
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
@spectree_serialize(response_model=serializers.FavoriteResponse, on_error_statuses=[400], api=blueprint.api)
@authenticated_and_active_user_required
def create_favorite(body: serializers.FavoriteRequest) -> serializers.FavoriteResponse:
    if settings.MAX_FAVORITES:
        if db.session.query(Favorite).filter_by(user=current_user).count() >= settings.MAX_FAVORITES:
            raise ApiErrors({"code": "MAX_FAVORITES_REACHED"})

    try:
        offer = get_offer_by_id(body.offer_id)
    except OfferNotFound as exception:
        raise ResourceNotFoundError() from exception

    try:
        # TODO (tconte-pass, 2026-03-24): use `atomic` as route decorator
        # https://passculture.atlassian.net/browse/PC-40922
        with atomic():
            favorite = Favorite(offer=offer, user=current_user)
            db.session.add(favorite)
    except sa.exc.IntegrityError as exception:
        candidate = db.session.query(Favorite).filter_by(offerId=body.offer_id, userId=current_user.id).one_or_none()
        if not candidate:
            raise exception
        favorite = candidate
    else:
        update_external_user(current_user)
        track_offer_added_to_favorites_event(current_user.id, offer)

    favorite_data = get_favorites_for(current_user, favorite.id)[0]
    return serializers.FavoriteResponse(
        id=favorite_data.favorite.id, offer=serializers.FavoriteOfferResponse.build(favorite_data)
    )


@blueprint.native_route("/me/favorites/<int:favorite_id>", methods=["DELETE"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
@atomic()
def delete_favorite(favorite_id: int) -> None:
    favorite = first_or_404(db.session.query(Favorite).filter_by(id=favorite_id, user=current_user))
    db.session.delete(favorite)
