from datetime import datetime
from datetime import time
from datetime import timedelta
from operator import attrgetter
from typing import List
from typing import Optional

from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy.orm import Query
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import coalesce

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.exceptions import OfferNotFound
from pcapi.core.offers.exceptions import StockDoesNotExist
from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.infrastructure.repository.pro_offers.offers_recap_domain_converter import to_domain
from pcapi.models import db
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.product import Product
from pcapi.models.user_offerer import UserOfferer
from pcapi.utils.custom_keys import compute_venue_reference


IMPORTED_CREATION_MODE = "imported"
MANUAL_CREATION_MODE = "manual"


def get_capped_offers_for_filters(
    user_id: int,
    user_is_admin: bool,
    offers_limit: int,
    offerer_id: Optional[int] = None,
    status: Optional[str] = None,
    venue_id: Optional[int] = None,
    category_id: Optional[str] = None,
    name_keywords_or_isbn: Optional[str] = None,
    creation_mode: Optional[str] = None,
    period_beginning_date: Optional[str] = None,
    period_ending_date: Optional[str] = None,
) -> OffersRecap:
    query = get_offers_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        name_keywords_or_isbn=name_keywords_or_isbn,
        creation_mode=creation_mode,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
    )

    offers = (
        query.options(joinedload(Offer.venue).joinedload(Venue.managingOfferer))
        .options(joinedload(Offer.stocks))
        .options(joinedload(Offer.mediations))
        .options(joinedload(Offer.product))
        .options(joinedload(Offer.lastProvider))
        .limit(offers_limit)
        .all()
    )

    # Do not use `ORDER BY` in SQL, which sometimes applies on a very large result set
    # _before_ the `LIMIT` clause (and kills performance).
    if len(offers) < offers_limit:
        offers = sorted(offers, key=attrgetter("id"), reverse=True)

    # FIXME (cgaunet, 2020-11-03): we should not have serialization logic in the repository
    return to_domain(
        offers=offers,
    )


def get_offers_by_ids(user: User, offer_ids: list[int]) -> Query:
    query = Offer.query
    if not user.has_admin_role:
        query = query.join(Venue, Offerer, UserOfferer).filter(
            and_(UserOfferer.userId == user.id, UserOfferer.validationToken.is_(None))
        )
    query = query.filter(Offer.id.in_(offer_ids))
    return query


def get_offers_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: Optional[int] = None,
    status: Optional[str] = None,
    venue_id: Optional[int] = None,
    category_id: Optional[str] = None,
    name_keywords_or_isbn: Optional[str] = None,
    creation_mode: Optional[str] = None,
    period_beginning_date: Optional[datetime] = None,
    period_ending_date: Optional[datetime] = None,
) -> Query:
    query = Offer.query.filter(Offer.validation != OfferValidationStatus.DRAFT)

    if not user_is_admin:
        query = (
            query.join(Venue)
            .join(Offerer)
            .join(UserOfferer)
            .filter(and_(UserOfferer.userId == user_id, UserOfferer.validationToken.is_(None)))
        )
    if offerer_id is not None:
        if user_is_admin:
            query = query.join(Venue)
        query = query.filter(Venue.managingOffererId == offerer_id)
    if venue_id is not None:
        query = query.filter(Offer.venueId == venue_id)
    if creation_mode is not None:
        query = _filter_by_creation_mode(query, creation_mode)
    if category_id is not None:
        requested_subcategories = [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category_id == category_id
        ]
        query = query.filter(Offer.subcategoryId.in_(requested_subcategories))
    if name_keywords_or_isbn is not None:
        search = name_keywords_or_isbn
        if len(name_keywords_or_isbn) > 3:
            search = "%{}%".format(name_keywords_or_isbn)
        # We should really be using `union` instead of `union_all` here since we don't want duplicates but
        # 1. it's unlikely that a book will contain its ISBN in its name
        # 2. we need to migrate Offer.extraData to JSONB in order to use `union`
        query = query.filter(Offer.name.ilike(search)).union_all(
            query.filter(Offer.extraData["isbn"].astext == name_keywords_or_isbn)
        )
    if status is not None:
        query = _filter_by_status(query, status)
    if period_beginning_date is not None or period_ending_date is not None:
        subquery = (
            Stock.query.with_entities(Stock.offerId)
            .distinct(Stock.offerId)
            .join(Offer)
            .join(Venue)
            .filter(Stock.isSoftDeleted.is_(False))
        )
        if period_beginning_date is not None:
            subquery = subquery.filter(
                func.timezone(
                    Venue.timezone,
                    func.timezone("UTC", Stock.beginningDatetime),
                )
                >= period_beginning_date
            )
        if period_ending_date is not None:
            subquery = subquery.filter(
                func.timezone(
                    Venue.timezone,
                    func.timezone("UTC", Stock.beginningDatetime),
                )
                <= period_ending_date
            )
        if venue_id is not None:
            subquery = subquery.filter(Offer.venueId == venue_id)
        elif offerer_id is not None:
            subquery = subquery.filter(Venue.managingOffererId == offerer_id)
        elif not user_is_admin:
            subquery = (
                subquery.join(Offerer)
                .join(UserOfferer)
                .filter(and_(UserOfferer.userId == user_id, UserOfferer.validationToken.is_(None)))
            )
        q2 = subquery.subquery()
        query = query.join(q2, q2.c.offerId == Offer.id)
    return query


