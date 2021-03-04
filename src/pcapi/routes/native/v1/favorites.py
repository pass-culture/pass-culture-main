from sqlalchemy import func
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
from pcapi.repository import repository
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
            func.min(Stock.price).over(partition_by=Stock.offerId).label("min_price"),
            func.count(Stock.price).over(partition_by=Stock.offerId).label("price_count"),
            func.min(Stock.beginningDatetime).over(partition_by=Stock.offerId).label("min_beginning_datetime"),
            func.count(Stock.beginningDatetime).over(partition_by=Stock.offerId).label("beginning_datetime_count"),
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
            .load_only(Mediation.dateCreated, Mediation.isActive, Mediation.thumbCount)
        )
        .options(
            joinedload(FavoriteSQLEntity.offer).joinedload(Offer.product).load_only(Product.id, Product.thumbCount)
        )
        .order_by(FavoriteSQLEntity.id)
        .all()
    )

    for fav, min_price, price_count, min_beginning_datetime, beginning_datetime_count in favorites:
        fav.offer.price = None
        fav.offer.startPrice = None
        if price_count == 1:
            fav.offer.price = min_price
        elif price_count > 1:
            fav.offer.startPrice = min_price
        fav.offer.date = None
        fav.offer.startDate = None
        if beginning_datetime_count == 1:
            fav.offer.date = min_beginning_datetime
        elif beginning_datetime_count > 1:
            fav.offer.startDate = min_beginning_datetime
    favorites = [fav for (fav, *_) in favorites]

    paginated_favorites = {
        "page": 1,
        "nbFavorites": len(favorites),
        "favorites": favorites,
    }
    return serializers.PaginatedFavoritesResponse(**paginated_favorites)


@blueprint.native_v1.route("/me/favorites", methods=["POST"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400], api=blueprint.api)  # type: ignore
@authenticated_user_required
def create_favorite(user: User, body: serializers.FavoriteRequest) -> None:
    offer = Offer.query.filter_by(id=body.offerId).first_or_404()

    favorite = FavoriteSQLEntity(
        mediation=offer.activeMediation,
        offer=offer,
        user=user,
    )
    repository.save(favorite)
