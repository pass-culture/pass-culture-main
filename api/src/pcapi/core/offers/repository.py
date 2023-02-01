from datetime import datetime
from datetime import time
from datetime import timedelta
from operator import attrgetter
import typing
from typing import List

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy import false
from sqlalchemy import func
from sqlalchemy import not_
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.models import Venue
from pcapi.core.providers import models as providers_models
from pcapi.core.users.models import User
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.infrastructure.repository.pro_offers.offers_recap_domain_converter import to_domain
from pcapi.models import db
from pcapi.models.offer_mixin import OfferStatus
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.custom_keys import compute_venue_reference

from . import exceptions
from . import models


IMPORTED_CREATION_MODE = "imported"
MANUAL_CREATION_MODE = "manual"


def get_capped_offers_for_filters(
    user_id: int,
    user_is_admin: bool,
    offers_limit: int,
    offerer_id: int | None = None,
    status: str | None = None,
    venue_id: int | None = None,
    category_id: str | None = None,
    name_keywords_or_isbn: str | None = None,
    creation_mode: str | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
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
        period_beginning_date=period_beginning_date,  # type: ignore [arg-type]
        period_ending_date=period_ending_date,  # type: ignore [arg-type]
    )

    offers = (
        query.options(joinedload(models.Offer.venue).joinedload(Venue.managingOfferer))
        .options(joinedload(models.Offer.stocks))
        .options(joinedload(models.Offer.mediations))
        .options(joinedload(models.Offer.product))
        .options(joinedload(models.Offer.lastProvider))
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


def get_offers_by_ids(user: User, offer_ids: list[int]) -> BaseQuery:
    query = models.Offer.query
    if not user.has_admin_role:
        query = query.join(Venue, Offerer, UserOfferer).filter(UserOfferer.userId == user.id, UserOfferer.isValidated)
    query = query.filter(models.Offer.id.in_(offer_ids))
    return query


def get_collective_offers_by_offer_ids(user: User, offer_ids: list[int]) -> BaseQuery:
    query = CollectiveOffer.query
    if not user.has_admin_role:
        query = query.join(Venue, Offerer, UserOfferer).filter(UserOfferer.userId == user.id, UserOfferer.isValidated)
    query = query.filter(CollectiveOffer.offerId.in_(offer_ids))
    return query


def get_collective_offers_template_by_offer_ids(user: User, offer_ids: list[int]) -> BaseQuery:
    query = CollectiveOfferTemplate.query
    if not user.has_admin_role:
        query = query.join(Venue, Offerer, UserOfferer).filter(UserOfferer.userId == user.id, UserOfferer.isValidated)
    query = query.filter(CollectiveOfferTemplate.offerId.in_(offer_ids))
    return query


def get_offers_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None = None,
    status: str | None = None,
    venue_id: int | None = None,
    category_id: str | None = None,
    name_keywords_or_isbn: str | None = None,
    creation_mode: str | None = None,
    period_beginning_date: datetime | None = None,
    period_ending_date: datetime | None = None,
) -> BaseQuery:
    query = models.Offer.query

    if not user_is_admin:
        query = (
            query.join(Venue)
            .join(Offerer)
            .join(UserOfferer)
            .filter(UserOfferer.userId == user_id, UserOfferer.isValidated)
        )
    if offerer_id is not None:
        if user_is_admin:
            query = query.join(Venue)
        query = query.filter(Venue.managingOffererId == offerer_id)
    if venue_id is not None:
        query = query.filter(models.Offer.venueId == venue_id)
    if creation_mode is not None:
        query = _filter_by_creation_mode(query, creation_mode)
    if category_id is not None:
        requested_subcategories = [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category.id == category_id
        ]
        query = query.filter(models.Offer.subcategoryId.in_(requested_subcategories))
    if name_keywords_or_isbn is not None:
        search = name_keywords_or_isbn
        if len(name_keywords_or_isbn) > 3:
            search = "%{}%".format(name_keywords_or_isbn)
        # We should really be using `union` instead of `union_all` here since we don't want duplicates but
        # 1. it's unlikely that a book will contain its ISBN in its name
        # 2. we need to migrate models.Offer.extraData to JSONB in order to use `union`
        query = query.filter(models.Offer.name.ilike(search)).union_all(
            query.filter(models.Offer.extraData["isbn"].astext == name_keywords_or_isbn)
        )
    if status is not None:
        query = _filter_by_status(query, status)
    if period_beginning_date is not None or period_ending_date is not None:
        subquery = (
            models.Stock.query.with_entities(models.Stock.offerId)
            .distinct(models.Stock.offerId)
            .join(models.Offer)
            .join(Venue)
            .filter(models.Stock.isSoftDeleted.is_(False))
        )
        if period_beginning_date is not None:
            subquery = subquery.filter(
                func.timezone(
                    Venue.timezone,
                    func.timezone("UTC", models.Stock.beginningDatetime),
                )
                >= period_beginning_date
            )
        if period_ending_date is not None:
            subquery = subquery.filter(
                func.timezone(
                    Venue.timezone,
                    func.timezone("UTC", models.Stock.beginningDatetime),
                )
                <= period_ending_date
            )
        if venue_id is not None:
            subquery = subquery.filter(models.Offer.venueId == venue_id)
        elif offerer_id is not None:
            subquery = subquery.filter(Venue.managingOffererId == offerer_id)
        elif not user_is_admin:
            subquery = (
                subquery.join(Offerer).join(UserOfferer).filter(UserOfferer.userId == user_id, UserOfferer.isValidated)
            )
        q2 = subquery.subquery()
        query = query.join(q2, q2.c.offerId == models.Offer.id)
    return query


