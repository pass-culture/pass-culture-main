import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models import db

from .models import FavoriteOffer
from .models import FavoriteOfferData


def get_favorites_for(user: User, favorite_id: int | None = None) -> list[FavoriteOfferData]:
    active_stock_filters = sa.and_(Offer.isActive, Stock.isSoftDeleted.is_(False))
    stock_filters = sa.and_(
        sa.not_(Stock.isEventExpired),
        sa.not_(Stock.hasBookingLimitDatetimePassed),
        active_stock_filters,
    )
    query = (
        sa.select(
            FavoriteOffer,
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
        .join(FavoriteOffer.offer)
        .outerjoin(Offer.stocks)
        .options(sa_orm.load_only(FavoriteOffer.id))
        .options(
            sa_orm.joinedload(FavoriteOffer.offer)
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
                .load_only(Venue.publicName, Venue.name, Venue.state)
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
        .filter(
            FavoriteOffer.userId == user.id,
            Offer.isPublished,
        )
        .order_by(FavoriteOffer.id.desc())
    )

    if favorite_id:
        query = query.filter(FavoriteOffer.id == favorite_id)

    results = db.session.execute(query).unique().all()

    return [
        FavoriteOfferData(
            date=start_date if start_date == end_date else None,
            favorite=favorite,
            is_expired=active_offers and not active_stocks,
            price=min_price if min_price == max_price else None,
            start_price=min_price if min_price != max_price else None,
            start_date=start_date if start_date != end_date else None,
        )
        for (favorite, min_price, max_price, start_date, end_date, active_stocks, active_offers) in results
    ]
