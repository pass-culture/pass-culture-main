import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.favorites import models as favorite_models
from pcapi.core.offerers import models as offerer_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


def get_favorites_for(
    user: offers_models.User,
    favorite_id: int | None = None,
) -> list[favorite_models.FavoriteOfferData]:
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
            favorite_models.FavoriteOffer,
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
        .join(favorite_models.FavoriteOffer.offer)
        .outerjoin(offers_models.Offer.stocks)
        .options(sa_orm.load_only(favorite_models.FavoriteOffer.id))
        .options(
            sa_orm.joinedload(favorite_models.FavoriteOffer.offer)
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
                .load_only(offerer_models.Venue.publicName, offerer_models.Venue.name, offerer_models.Venue.state)
                .options(
                    sa_orm.joinedload(offerer_models.Venue.offererAddress)
                    .load_only()
                    .joinedload(offerer_models.OffererAddress.address)
                )
                .options(
                    sa_orm.joinedload(offerer_models.Venue.managingOfferer).load_only(
                        offerer_models.Offerer.validationStatus,
                        offerer_models.Offerer.isActive,
                        offerer_models.Offerer.name,
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
                sa_orm.joinedload(offers_models.Offer.offererAddress).joinedload(offerer_models.OffererAddress.address)
            )
        )
        .filter(
            favorite_models.FavoriteOffer.userId == user.id,
            offers_models.Offer.isPublished,
        )
        .order_by(favorite_models.FavoriteOffer.id.desc())
    )

    if favorite_id:
        query = query.filter(favorite_models.FavoriteOffer.id == favorite_id)

    results = db.session.execute(query).unique().all()

    return [
        favorite_models.FavoriteOfferData(
            date=start_date if start_date == end_date else None,
            favorite=favorite,
            is_expired=active_offers and not active_stocks,
            price=min_price if min_price == max_price else None,
            start_price=min_price if min_price != max_price else None,
            start_date=start_date if start_date != end_date else None,
        )
        for (favorite, min_price, max_price, start_date, end_date, active_stocks, active_offers) in results
    ]
