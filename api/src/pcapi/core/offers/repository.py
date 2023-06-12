import datetime
import logging
import operator
import typing

import flask_sqlalchemy
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers import models as providers_models
from pcapi.core.users import models as users_models
from pcapi.domain.pro_offers import offers_recap
from pcapi.infrastructure.repository.pro_offers import offers_recap_domain_converter
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import custom_keys

from . import exceptions
from . import models


logger = logging.getLogger(__name__)


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
    name_keywords_or_ean: str | None = None,
    creation_mode: str | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
) -> offers_recap.OffersRecap:
    query = get_offers_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        name_keywords_or_ean=name_keywords_or_ean,
        creation_mode=creation_mode,
        period_beginning_date=period_beginning_date,  # type: ignore [arg-type]
        period_ending_date=period_ending_date,  # type: ignore [arg-type]
    )

    offers = (
        query.options(sa_orm.joinedload(models.Offer.venue).joinedload(offerers_models.Venue.managingOfferer))
        .options(sa_orm.joinedload(models.Offer.stocks))
        .options(sa_orm.joinedload(models.Offer.mediations))
        .options(sa_orm.joinedload(models.Offer.product))
        .options(sa_orm.joinedload(models.Offer.lastProvider))
        .limit(offers_limit)
        .all()
    )

    # Do not use `ORDER BY` in SQL, which sometimes applies on a very large result set
    # _before_ the `LIMIT` clause (and kills performance).
    if len(offers) < offers_limit:
        offers = sorted(offers, key=operator.attrgetter("id"), reverse=True)

    # FIXME (cgaunet, 2020-11-03): we should not have serialization logic in the repository
    return offers_recap_domain_converter.to_domain(
        offers=offers,
    )


def get_offers_by_ids(user: users_models.User, offer_ids: list[int]) -> flask_sqlalchemy.BaseQuery:
    query = models.Offer.query
    if not user.has_admin_role:
        query = query.join(offerers_models.Venue, offerers_models.Offerer, offerers_models.UserOfferer).filter(
            offerers_models.UserOfferer.userId == user.id, offerers_models.UserOfferer.isValidated
        )
    query = query.filter(models.Offer.id.in_(offer_ids))
    return query