def get_collective_offers_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None = None,
    status: str | None = None,
    venue_id: int | None = None,
    category_id: str | None = None,
    name_keywords: str | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
) -> BaseQuery:
    query = CollectiveOffer.query.filter(CollectiveOffer.validation != models.OfferValidationStatus.DRAFT)

    if not user_is_admin:
        query = (
            query.join(Venue)
            .join(Offerer)
            .join(UserOfferer)
            .filter(UserOfferer.userId == user_id, UserOfferer.isValidated)
        )
    if offerer_id is not None:
        if user_is_admin:
            query = query.join(Venue)
        query = query.filter(Venue.managingOffererId == offerer_id)
    if venue_id is not None:
        query = query.filter(CollectiveOffer.venueId == venue_id)
    if category_id is not None:
        requested_subcategories = [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category.id == category_id
        ]
        query = query.filter(CollectiveOffer.subcategoryId.in_(requested_subcategories))
    if name_keywords is not None:
        search = name_keywords
        if len(name_keywords) > 3:
            search = "%{}%".format(name_keywords)
        # We should really be using `union` instead of `union_all` here since we don't want duplicates but
        # 1. it's unlikely that a book will contain its ISBN in its name
        # 2. we need to migrate models.Offer.extraData to JSONB in order to use `union`
        query = query.filter(CollectiveOffer.name.ilike(search))
    if status is not None:
        match status:
            # Status BOOKED == offer is sold out and last booking link to this reservation is not PENDING
            case CollectiveOfferDisplayedStatus.BOOKED.value:
                booking_subquery = (
                    CollectiveStock.query.with_entities(CollectiveStock.collectiveOfferId)
                    .join(CollectiveBooking, CollectiveStock.collectiveBookings)
                    .filter(CollectiveBooking.status != CollectiveBookingStatus.PENDING)
                )
                query = query.filter(
                    CollectiveOffer.status == OfferStatus.SOLD_OUT.name, CollectiveOffer.id.in_(booking_subquery)
                )
            # Status PREBOOKED == offer is sold out and last booking link to this reservation is PENDING
            case CollectiveOfferDisplayedStatus.PREBOOKED.value:
                last_booking_query = (
                    CollectiveBooking.query.with_entities(
                        CollectiveBooking.collectiveStockId, func.max(CollectiveBooking.dateCreated).label("maxdate")
                    )
                    .group_by(CollectiveBooking.collectiveStockId)
                    .subquery()
                )
                offer_id_query = (
                    CollectiveStock.query.with_entities(CollectiveStock.collectiveOfferId, CollectiveBooking.status)
                    .join(CollectiveBooking, CollectiveStock.collectiveBookings)
                    .join(
                        last_booking_query,
                        and_(
                            CollectiveStock.id == last_booking_query.c.collectiveStockId,
                            CollectiveBooking.dateCreated == last_booking_query.c.maxdate,
                        ),
                    )
                    .subquery()
                )
                query = query.filter(
                    CollectiveOffer.status == OfferStatus.SOLD_OUT.name,
                    offer_id_query.c.status == CollectiveBookingStatus.PENDING.name,
                ).join(offer_id_query, offer_id_query.c.collectiveOfferId == CollectiveOffer.id)
            # Status ENDED == event is passed with a reservation
            case CollectiveOfferDisplayedStatus.ENDED.value:
                hasBookingQuery = (
                    CollectiveStock.query.with_entities(CollectiveStock.collectiveOfferId)
                    .filter(CollectiveStock.collectiveBookings != None)
                    .subquery()
                )
                query = query.join(hasBookingQuery, hasBookingQuery.c.collectiveOfferId == CollectiveOffer.id).filter(
                    CollectiveOffer.status == OfferStatus.EXPIRED.name
                )
            # Status EXPIRED == event is passed without any reservation
            case CollectiveOfferDisplayedStatus.EXPIRED.value:
                hasNoBookingQuery = (
                    CollectiveStock.query.with_entities(CollectiveStock.collectiveOfferId)
                    .filter(CollectiveStock.collectiveBookings == None)
                    .subquery()
                )
                query = query.join(
                    hasNoBookingQuery, hasNoBookingQuery.c.collectiveOfferId == CollectiveOffer.id
                ).filter(CollectiveOffer.status == OfferStatus.EXPIRED.name)
            case _:
                query = query.filter(CollectiveOffer.status == OfferStatus[status].name)
    if period_beginning_date is not None or period_ending_date is not None:
        subquery = (
            CollectiveStock.query.with_entities(CollectiveStock.collectiveOfferId)
            .distinct(CollectiveStock.collectiveOfferId)
            .join(CollectiveOffer)
            .join(Venue)
        )
        if period_beginning_date is not None:
            subquery = subquery.filter(
                func.timezone(
                    Venue.timezone,
                    func.timezone("UTC", CollectiveStock.beginningDatetime),
                )
                >= period_beginning_date
            )
        if period_ending_date is not None:
            subquery = subquery.filter(
                func.timezone(
                    Venue.timezone,
                    func.timezone("UTC", CollectiveStock.beginningDatetime),
                )
                <= period_ending_date
            )
        if venue_id is not None:
            subquery = subquery.filter(CollectiveOffer.venueId == venue_id)
        elif offerer_id is not None:
            subquery = subquery.filter(Venue.managingOffererId == offerer_id)
        elif not user_is_admin:
            subquery = (
                subquery.join(Offerer).join(UserOfferer).filter(UserOfferer.userId == user_id, UserOfferer.isValidated)
            )
        q2 = subquery.subquery()
        query = query.join(q2, q2.c.collectiveOfferId == CollectiveOffer.id)
    return query