def _filter_by_creation_mode(query: Query, creation_mode: str) -> Query:
    if creation_mode == MANUAL_CREATION_MODE:
        query = query.filter(Offer.lastProviderId.is_(None))
    if creation_mode == IMPORTED_CREATION_MODE:
        query = query.filter(~Offer.lastProviderId.is_(None))

    return query


def _filter_by_status(query: Query, status: str) -> Query:
    return query.filter(Offer.status == OfferStatus[status].name)


def get_stocks_for_offers(offer_ids: list[int]) -> list[Stock]:
    return Stock.query.filter(Stock.offerId.in_(offer_ids)).all()


def get_stocks_for_offer(offer_id: int) -> list[Stock]:
    return (
        Stock.query.options(joinedload(Stock.offer).load_only(Offer.url, Offer.isEducational))
        .options(joinedload(Stock.bookings).load_only(Booking.status))
        .filter(Stock.offerId == offer_id)
        .filter(Stock.isSoftDeleted.is_(False))
        .all()
    )


def get_products_map_by_provider_reference(id_at_providers: list[str]) -> dict[str, Product]:
    products = (
        Product.query.filter(Product.can_be_synchronized)
        .filter(Product.subcategoryId == subcategories.LIVRE_PAPIER.id)
        .filter(Product.idAtProviders.in_(id_at_providers))
        .all()
    )
    return {product.idAtProviders: product for product in products}


def get_offers_map_by_id_at_provider(id_at_provider_list: list[str], venue: Venue) -> dict[str, int]:
    offers_map = {}
    for offer_id, offer_id_at_provider in (
        db.session.query(Offer.id, Offer.idAtProvider)
        .filter(Offer.idAtProvider.in_(id_at_provider_list), Offer.venue == venue)
        .all()
    ):
        offers_map[offer_id_at_provider] = offer_id

    return offers_map


def get_offers_map_by_venue_reference(id_at_provider_list: list[str], venue_id: int) -> dict[str, int]:

    offers_map = {}
    for offer_id, offer_id_at_provider in (
        db.session.query(Offer.id, Offer.idAtProvider)
        .filter(Offer.venueId == venue_id, Offer.idAtProvider.in_(id_at_provider_list))
        .all()
    ):
        offers_map[compute_venue_reference(offer_id_at_provider, venue_id)] = offer_id

    return offers_map


def get_stocks_by_id_at_providers(id_at_providers: list[str]) -> dict:
    stocks = (
        Stock.query.filter(Stock.idAtProviders.in_(id_at_providers))
        .outerjoin(Booking, and_(Stock.id == Booking.stockId, Booking.status != BookingStatus.CANCELLED))
        .group_by(Stock.id)
        .with_entities(
            Stock.id,
            Stock.idAtProviders,
            coalesce(func.sum(Booking.quantity), 0),
            Stock.quantity,
            Stock.price,
        )
        .all()
    )
    return {
        id_at_providers: {
            "id": id,
            "booking_quantity": booking_quantity,
            "quantity": quantity,
            "price": price,
        }
        for (id, id_at_providers, booking_quantity, quantity, price) in stocks
    }


def get_active_offers_count_for_venue(venue_id) -> int:
    query = Offer.query.filter(Offer.venueId == venue_id)
    query = _filter_by_status(query, OfferStatus.ACTIVE.name)
    return query.distinct(Offer.id).count()