def get_offers_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None = None,
    status: str | None = None,
    venue_id: int | None = None,
    category_id: str | None = None,
    name_keywords_or_ean: str | None = None,
    creation_mode: str | None = None,
    period_beginning_date: datetime.datetime | None = None,
    period_ending_date: datetime.datetime | None = None,
) -> flask_sqlalchemy.BaseQuery:
    query = models.Offer.query

    if not user_is_admin:
        query = (
            query.join(offerers_models.Venue)
            .join(offerers_models.Offerer)
            .join(offerers_models.UserOfferer)
            .filter(offerers_models.UserOfferer.userId == user_id, offerers_models.UserOfferer.isValidated)
        )
    if offerer_id is not None:
        if user_is_admin:
            query = query.join(offerers_models.Venue)
        query = query.filter(offerers_models.Venue.managingOffererId == offerer_id)
    if venue_id is not None:
        query = query.filter(models.Offer.venueId == venue_id)
    if creation_mode is not None:
        query = _filter_by_creation_mode(query, creation_mode)
    if category_id is not None:
        requested_subcategories = [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category.id == category_id
        ]
        query = query.filter(models.Offer.subcategoryId.in_(requested_subcategories))
    if name_keywords_or_ean is not None:
        search = name_keywords_or_ean
        if len(name_keywords_or_ean) > 3:
            search = "%{}%".format(name_keywords_or_ean)
        # We should really be using `union` instead of `union_all` here since we don't want duplicates but
        # 1. it's unlikely that a book will contain its EAN in its name
        # 2. we need to migrate models.Offer.extraData to JSONB in order to use `union`
        query = query.filter(models.Offer.name.ilike(search)).union_all(
            query.filter(models.Offer.extraData["ean"].astext == name_keywords_or_ean)
        )
    if status is not None:
        query = _filter_by_status(query, status)
    if period_beginning_date is not None or period_ending_date is not None:
        subquery = (
            models.Stock.query.with_entities(models.Stock.offerId)
            .distinct(models.Stock.offerId)
            .join(models.Offer)
            .join(offerers_models.Venue)
            .filter(models.Stock.isSoftDeleted.is_(False))
        )
        if period_beginning_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                )
                >= period_beginning_date
            )
        if period_ending_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                )
                <= period_ending_date
            )
        if venue_id is not None:
            subquery = subquery.filter(models.Offer.venueId == venue_id)
        elif offerer_id is not None:
            subquery = subquery.filter(offerers_models.Venue.managingOffererId == offerer_id)
        elif not user_is_admin:
            subquery = (
                subquery.join(offerers_models.Offerer)
                .join(offerers_models.UserOfferer)
                .filter(offerers_models.UserOfferer.userId == user_id, offerers_models.UserOfferer.isValidated)
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
) -> flask_sqlalchemy.BaseQuery:
    query = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.validation != models.OfferValidationStatus.DRAFT
    )

    if not user_is_admin:
        query = (
            query.join(offerers_models.Venue)
            .join(offerers_models.Offerer)
            .join(offerers_models.UserOfferer)
            .filter(offerers_models.UserOfferer.userId == user_id, offerers_models.UserOfferer.isValidated)
        )
    if offerer_id is not None:
        if user_is_admin:
            query = query.join(offerers_models.Venue)
        query = query.filter(offerers_models.Venue.managingOffererId == offerer_id)
    if venue_id is not None:
        query = query.filter(educational_models.CollectiveOffer.venueId == venue_id)
    if category_id is not None:
        requested_subcategories = [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category.id == category_id
        ]
        query = query.filter(educational_models.CollectiveOffer.subcategoryId.in_(requested_subcategories))
    if name_keywords is not None:
        search = name_keywords
        if len(name_keywords) > 3:
            search = "%{}%".format(name_keywords)
        # We should really be using `union` instead of `union_all` here since we don't want duplicates but
        # 1. it's unlikely that a book will contain its EAN in its name
        # 2. we need to migrate models.Offer.extraData to JSONB in order to use `union`
        query = query.filter(educational_models.CollectiveOffer.name.ilike(search))
    if status is not None:
        match status:
            # Status BOOKED == offer is sold out and last booking link to this reservation is not PENDING
            case educational_models.CollectiveOfferDisplayedStatus.BOOKED.value:
                booking_subquery = (
                    educational_models.CollectiveStock.query.with_entities(
                        educational_models.CollectiveStock.collectiveOfferId
                    )
                    .join(educational_models.CollectiveBooking, educational_models.CollectiveStock.collectiveBookings)
                    .filter(
                        educational_models.CollectiveBooking.status
                        != educational_models.CollectiveBookingStatus.PENDING
                    )
                )
                query = query.filter(
                    educational_models.CollectiveOffer.status == offer_mixin.OfferStatus.SOLD_OUT.name,
                    educational_models.CollectiveOffer.id.in_(booking_subquery),
                )
            # Status PREBOOKED == offer is sold out and last booking link to this reservation is PENDING
            case educational_models.CollectiveOfferDisplayedStatus.PREBOOKED.value:
                last_booking_query = (
                    educational_models.CollectiveBooking.query.with_entities(
                        educational_models.CollectiveBooking.collectiveStockId,
                        sa.func.max(educational_models.CollectiveBooking.dateCreated).label("maxdate"),
                    )
                    .group_by(educational_models.CollectiveBooking.collectiveStockId)
                    .subquery()
                )
                offer_id_query = (
                    educational_models.CollectiveStock.query.with_entities(
                        educational_models.CollectiveStock.collectiveOfferId,
                        educational_models.CollectiveBooking.status,
                    )
                    .join(educational_models.CollectiveBooking, educational_models.CollectiveStock.collectiveBookings)
                    .join(
                        last_booking_query,
                        sa.and_(
                            educational_models.CollectiveStock.id == last_booking_query.c.collectiveStockId,
                            educational_models.CollectiveBooking.dateCreated == last_booking_query.c.maxdate,
                        ),
                    )
                    .subquery()
                )
                query = query.filter(
                    educational_models.CollectiveOffer.status == offer_mixin.OfferStatus.SOLD_OUT.name,
                    offer_id_query.c.status == educational_models.CollectiveBookingStatus.PENDING.name,
                ).join(offer_id_query, offer_id_query.c.collectiveOfferId == educational_models.CollectiveOffer.id)
            # Status ENDED == event is passed with a reservation not cancelled
            case educational_models.CollectiveOfferDisplayedStatus.ENDED.value:
                hasBookingQuery = (
                    educational_models.CollectiveStock.query.with_entities(
                        educational_models.CollectiveStock.collectiveOfferId
                    )
                    .join(educational_models.CollectiveBooking, educational_models.CollectiveStock.collectiveBookings)
                    .filter(
                        educational_models.CollectiveBooking.status
                        != educational_models.CollectiveBookingStatus.CANCELLED
                    )
                    .subquery()
                )
                query = query.join(
                    hasBookingQuery, hasBookingQuery.c.collectiveOfferId == educational_models.CollectiveOffer.id
                ).filter(educational_models.CollectiveOffer.status == offer_mixin.OfferStatus.EXPIRED.name)
            # Status EXPIRED == event is passed without any reservation or cancelled ones
            case educational_models.CollectiveOfferDisplayedStatus.EXPIRED.value:
                hasNoBookingOrCancelledQuery = (
                    educational_models.CollectiveStock.query.with_entities(
                        educational_models.CollectiveStock.collectiveOfferId
                    )
                    .outerjoin(
                        educational_models.CollectiveBooking, educational_models.CollectiveStock.collectiveBookings
                    )
                    .filter(
                        (educational_models.CollectiveBooking.id.is_(None))
                        | (
                            educational_models.CollectiveBooking.status
                            == educational_models.CollectiveBookingStatus.CANCELLED
                        )
                    )
                    .subquery()
                )
                query = query.join(
                    hasNoBookingOrCancelledQuery,
                    hasNoBookingOrCancelledQuery.c.collectiveOfferId == educational_models.CollectiveOffer.id,
                ).filter(educational_models.CollectiveOffer.status == offer_mixin.OfferStatus.EXPIRED.name)
            case _:
                query = query.filter(educational_models.CollectiveOffer.status == offer_mixin.OfferStatus[status].name)
    if period_beginning_date is not None or period_ending_date is not None:
        subquery = (
            educational_models.CollectiveStock.query.with_entities(educational_models.CollectiveStock.collectiveOfferId)
            .distinct(educational_models.CollectiveStock.collectiveOfferId)
            .join(educational_models.CollectiveOffer)
            .join(offerers_models.Venue)
        )
        if period_beginning_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", educational_models.CollectiveStock.beginningDatetime),
                )
                >= period_beginning_date
            )
        if period_ending_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", educational_models.CollectiveStock.beginningDatetime),
                )
                <= period_ending_date
            )
        if venue_id is not None:
            subquery = subquery.filter(educational_models.CollectiveOffer.venueId == venue_id)
        elif offerer_id is not None:
            subquery = subquery.filter(offerers_models.Venue.managingOffererId == offerer_id)
        elif not user_is_admin:
            subquery = (
                subquery.join(offerers_models.Offerer)
                .join(offerers_models.UserOfferer)
                .filter(offerers_models.UserOfferer.userId == user_id, offerers_models.UserOfferer.isValidated)
            )
        q2 = subquery.subquery()
        query = query.join(q2, q2.c.collectiveOfferId == educational_models.CollectiveOffer.id)
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
) -> flask_sqlalchemy.BaseQuery:
    query = educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.validation != models.OfferValidationStatus.DRAFT
    )

    if period_beginning_date is not None or period_ending_date is not None:
        query = query.filter(sa.false())

    if not user_is_admin:
        query = (
            query.join(offerers_models.Venue)
            .join(offerers_models.Offerer)
            .join(offerers_models.UserOfferer)
            .filter(offerers_models.UserOfferer.userId == user_id, offerers_models.UserOfferer.isValidated)
        )
    if offerer_id is not None:
        if user_is_admin:
            query = query.join(offerers_models.Venue)
        query = query.filter(offerers_models.Venue.managingOffererId == offerer_id)
    if venue_id is not None:
        query = query.filter(educational_models.CollectiveOfferTemplate.venueId == venue_id)
    if category_id is not None:
        requested_subcategories = [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category.id == category_id
        ]
        query = query.filter(educational_models.CollectiveOfferTemplate.subcategoryId.in_(requested_subcategories))
    if name_keywords is not None:
        search = name_keywords
        if len(name_keywords) > 3:
            search = "%{}%".format(name_keywords)
        # We should really be using `union` instead of `union_all` here since we don't want duplicates but
        # 1. it's unlikely that a book will contain its EAN in its name
        # 2. we need to migrate models.Offer.extraData to JSONB in order to use `union`
        query = query.filter(educational_models.CollectiveOfferTemplate.name.ilike(search))
    if status is not None:
        if status in (
            educational_models.CollectiveOfferDisplayedStatus.BOOKED.value,
            educational_models.CollectiveOfferDisplayedStatus.PREBOOKED.value,
        ):
            query = query.filter(
                educational_models.CollectiveOfferTemplate.status == offer_mixin.OfferStatus.SOLD_OUT.name
            )
        elif status in (
            educational_models.CollectiveOfferDisplayedStatus.ENDED.value,
            educational_models.CollectiveOfferDisplayedStatus.EXPIRED.value,
        ):
            query = query.filter(
                educational_models.CollectiveOfferTemplate.status == offer_mixin.OfferStatus.EXPIRED.name
            )
        else:
            query = query.filter(
                educational_models.CollectiveOfferTemplate.status == offer_mixin.OfferStatus[status].name
            )
    return query