def get_collective_offers_template_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None = None,
    status: str | None = None,
    venue_id: int | None = None,
    category_id: str | None = None,
    name_keywords: str | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
) -> BaseQuery:
    query = CollectiveOfferTemplate.query.filter(
        CollectiveOfferTemplate.validation != models.OfferValidationStatus.DRAFT
    )

    if period_beginning_date is not None or period_ending_date is not None:
        query = query.filter(false())

    if not user_is_admin:
        query = (
            query.join(Venue)
            .join(Offerer)
            .join(UserOfferer)
            .filter(UserOfferer.userId == user_id, UserOfferer.isValidated)
        )
    if offerer_id is not None:
        if user_is_admin:
            query = query.join(Venue)
        query = query.filter(Venue.managingOffererId == offerer_id)
    if venue_id is not None:
        query = query.filter(CollectiveOfferTemplate.venueId == venue_id)
    if category_id is not None:
        requested_subcategories = [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category.id == category_id
        ]
        query = query.filter(CollectiveOfferTemplate.subcategoryId.in_(requested_subcategories))
    if name_keywords is not None:
        search = name_keywords
        if len(name_keywords) > 3:
            search = "%{}%".format(name_keywords)
        # We should really be using `union` instead of `union_all` here since we don't want duplicates but
        # 1. it's unlikely that a book will contain its ISBN in its name
        # 2. we need to migrate models.Offer.extraData to JSONB in order to use `union`
        query = query.filter(CollectiveOfferTemplate.name.ilike(search))
    if status is not None:
        if status in (CollectiveOfferDisplayedStatus.BOOKED.value, CollectiveOfferDisplayedStatus.PREBOOKED.value):
            query = query.filter(CollectiveOfferTemplate.status == OfferStatus.SOLD_OUT.name)
        elif status in (CollectiveOfferDisplayedStatus.ENDED.value, CollectiveOfferDisplayedStatus.EXPIRED.value):
            query = query.filter(CollectiveOfferTemplate.status == OfferStatus.EXPIRED.name)
        else:
            query = query.filter(CollectiveOfferTemplate.status == OfferStatus[status].name)
    return query