def get_sold_out_offers_count_for_venue(venue_id) -> int:
    query = Offer.query.filter(Offer.venueId == venue_id)
    query = _filter_by_status(query, OfferStatus.SOLD_OUT.name)
    return query.distinct(Offer.id).count()


def get_and_lock_stock(stock_id: int) -> Stock:
    """Returns `stock_id` stock with a FOR UPDATE lock
    Raises StockDoesNotExist if no stock is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    # Use `with_for_update()` to make sure we lock the stock while perfoming
    # the booking checks and update the `dnBookedQuantity`
    # This is required to prevent bugs due to concurent acces
    # Also call `populate_existing()` to make sure we don't use something
    # older from the SQLAlchemy's session.
    stock = Stock.query.filter_by(id=stock_id).populate_existing().with_for_update().one_or_none()
    if not stock:
        raise StockDoesNotExist()
    return stock


def check_stock_consistency() -> list[int]:
    return [
        item[0]
        for item in db.session.query(Stock.id)
        .outerjoin(Stock.bookings)
        .group_by(Stock.id)
        .having(
            Stock.dnBookedQuantity
            != func.coalesce(func.sum(Booking.quantity).filter(Booking.status != BookingStatus.CANCELLED), 0)
        )
        .all()
    ]


def find_tomorrow_event_stock_ids() -> set[int]:
    """Find stocks linked to offers that happen tomorrow (and that are not cancelled)"""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_min = datetime.combine(tomorrow, time.min)
    tomorrow_max = datetime.combine(tomorrow, time.max)

    stocks = (
        Stock.query.filter(Stock.beginningDatetime.between(tomorrow_min, tomorrow_max))
        .join(Booking)
        .filter(Booking.status != BookingStatus.CANCELLED)
        .options(load_only(Stock.id))
    )

    return {stock.id for stock in stocks}


def get_current_offer_validation_config() -> Optional[OfferValidationConfig]:
    return OfferValidationConfig.query.order_by(OfferValidationConfig.id.desc()).first()


def get_expired_offers(interval: List[datetime]) -> Query:
    """Return a query of offers whose latest booking limit occurs within
    the given interval.

    Inactive or deleted offers are ignored.
    """
    return (
        Offer.query.join(Stock)
        .filter(
            Offer.isActive.is_(True),
            Stock.isSoftDeleted.is_(False),
            Stock.bookingLimitDatetime.isnot(None),
        )
        .having(func.max(Stock.bookingLimitDatetime).between(*interval))
        .group_by(Offer.id)
        .order_by(Offer.id)
    )


def delete_past_draft_offers() -> None:
    yesterday = datetime.utcnow() - timedelta(days=1)
    filters = (Offer.dateCreated < yesterday, Offer.validation == OfferValidationStatus.DRAFT)
    Mediation.query.filter(Mediation.offerId == Offer.id).filter(*filters).delete(synchronize_session=False)
    OfferCriterion.query.filter(OfferCriterion.offerId == Offer.id).filter(*filters).delete(synchronize_session=False)
    Offer.query.filter(*filters).delete()
    db.session.commit()


def get_available_activation_code(stock: Stock) -> Optional[ActivationCode]:
    return ActivationCode.query.filter(
        ActivationCode.stockId == stock.id,
        ActivationCode.bookingId.is_(None),
        or_(ActivationCode.expirationDate.is_(None), ActivationCode.expirationDate > func.now()),
    ).first()


def get_educational_offer_by_id(offer_id: str) -> Offer:
    return get_educational_offer_by_id_base_query(offer_id).one()


def get_educational_offer_by_id_base_query(offer_id: str) -> Offer:
    return Offer.query.filter(Offer.isEducational == True, Offer.id == offer_id)


def get_non_deleted_stock_by_id(stock_id: int):
    stock = Stock.queryNotSoftDeleted().filter_by(id=stock_id).first()
    if stock is None:
        raise StockDoesNotExist()
    return stock


def get_offer_by_id(offer_id: int) -> Offer:
    try:
        return (
            Offer.query.filter(Offer.id == offer_id)
            .options(joinedload(Offer.mediations))
            .options(joinedload(Offer.stocks))
            .options(joinedload(Offer.product, innerjoin=True))
            .options(
                joinedload(Offer.venue, innerjoin=True,).joinedload(
                    Venue.managingOfferer,
                    innerjoin=True,
                )
            )
            .one()
        )
    except NoResultFound:
        raise OfferNotFound()