def _filter_by_creation_mode(query: flask_sqlalchemy.BaseQuery, creation_mode: str) -> flask_sqlalchemy.BaseQuery:
    if creation_mode == MANUAL_CREATION_MODE:
        query = query.filter(models.Offer.lastProviderId.is_(None))
    if creation_mode == IMPORTED_CREATION_MODE:
        query = query.filter(models.Offer.lastProviderId.isnot(None))

    return query


def _filter_by_status(query: flask_sqlalchemy.BaseQuery, status: str) -> flask_sqlalchemy.BaseQuery:
    return query.filter(models.Offer.status == offer_mixin.OfferStatus[status].name)


def get_stocks_for_offers(offer_ids: list[int]) -> list[models.Stock]:
    return models.Stock.query.filter(models.Stock.offerId.in_(offer_ids)).all()


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


def get_offers_map_by_id_at_provider(id_at_provider_list: list[str], venue: offerers_models.Venue) -> dict[str, int]:
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
        offers_map[custom_keys.compute_venue_reference(offer_id_at_provider, venue_id)] = offer_id

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
    active_offers_query = _filter_by_status(active_offers_query, offer_mixin.OfferStatus.ACTIVE.name)

    n_active_offers = active_offers_query.distinct(models.Offer.id).count()

    n_active_collective_offer = (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.venueId == venue_id)
        .filter(educational_models.CollectiveOffer.status == offer_mixin.OfferStatus.ACTIVE.name)
        .distinct(educational_models.CollectiveOffer.id)
        .count()
    )

    n_active_collective_offer_template = (
        educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.venueId == venue_id
        )
        .filter(educational_models.CollectiveOfferTemplate.status == offer_mixin.OfferStatus.ACTIVE.name)
        .distinct(educational_models.CollectiveOfferTemplate.id)
        .count()
    )

    return n_active_offers + n_active_collective_offer + n_active_collective_offer_template