def _filter_by_creation_mode(query: BaseQuery, creation_mode: str) -> BaseQuery:
    if creation_mode == MANUAL_CREATION_MODE:
        query = query.filter(models.Offer.lastProviderId.is_(None))
    if creation_mode == IMPORTED_CREATION_MODE:
        query = query.filter(~models.Offer.lastProviderId.is_(None))

    return query


def _filter_by_status(query: BaseQuery, status: str) -> BaseQuery:
    return query.filter(models.Offer.status == OfferStatus[status].name)


def get_stocks_for_offers(offer_ids: list[int]) -> list[models.Stock]:
    return models.Stock.query.filter(models.Stock.offerId.in_(offer_ids)).all()


def get_stocks_for_offer(offer_id: int) -> list[models.Stock]:
    return (
        models.Stock.query.options(joinedload(models.Stock.offer).load_only(models.Offer.url))
        .options(joinedload(models.Stock.bookings).load_only(Booking.status))
        .filter(models.Stock.offerId == offer_id)
        .filter(models.Stock.isSoftDeleted.is_(False))
        .all()
    )


def get_products_map_by_provider_reference(id_at_providers: list[str]) -> dict[str, models.Product]:
    products = (
        models.Product.query.filter(models.Product.can_be_synchronized)
        .filter(models.Product.subcategoryId == subcategories.LIVRE_PAPIER.id)
        .filter(models.Product.idAtProviders.in_(id_at_providers))
        .all()
    )
    return {product.idAtProviders: product for product in products}


def venue_already_has_validated_offer(offer: models.Offer) -> bool:
    return (
        db.session.query(models.Offer.id)
        .filter(
            models.Offer.venueId == offer.venueId,
            models.Offer.validation == models.OfferValidationStatus.APPROVED,
        )
        .first()
        is not None
    )


def get_offers_map_by_id_at_provider(id_at_provider_list: list[str], venue: Venue) -> dict[str, int]:
    offers_map = {}
    for offer_id, offer_id_at_provider in (
        db.session.query(models.Offer.id, models.Offer.idAtProvider)
        .filter(models.Offer.idAtProvider.in_(id_at_provider_list), models.Offer.venue == venue)
        .all()
    ):
        offers_map[offer_id_at_provider] = offer_id

    return offers_map


def get_offers_map_by_venue_reference(id_at_provider_list: list[str], venue_id: int) -> dict[str, int]:
    offers_map = {}
    for offer_id, offer_id_at_provider in (
        db.session.query(models.Offer.id, models.Offer.idAtProvider)
        .filter(models.Offer.venueId == venue_id, models.Offer.idAtProvider.in_(id_at_provider_list))
        .all()
    ):
        offers_map[compute_venue_reference(offer_id_at_provider, venue_id)] = offer_id

    return offers_map  # type: ignore [return-value]


def get_stocks_by_id_at_providers(id_at_providers: list[str]) -> dict:
    stocks = models.Stock.query.filter(models.Stock.idAtProviders.in_(id_at_providers)).with_entities(
        models.Stock.id,
        models.Stock.idAtProviders,
        models.Stock.dnBookedQuantity,
        models.Stock.quantity,
        models.Stock.price,
    )
    return {
        stock.idAtProviders: {
            "id": stock.id,
            "booking_quantity": stock.dnBookedQuantity,
            "quantity": stock.quantity,
            "price": stock.price,
        }
        for stock in stocks
    }


def get_active_offers_count_for_venue(venue_id: int) -> int:
    active_offers_query = models.Offer.query.filter(models.Offer.venueId == venue_id)
    active_offers_query = _filter_by_status(active_offers_query, OfferStatus.ACTIVE.name)

    n_active_offers = active_offers_query.distinct(models.Offer.id).count()

    n_active_collective_offer = (
        CollectiveOffer.query.filter(CollectiveOffer.venueId == venue_id)
        .filter(CollectiveOffer.status == OfferStatus.ACTIVE.name)
        .distinct(CollectiveOffer.id)
        .count()
    )

    n_active_collective_offer_template = (
        CollectiveOfferTemplate.query.filter(CollectiveOfferTemplate.venueId == venue_id)
        .filter(CollectiveOfferTemplate.status == OfferStatus.ACTIVE.name)
        .distinct(CollectiveOfferTemplate.id)
        .count()
    )

    return n_active_offers + n_active_collective_offer + n_active_collective_offer_template


