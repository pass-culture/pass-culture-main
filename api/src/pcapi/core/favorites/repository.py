from typing import Literal

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Query
from sqlalchemy.sql.dml import ReturningInsert

from pcapi import settings
from pcapi.core.favorites import exceptions
from pcapi.core.favorites import models
from pcapi.core.favorites.models import FavoriteArtist
from pcapi.core.favorites.models import FavoriteOffer
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.models import Offer
from pcapi.core.users import models as users_models
from pcapi.models import db


FAVORITE_TYPES = Literal["offer", "artist"]
FAVORITE_MODELS = type[models.FavoriteOffer] | type[models.FavoriteArtist]


# GET Functions
def get_favorite_offers_for(
    user: users_models.User,
    favorite_id: int | None = None,
    offer_id: int | None = None,
) -> list[models.FavoriteOfferData]:
    active_stock_filters = sa.and_(
        offers_models.Offer.isActive,
        offers_models.Stock.isSoftDeleted.is_(False),
    )

    stock_filters = sa.and_(
        sa.not_(offers_models.Stock.isEventExpired),
        sa.not_(offers_models.Stock.hasBookingLimitDatetimePassed),
        active_stock_filters,
    )

    query = (
        sa.select(
            models.FavoriteOffer,
            # minimum price
            sa.func.min(offers_models.Stock.price)
            .filter(stock_filters)
            .over(partition_by=offers_models.Stock.offerId)
            .label("min_price"),
            # maximum price
            sa.func.max(offers_models.Stock.price)
            .filter(stock_filters)
            .over(partition_by=offers_models.Stock.offerId)
            .label("max_price"),
            # earliest datetime in stocks
            sa.func.min(offers_models.Stock.beginningDatetime)
            .filter(stock_filters)
            .over(partition_by=offers_models.Stock.offerId)
            .label("min_begin"),
            # latest datetime in stocks
            sa.func.max(offers_models.Stock.beginningDatetime)
            .filter(stock_filters)
            .over(partition_by=offers_models.Stock.offerId)
            .label("max_begin"),
            # count active stocks of active offers
            sa.func.count(offers_models.Stock.id)
            .filter(stock_filters)
            .over(partition_by=offers_models.Stock.offerId)
            .label("active_stocks"),
            # count favorites of active offers
            sa.func.count(offers_models.Stock.id)
            .filter(active_stock_filters)
            .over(partition_by=offers_models.Stock.offerId)
            .label("active_offers"),
        )
        .join(models.FavoriteOffer.offer)
        .outerjoin(offers_models.Offer.stocks)
        .options(sa_orm.load_only(models.FavoriteOffer.id))
        .options(
            sa_orm.joinedload(models.FavoriteOffer.offer)
            .load_only(
                offers_models.Offer.name,
                offers_models.Offer.externalTicketOfficeUrl,
                offers_models.Offer.url,
                offers_models.Offer.subcategoryId,
                offers_models.Offer.validation,
                offers_models.Offer.publicationDatetime,
                offers_models.Offer.bookingAllowedDatetime,
            )
            .options(
                sa_orm.joinedload(offers_models.Offer.venue)
                .load_only(offerers_models.Venue.publicName, offerers_models.Venue.name, offerers_models.Venue.state)
                .options(
                    sa_orm.joinedload(offerers_models.Venue.offererAddress)
                    .load_only()
                    .joinedload(offerers_models.OffererAddress.address)
                )
                .options(
                    sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(
                        offerers_models.Offerer.validationStatus,
                        offerers_models.Offerer.isActive,
                        offerers_models.Offerer.name,
                    )
                )
            )
            .options(
                sa_orm.joinedload(offers_models.Offer.mediations).load_only(
                    offers_models.Mediation.dateCreated,
                    offers_models.Mediation.isActive,
                    offers_models.Mediation.thumbCount,
                    offers_models.Mediation.credit,
                )
            )
            .options(
                sa_orm.joinedload(offers_models.Offer.product)
                .load_only(offers_models.Product.id, offers_models.Product.thumbCount)
                .joinedload(offers_models.Product.productMediations)
            )
            .options(
                sa_orm.contains_eager(offers_models.Offer.stocks).load_only(
                    offers_models.Stock.beginningDatetime,
                    offers_models.Stock.bookingLimitDatetime,
                    offers_models.Stock.isSoftDeleted,
                    offers_models.Stock.quantity,
                    offers_models.Stock.dnBookedQuantity,
                )
            )
            .options(
                sa_orm.joinedload(offers_models.Offer.offererAddress).joinedload(offerers_models.OffererAddress.address)
            )
        )
        .filter(
            models.FavoriteOffer.userId == user.id,
            offers_models.Offer.isPublished,
        )
        .order_by(models.FavoriteOffer.id.desc())
    )

    if favorite_id:
        query = query.filter(models.FavoriteOffer.id == favorite_id)

    if offer_id:
        query = query.filter(Offer.id == offer_id)

    results = db.session.execute(query).unique().all()

    return [
        models.FavoriteOfferData(
            date=start_date if start_date == end_date else None,
            favorite=favorite,
            is_expired=active_offers and not active_stocks,
            price=min_price if min_price == max_price else None,
            start_price=min_price if min_price != max_price else None,
            start_date=start_date if start_date != end_date else None,
        )
        for (favorite, min_price, max_price, start_date, end_date, active_stocks, active_offers) in results
    ]


## CREATE function
def create_favorite_offer(
    user: users_models.User,
    offer: Offer,
) -> tuple[models.FavoriteOffer, bool]:
    stmt: ReturningInsert = (
        insert(models.FavoriteOffer)
        .values({"offerId": offer.id, "userId": user.id})
        .on_conflict_do_update(
            index_elements=[models.FavoriteOffer.offerId, models.FavoriteOffer.userId],
            set_={"offerId": offer.id},
        )
        .returning(
            models.FavoriteOffer,
            # xmax is a "system" column that returns the transaction id that modified the row.
            # In case of insertion, no row has been modified → xmax = 0
            sa.literal_column("xmax = 0").label("is_inserted"),
        )
    )

    res = db.session.execute(stmt).all()
    favorite, is_inserted = res[0]

    return favorite, is_inserted == 1


## DELETE Functions
def delete_favorite(
    type: FAVORITE_TYPES,
    favorite_id: int,
) -> None:
    _model: FAVORITE_MODELS | None = None
    match type:
        case "offer":
            _model = models.FavoriteOffer
        case _:
            raise exceptions.UnhandledFavoriteType

    db.session.execute(delete(_model).where(_model.id == favorite_id))
    db.session.flush()


## Utils
def has_reached_max_favorites_for(
    type: FAVORITE_TYPES,
    user: users_models.User,
) -> bool:
    if not settings.MAX_FAVORITES:
        return False

    query: Query[FavoriteArtist] | Query[FavoriteOffer]

    match type:
        case "offer":
            query = (
                db.session.query(models.FavoriteOffer)
                .join(models.FavoriteOffer.offer)
                .filter(
                    models.FavoriteOffer.userId == user.id,
                    offers_models.Offer.isPublished,
                )
            )
        case _:
            raise exceptions.UnhandledFavoriteType

    return query.count() >= settings.MAX_FAVORITES