def get_sold_out_offers_count_for_venue(venue_id: int) -> int:
    sold_out_offers_query = models.Offer.query.filter(models.Offer.venueId == venue_id)
    sold_out_offers_query = _filter_by_status(sold_out_offers_query, offer_mixin.OfferStatus.SOLD_OUT.name)

    n_sold_out_offers = sold_out_offers_query.distinct(models.Offer.id).count()

    n_sold_out_collective_offers = (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.venueId == venue_id)
        .filter(educational_models.CollectiveOffer.status == offer_mixin.OfferStatus.SOLD_OUT.name)
        .distinct(educational_models.CollectiveOffer.id)
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
            != sa.func.coalesce(
                sa.func.sum(bookings_models.Booking.quantity).filter(
                    bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED
                ),
                0,
            )
        )
        .all()
    ]


def find_event_stocks_happening_in_x_days(number_of_days: int) -> flask_sqlalchemy.BaseQuery:
    target_day = datetime.datetime.utcnow() + datetime.timedelta(days=number_of_days)
    start = datetime.datetime.combine(target_day, datetime.time.min)
    end = datetime.datetime.combine(target_day, datetime.time.max)

    return find_event_stocks_day(start, end)


def find_event_stocks_day(start: datetime.datetime, end: datetime.datetime) -> flask_sqlalchemy.BaseQuery:
    return (
        models.Stock.query.filter(models.Stock.beginningDatetime.between(start, end))
        .join(bookings_models.Booking)
        .filter(bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED)
        .distinct()
    )