def get_sold_out_offers_count_for_venue(venue_id: int) -> int:
    sold_out_offers_query = models.Offer.query.filter(models.Offer.venueId == venue_id)
    sold_out_offers_query = _filter_by_status(sold_out_offers_query, OfferStatus.SOLD_OUT.name)

    n_sold_out_offers = sold_out_offers_query.distinct(models.Offer.id).count()

    n_sold_out_collective_offers = (
        CollectiveOffer.query.filter(CollectiveOffer.venueId == venue_id)
        .filter(CollectiveOffer.status == OfferStatus.SOLD_OUT.name)
        .distinct(CollectiveOffer.id)
        .count()
    )

    return n_sold_out_offers + n_sold_out_collective_offers


def get_and_lock_stock(stock_id: int) -> models.Stock:
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
    stock = models.Stock.query.filter_by(id=stock_id).populate_existing().with_for_update().one_or_none()
    if not stock:
        raise exceptions.StockDoesNotExist()
    return stock


def check_stock_consistency() -> list[int]:
    return [
        item[0]
        for item in db.session.query(models.Stock.id)
        .outerjoin(models.Stock.bookings)
        .group_by(models.Stock.id)
        .having(
            models.Stock.dnBookedQuantity
            != func.coalesce(func.sum(Booking.quantity).filter(Booking.status != BookingStatus.CANCELLED), 0)
        )
        .all()
    ]


def find_event_stocks_happening_in_x_days(number_of_days: int) -> BaseQuery:
    target_day = datetime.utcnow() + timedelta(days=number_of_days)
    start = datetime.combine(target_day, time.min)
    end = datetime.combine(target_day, time.max)

    return find_event_stocks_day(start, end)


def find_event_stocks_day(start: datetime, end: datetime) -> BaseQuery:
    return (
        models.Stock.query.filter(models.Stock.beginningDatetime.between(start, end))
        .join(Booking)
        .filter(Booking.status != BookingStatus.CANCELLED)
        .distinct()
    )


def get_current_offer_validation_config() -> models.OfferValidationConfig | None:
    return models.OfferValidationConfig.query.order_by(models.OfferValidationConfig.id.desc()).first()


def get_expired_offers(interval: List[datetime]) -> BaseQuery:
    """Return a query of offers whose latest booking limit occurs within
    the given interval.

    Inactive or deleted offers are ignored.
    """
    return (
        models.Offer.query.join(models.Stock)
        .filter(
            models.Offer.isActive.is_(True),
            models.Stock.isSoftDeleted.is_(False),
            models.Stock.bookingLimitDatetime.isnot(None),
        )
        .having(func.max(models.Stock.bookingLimitDatetime).between(*interval))  # type: ignore [arg-type]
        .group_by(models.Offer.id)
        .order_by(models.Offer.id)
    )


def find_today_event_stock_ids_metropolitan_france(today_min: datetime, today_max: datetime) -> set[int]:
    not_overseas_france = and_(
        not_(Venue.departementCode.startswith("97")),
        not_(Venue.departementCode.startswith("98")),
    )

    return _find_today_event_stock_ids_filter_by_departments(today_min, today_max, not_overseas_france)


def find_today_event_stock_ids_from_departments(
    today_min: datetime,
    today_max: datetime,
    postal_codes_prefixes: typing.Any,
) -> set[int]:
    departments = and_(*[Venue.departementCode.startswith(code) for code in postal_codes_prefixes])
    return _find_today_event_stock_ids_filter_by_departments(today_min, today_max, departments)


def _find_today_event_stock_ids_filter_by_departments(
    today_min: datetime,
    today_max: datetime,
    departments_filter: typing.Any,
) -> set[int]:
    """
    Find stocks linked to offers that:
        * happen today;
        * are not cancelled;
        * matches the `departments_filter`.
    """
    base_query = find_event_stocks_day(today_min, today_max)
    query = base_query.join(Venue).filter(departments_filter).with_entities(models.Stock.id)

    return {stock.id for stock in query}