def get_current_offer_validation_config() -> models.OfferValidationConfig | None:
    return models.OfferValidationConfig.query.order_by(models.OfferValidationConfig.id.desc()).first()


def get_expired_offers(interval: typing.List[datetime.datetime]) -> flask_sqlalchemy.BaseQuery:
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
        .having(sa.func.max(models.Stock.bookingLimitDatetime).between(*interval))  # type: ignore [arg-type]
        .group_by(models.Offer.id)
        .order_by(models.Offer.id)
    )


def find_today_event_stock_ids_metropolitan_france(
    today_min: datetime.datetime, today_max: datetime.datetime
) -> set[int]:
    not_overseas_france = sa.and_(
        sa.not_(offerers_models.Venue.departementCode.startswith("97")),
        sa.not_(offerers_models.Venue.departementCode.startswith("98")),
    )

    return _find_today_event_stock_ids_filter_by_departments(today_min, today_max, not_overseas_france)


def find_today_event_stock_ids_from_departments(
    today_min: datetime.datetime,
    today_max: datetime.datetime,
    postal_codes_prefixes: typing.Any,
) -> set[int]:
    departments = sa.and_(*[offerers_models.Venue.departementCode.startswith(code) for code in postal_codes_prefixes])
    return _find_today_event_stock_ids_filter_by_departments(today_min, today_max, departments)


def _find_today_event_stock_ids_filter_by_departments(
    today_min: datetime.datetime,
    today_max: datetime.datetime,
    departments_filter: typing.Any,
) -> set[int]:
    """
    Find stocks linked to offers that:
        * happen today;
        * are not cancelled;
        * matches the `departments_filter`.
    """
    base_query = find_event_stocks_day(today_min, today_max)
    query = base_query.join(offerers_models.Venue).filter(departments_filter).with_entities(models.Stock.id)

    return {stock.id for stock in query}


def delete_past_draft_collective_offers() -> None:
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    collective_offer_ids_tuple = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.dateCreated < yesterday,
        educational_models.CollectiveOffer.validation == models.OfferValidationStatus.DRAFT,
    ).with_entities(educational_models.CollectiveOffer.id)
    collective_offer_ids = [collective_offer_id for (collective_offer_id,) in collective_offer_ids_tuple]

    # Handle collective offers having a stock but user did not save institution association
    # Thus the collective offer is not fully created
    educational_models.CollectiveStock.query.filter(
        educational_models.CollectiveStock.collectiveOfferId.in_(collective_offer_ids)
    ).delete()
    educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id.in_(collective_offer_ids)
    ).delete()

    db.session.commit()


def get_available_activation_code(stock: models.Stock) -> models.ActivationCode | None:
    return models.ActivationCode.query.filter(
        models.ActivationCode.stockId == stock.id,
        models.ActivationCode.bookingId.is_(None),
        sa.or_(models.ActivationCode.expirationDate.is_(None), models.ActivationCode.expirationDate > sa.func.now()),
    ).first()


def get_offer_by_id(offer_id: int) -> models.Offer:
    try:
        return (
            models.Offer.query.filter(models.Offer.id == offer_id)
            .outerjoin(models.Stock, sa.and_(models.Stock.offerId == offer_id, sa.not_(models.Stock.isSoftDeleted)))  # type: ignore [type-var]
            .options(sa_orm.contains_eager(models.Offer.stocks))
            .options(sa_orm.joinedload(models.Offer.mediations))
            .options(sa_orm.joinedload(models.Offer.product, innerjoin=True))
            .options(
                sa_orm.joinedload(models.Offer.priceCategories).joinedload(models.PriceCategory.priceCategoryLabel)
            )
            .options(
                sa_orm.joinedload(models.Offer.venue, innerjoin=True).joinedload(
                    offerers_models.Venue.managingOfferer,
                    innerjoin=True,
                )
            )
            .one()
        )
    except sa_orm.exc.NoResultFound:
        raise exceptions.OfferNotFound()


def get_synchronized_offers_with_provider_for_venue(venue_id: int, provider_id: int) -> flask_sqlalchemy.BaseQuery:
    return models.Offer.query.filter(models.Offer.venueId == venue_id).filter(
        models.Offer.lastProviderId == provider_id  # pylint: disable=comparison-with-callable
    )


def update_stock_quantity_to_dn_booked_quantity(stock_id: int | None) -> None:
    if not stock_id:
        return
    models.Stock.query.filter(models.Stock.id == stock_id).update({"quantity": models.Stock.dnBookedQuantity})
    db.session.commit()


def get_paginated_active_offer_ids(batch_size: int, page: int = 1) -> list[int]:
    query = (
        models.Offer.query.with_entities(models.Offer.id)
        .filter(models.Offer.isActive.is_(True))
        .order_by(models.Offer.id)
        .offset((page - 1) * batch_size)  # first page is 1, not 0
        .limit(batch_size)
    )
    return [offer_id for offer_id, in query]


def get_paginated_offer_ids_by_venue_id(venue_id: int, limit: int, page: int = 0) -> list[int]:
    query = (
        models.Offer.query.with_entities(models.Offer.id)
        .filter(models.Offer.venueId == venue_id)
        .order_by(models.Offer.id)
        .offset(page * limit)  # first page is 0
        .limit(limit)
    )
    return [offer_id for offer_id, in query]


def exclude_offers_from_inactive_venue_provider(query: flask_sqlalchemy.BaseQuery) -> flask_sqlalchemy.BaseQuery:
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
                providers_models.VenueProvider.isActive.is_(True),
                providers_models.Provider.localClass == providers_constants.PASS_CULTURE_STOCKS_FAKE_CLASS_NAME,
            )
        )
    )


def get_next_product_id_from_database() -> int:
    sequence: sa.Sequence = sa.Sequence("product_id_seq")
    return db.session.execute(sequence)


def has_active_offer_with_ean(ean: str | None, venue: offerers_models.Venue) -> bool:
    if not ean:
        # We should never be there (an ean or an ean must be given), in case we are alert sentry.
        logger.error("Could not search for an offer without ean")
    return db.session.query(
        models.Offer.query.filter(
            models.Offer.venue == venue, models.Offer.isActive.is_(True), models.Offer.extraData["ean"].astext == ean
        ).exists()
    ).scalar()