def delete_past_draft_collective_offers() -> None:
    yesterday = datetime.utcnow() - timedelta(days=1)
    collective_offer_ids_tuple = CollectiveOffer.query.filter(
        CollectiveOffer.dateCreated < yesterday,
        CollectiveOffer.validation == models.OfferValidationStatus.DRAFT,
    ).with_entities(CollectiveOffer.id)
    collective_offer_ids = [collective_offer_id for (collective_offer_id,) in collective_offer_ids_tuple]

    # Handle collective offers having a stock but user did not save institution association
    # Thus the collective offer is not fully created
    CollectiveStock.query.filter(CollectiveStock.collectiveOfferId.in_(collective_offer_ids)).delete()
    CollectiveOffer.query.filter(CollectiveOffer.id.in_(collective_offer_ids)).delete()

    db.session.commit()


def get_available_activation_code(stock: models.Stock) -> models.ActivationCode | None:
    return models.ActivationCode.query.filter(
        models.ActivationCode.stockId == stock.id,
        models.ActivationCode.bookingId.is_(None),
        or_(models.ActivationCode.expirationDate.is_(None), models.ActivationCode.expirationDate > func.now()),
    ).first()


def get_offer_by_id(offer_id: int) -> models.Offer:
    try:
        return (
            models.Offer.query.filter(models.Offer.id == offer_id)
            .outerjoin(models.Stock, and_(models.Stock.offerId == offer_id, not_(models.Stock.isSoftDeleted)))  # type: ignore [type-var]
            .options(contains_eager(models.Offer.stocks))
            .options(joinedload(models.Offer.mediations))
            .options(joinedload(models.Offer.product, innerjoin=True))
            .options(joinedload(models.Offer.priceCategories).joinedload(models.PriceCategory.priceCategoryLabel))
            .options(
                joinedload(
                    models.Offer.venue,
                    innerjoin=True,
                ).joinedload(
                    Venue.managingOfferer,
                    innerjoin=True,
                )
            )
            .one()
        )
    except NoResultFound:
        raise exceptions.OfferNotFound()


def get_synchronized_offers_with_provider_for_venue(venue_id: int, provider_id: int) -> BaseQuery:
    return models.Offer.query.filter(models.Offer.venueId == venue_id).filter(
        models.Offer.lastProviderId == provider_id  # pylint: disable=comparison-with-callable
    )


def update_stock_quantity_to_dn_booked_quantity(stock_id: int | None) -> None:
    if not stock_id:
        return
    models.Stock.query.filter(models.Stock.id == stock_id).update({"quantity": models.Stock.dnBookedQuantity})
    db.session.commit()


def get_paginated_active_offer_ids(limit: int, page: int) -> list[int]:
    query = (
        models.Offer.query.with_entities(models.Offer.id)
        .filter(models.Offer.isActive.is_(True))
        .order_by(models.Offer.id)
        .offset(page * limit)
        .limit(limit)
    )
    return [offer_id for offer_id, in query]


def get_paginated_offer_ids_by_venue_id(venue_id: int, limit: int, page: int) -> list[int]:
    query = (
        models.Offer.query.with_entities(models.Offer.id)
        .filter(models.Offer.venueId == venue_id)
        .order_by(models.Offer.id)
        .offset(page * limit)
        .limit(limit)
    )
    return [offer_id for offer_id, in query]


def search_offers_by_filters(
    search_query: str | None,
    limit: int,
) -> sa.orm.Query:
    offers = models.Offer.query.options(
        sa.orm.joinedload(models.Offer.stocks),
        sa.orm.joinedload(models.Offer.criteria),
    )

    if search_query:
        if search_query.isnumeric():
            offers = offers.filter(models.Offer.id == search_query)
        else:
            name_query = search_query.replace(" ", "%").replace("-", "%")
            name_query = clean_accents(name_query)
            offers = offers.filter(sa.func.unaccent(models.Offer.name).ilike(f"%{name_query}%")).limit(limit)

    return offers.distinct()


def exclude_offers_from_inactive_venue_provider(query: BaseQuery) -> BaseQuery:
    return (
        query.outerjoin(models.Offer.lastProvider)
        .outerjoin(
            providers_models.VenueProvider,
            sa.and_(
                providers_models.Provider.id == providers_models.VenueProvider.providerId,
                providers_models.VenueProvider.venueId == models.Offer.venueId,
            ),
        )
        .filter(
            sa.or_(
                models.Offer.lastProviderId.is_(None),
                providers_models.VenueProvider.isActive == True,
            )
        )
    )
