import datetime
import enum
import logging
import operator
import typing

from flask_sqlalchemy import BaseQuery
import pytz
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql import and_
from sqlalchemy.sql import or_

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus as DisplayedStatus
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers import models as providers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import custom_keys
from pcapi.utils import string as string_utils

from . import exceptions
from . import models


logger = logging.getLogger(__name__)


IMPORTED_CREATION_MODE = "imported"
MANUAL_CREATION_MODE = "manual"

LIMIT_STOCKS_PER_PAGE = 20
STOCK_LIMIT_TO_DELETE = 50

OFFER_LOAD_OPTIONS = typing.Iterable[
    typing.Literal[
        "stock",
        "mediations",
        "product",
        "price_category",
        "venue",
        "bookings_count",
        "offerer_address",
        "future_offer",
        "pending_bookings",
    ]
]


class StocksOrderedBy(str, enum.Enum):
    DATE = "DATE"
    TIME = "TIME"
    BEGINNING_DATETIME = "BEGINNING_DATETIME"
    PRICE_CATEGORY_ID = "PRICE_CATEGORY_ID"
    BOOKING_LIMIT_DATETIME = "BOOKING_LIMIT_DATETIME"
    REMAINING_QUANTITY = "REMAINING_QUANTITY"  # quantity - dnBookedQuantity
    DN_BOOKED_QUANTITY = "DN_BOOKED_QUANTITY"


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
    period_beginning_date: datetime.date | None = None,
    period_ending_date: datetime.date | None = None,
    offerer_address_id: int | None = None,
) -> list[models.Offer]:
    query = get_offers_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        offerer_address_id=offerer_address_id,
        name_keywords_or_ean=name_keywords_or_ean,
        creation_mode=creation_mode,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
    )

    offers = (
        query.options(
            sa.orm.load_only(
                models.Offer.id,
                models.Offer.name,
                models.Offer.isActive,
                models.Offer.subcategoryId,
                models.Offer.validation,
                models.Offer.extraData,
                models.Offer.lastProviderId,
            )
        )
        .options(
            sa_orm.joinedload(models.Offer.venue)
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.departementCode,
                offerers_models.Venue.isVirtual,
            )
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.id, offerers_models.Offerer.name),
            sa_orm.joinedload(models.Offer.venue)
            .joinedload(offerers_models.Venue.offererAddress)
            .joinedload(offerers_models.OffererAddress.address),
            sa_orm.joinedload(models.Offer.venue)
            .joinedload(offerers_models.Venue.offererAddress)
            .with_expression(
                offerers_models.OffererAddress._isEditable, offerers_models.OffererAddress.isEditable.expression  # type: ignore [attr-defined]
            ),
        )
        .options(
            sa_orm.joinedload(models.Offer.stocks).load_only(
                models.Stock.id,
                models.Stock.beginningDatetime,
                models.Stock.bookingLimitDatetime,
                models.Stock.quantity,
                models.Stock.dnBookedQuantity,
                models.Stock.isSoftDeleted,
            )
        )
        .options(
            sa_orm.joinedload(models.Offer.mediations).load_only(
                models.Mediation.id,
                models.Mediation.credit,
                models.Mediation.dateCreated,
                models.Mediation.isActive,
                models.Mediation.thumbCount,
            )
        )
        .options(
            sa_orm.joinedload(models.Offer.product)
            .load_only(
                models.Product.id,
                models.Product.thumbCount,
            )
            .joinedload(models.Product.productMediations)
        )
        .options(sa_orm.joinedload(models.Offer.lastProvider).load_only(providers_models.Provider.localClass))
        .options(
            sa_orm.joinedload(models.Offer.offererAddress).joinedload(offerers_models.OffererAddress.address),
            sa_orm.joinedload(models.Offer.offererAddress).with_expression(
                offerers_models.OffererAddress._isEditable, offerers_models.OffererAddress.isEditable.expression  # type: ignore [attr-defined]
            ),
        )
        .limit(offers_limit)
        .all()
    )

    # Do not use `ORDER BY` in SQL, which sometimes applies on a very large result set
    # _before_ the `LIMIT` clause (and kills performance).
    if len(offers) < offers_limit:
        offers = sorted(offers, key=operator.attrgetter("id"), reverse=True)

    return offers


def get_offers_by_publication_date(publication_date: datetime.datetime | None = None) -> BaseQuery:
    if publication_date is None:
        publication_date = datetime.datetime.utcnow()
    publication_date = publication_date.replace(minute=0, second=0, microsecond=0, tzinfo=None)
    future_offers_subquery = db.session.query(models.FutureOffer.offerId).filter_by(publicationDate=publication_date)
    return models.Offer.query.filter(models.Offer.id.in_(future_offers_subquery))


def get_offers_by_ids(user: users_models.User, offer_ids: list[int]) -> BaseQuery:
    query = models.Offer.query
    if not user.has_admin_role:
        query = (
            query.join(offerers_models.Venue)
            .join(offerers_models.Offerer)
            .join(offerers_models.UserOfferer)
            .filter(offerers_models.UserOfferer.userId == user.id, offerers_models.UserOfferer.isValidated)
        )
    query = query.filter(models.Offer.id.in_(offer_ids))
    return query


def get_offers_details(offer_ids: list[int]) -> BaseQuery:
    return (
        models.Offer.query.options(
            sa_orm.joinedload(models.Offer.stocks)
            .joinedload(models.Stock.priceCategory)
            .joinedload(models.PriceCategory.priceCategoryLabel)
        )
        .options(
            sa_orm.joinedload(models.Offer.venue)
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.name, offerers_models.Offerer.validationStatus, offerers_models.Offerer.isActive
            )
        )
        .options(sa_orm.joinedload(models.Offer.venue).joinedload(offerers_models.Venue.googlePlacesInfo))
        .options(sa_orm.joinedload(models.Offer.mediations))
        .options(sa_orm.joinedload(models.Offer.reactions))
        .options(
            sa_orm.joinedload(models.Offer.product)
            .load_only(models.Product.id, models.Product.last_30_days_booking, models.Product.thumbCount)
            .joinedload(models.Product.productMediations)
        )
        .options(sa_orm.joinedload(models.Offer.product).joinedload(models.Product.reactions))
        .outerjoin(models.Offer.lastProvider)
        .options(sa_orm.contains_eager(models.Offer.lastProvider).load_only(providers_models.Provider.localClass))
        .filter(models.Offer.id.in_(offer_ids), models.Offer.validation == models.OfferValidationStatus.APPROVED)
    )


def get_offers_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None = None,
    status: str | None = None,
    venue_id: int | None = None,
    category_id: str | None = None,
    offerer_address_id: int | None = None,
    name_keywords_or_ean: str | None = None,
    creation_mode: str | None = None,
    period_beginning_date: datetime.date | None = None,
    period_ending_date: datetime.date | None = None,
) -> BaseQuery:
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
    if offerer_address_id is not None:
        query = query.filter(models.Offer.offererAddressId == offerer_address_id)
    if creation_mode is not None:
        query = _filter_by_creation_mode(query, creation_mode)
    if category_id is not None:
        requested_subcategories = [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category.id == category_id
        ]
        query = query.filter(models.Offer.subcategoryId.in_(requested_subcategories))
    if name_keywords_or_ean is not None:
        if string_utils.is_ean_valid(name_keywords_or_ean):
            query = query.filter(models.Offer.extraData["ean"].astext == name_keywords_or_ean)
        else:
            search = name_keywords_or_ean
            if len(name_keywords_or_ean) > 3:
                search = "%{}%".format(name_keywords_or_ean)
            query = query.filter(models.Offer.name.ilike(search))
    if status is not None:
        query = _filter_by_status(query, status)
    if period_beginning_date is not None or period_ending_date is not None:
        offer_alias = sa.orm.aliased(models.Offer)
        stock_query = (
            models.Stock.query.join(offer_alias)
            .join(offerers_models.Venue)
            .filter(models.Stock.isSoftDeleted.is_(False))
            .filter(models.Stock.offerId == models.Offer.id)
        )
        if period_beginning_date is not None:
            stock_query = stock_query.filter(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                )
                >= period_beginning_date
            )
        if period_ending_date is not None:
            stock_query = stock_query.filter(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                )
                <= datetime.datetime.combine(period_ending_date, datetime.time.max),
            )
        query = query.filter(stock_query.exists())
    return query


def get_collective_offers_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None = None,
    statuses: list[str] | None = None,
    venue_id: int | None = None,
    provider_id: int | None = None,
    category_id: str | None = None,
    name_keywords: str | None = None,
    period_beginning_date: datetime.date | None = None,
    period_ending_date: datetime.date | None = None,
    formats: list[subcategories.EacFormat] | None = None,
) -> BaseQuery:
    query = educational_models.CollectiveOffer.query

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
    if provider_id is not None:
        query = query.filter(educational_models.CollectiveOffer.providerId == provider_id)
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
    if statuses:
        query = _filter_collective_offers_by_statuses(query, statuses)

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
                <= datetime.datetime.combine(period_ending_date, datetime.time.max),
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
    if formats:
        query = query.filter(
            educational_models.CollectiveOffer.formats.overlap(postgresql.array((format.name for format in formats)))
        )
    return query


def get_collective_offers_template_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None = None,
    statuses: list[str] | None = None,
    venue_id: int | None = None,
    provider_id: int | None = None,
    category_id: str | None = None,
    name_keywords: str | None = None,
    period_beginning_date: datetime.date | None = None,
    period_ending_date: datetime.date | None = None,
    formats: list[subcategories.EacFormat] | None = None,
) -> BaseQuery:
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
    if provider_id is not None:
        query = query.filter(educational_models.CollectiveOfferTemplate.providerId == provider_id)
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
    if statuses:
        query_filters: list = []
        if DisplayedStatus.BOOKED.value in statuses or DisplayedStatus.PREBOOKED.value in statuses:
            query_filters.append(
                educational_models.CollectiveOfferTemplate.status == offer_mixin.CollectiveOfferStatus.SOLD_OUT.name
            )
        if DisplayedStatus.ENDED.value in statuses or DisplayedStatus.EXPIRED.value in statuses:
            query_filters.append(
                educational_models.CollectiveOfferTemplate.status == offer_mixin.CollectiveOfferStatus.EXPIRED.name
            )
        remaining_statuses = set(statuses) - {
            DisplayedStatus.BOOKED.value,
            DisplayedStatus.PREBOOKED.value,
            DisplayedStatus.ENDED.value,
            DisplayedStatus.EXPIRED.value,
        }
        for status in remaining_statuses:
            query_filters.append(
                educational_models.CollectiveOfferTemplate.status == offer_mixin.CollectiveOfferStatus[status].name
            )
        if query_filters:
            query = query.filter(or_(*query_filters))
    if formats:
        query = query.filter(
            educational_models.CollectiveOfferTemplate.formats.overlap(
                postgresql.array((format.name for format in formats))
            )
        )
    return query


def _filter_by_creation_mode(query: BaseQuery, creation_mode: str) -> BaseQuery:
    if creation_mode == MANUAL_CREATION_MODE:
        query = query.filter(models.Offer.lastProviderId.is_(None))
    if creation_mode == IMPORTED_CREATION_MODE:
        query = query.filter(models.Offer.lastProviderId.is_not(None))

    return query


def _filter_by_status(query: BaseQuery, status: str) -> BaseQuery:
    return query.filter(models.Offer.status == offer_mixin.OfferStatus[status].name)


def _filter_collective_offers_by_statuses(query: BaseQuery, statuses: list[str] | None) -> BaseQuery:
    """
    Filter a SQLAlchemy query for CollectiveOffers based on a list of statuses.

    This function modifies the input query to filter CollectiveOffers based on their CollectiveOfferDisplayedStatus.

    Args:
      query (BaseQuery): The initial query to be filtered.
      statuses (list[str]): A list of status strings to filter by.

    Returns:
      BaseQuery: The modified query with applied filters.
    """
    on_collective_offer_filters: list = []
    on_booking_status_filter: list = []

    if statuses is None or len(statuses) == 0:
        # if statuses is empty we return no orders
        return query

    offer_id_with_booking_status_subquery, query_with_booking = add_last_booking_status_to_collective_offer_query(query)
    if DisplayedStatus.BOOKED.value in statuses or DisplayedStatus.PREBOOKED.value in statuses:
        # all displayedStatus with an offer that has NOT expired

        allowed_booking_status = set()
        if DisplayedStatus.BOOKED.value in statuses:
            allowed_booking_status.update(
                {
                    educational_models.CollectiveBookingStatus.CONFIRMED.value,
                    educational_models.CollectiveBookingStatus.USED.value,
                }
            )
        if DisplayedStatus.PREBOOKED.value in statuses:
            allowed_booking_status.add(educational_models.CollectiveBookingStatus.PENDING.value)

        on_booking_status_filter.append(
            and_(
                offer_id_with_booking_status_subquery.c.status.in_(allowed_booking_status),
                educational_models.CollectiveOffer.status != offer_mixin.CollectiveOfferStatus.EXPIRED.name,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )

    allowed_expired_booking_status: set[educational_models.CollectiveBookingStatus | None] = set()
    if DisplayedStatus.ENDED.value in statuses or DisplayedStatus.REIMBURSED.value in statuses:
        # all displayedStatus with an offer that has expired
        if DisplayedStatus.ENDED.value in statuses:
            # TODO(anoukhello - 08/08/24) remove REIMBURSED status once it is handled in frontend filters
            allowed_expired_booking_status.update(
                {educational_models.CollectiveBookingStatus.USED, educational_models.CollectiveBookingStatus.REIMBURSED}
            )
        if DisplayedStatus.REIMBURSED.value in statuses:
            allowed_expired_booking_status.add(educational_models.CollectiveBookingStatus.REIMBURSED)

        on_booking_status_filter.append(
            and_(
                offer_id_with_booking_status_subquery.c.status.in_(allowed_expired_booking_status),
                educational_models.CollectiveOffer.status == offer_mixin.CollectiveOfferStatus.EXPIRED.name,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )

    if DisplayedStatus.EXPIRED.value in statuses:
        allowed_expired_booking_status.update(
            {
                educational_models.CollectiveBookingStatus.PENDING,
                educational_models.CollectiveBookingStatus.CANCELLED,
            }
        )

        on_booking_status_filter.append(
            and_(
                or_(
                    offer_id_with_booking_status_subquery.c.status == None,
                    offer_id_with_booking_status_subquery.c.status.in_(allowed_expired_booking_status),
                ),
                educational_models.CollectiveOffer.status == offer_mixin.CollectiveOfferStatus.EXPIRED.name,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )

    if DisplayedStatus.ACTIVE.value in statuses:
        on_booking_status_filter.append(
            and_(
                offer_id_with_booking_status_subquery.c.status == None,
                educational_models.CollectiveOffer.status == offer_mixin.CollectiveOfferStatus.ACTIVE.name,
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )
    if DisplayedStatus.INACTIVE.value in statuses:
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.status == offer_mixin.CollectiveOfferStatus.INACTIVE.name,
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )

    if DisplayedStatus.ARCHIVED.value in statuses:
        on_collective_offer_filters.append(educational_models.CollectiveOffer.isArchived == True)
    if DisplayedStatus.REJECTED.value in statuses:
        on_collective_offer_filters.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.REJECTED,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )
    if DisplayedStatus.PENDING.value in statuses:
        on_collective_offer_filters.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )

    # Add filters on `CollectiveBooking.Status`
    if on_booking_status_filter:
        substmt = query_with_booking.filter(or_(*on_booking_status_filter)).subquery()
        on_collective_offer_filters.append(educational_models.CollectiveOffer.id.in_(sa.select(substmt.c.id)))

    # Add filters on `CollectiveOffer`
    if on_collective_offer_filters:
        query = query.filter(or_(*on_collective_offer_filters))

    return query


def add_last_booking_status_to_collective_offer_query(
    query: BaseQuery,
) -> typing.Tuple[BaseQuery, BaseQuery]:
    last_booking_query = (
        educational_models.CollectiveBooking.query.with_entities(
            educational_models.CollectiveBooking.collectiveStockId,
            sa.func.max(educational_models.CollectiveBooking.dateCreated).label("maxdate"),
        )
        .group_by(educational_models.CollectiveBooking.collectiveStockId)
        .subquery()
    )

    collective_stock_with_last_booking_status_query = (
        educational_models.CollectiveStock.query.with_entities(
            educational_models.CollectiveStock.collectiveOfferId,
            educational_models.CollectiveBooking.status,
        )
        .outerjoin(educational_models.CollectiveBooking, educational_models.CollectiveStock.collectiveBookings)
        .join(
            last_booking_query,
            sa.and_(
                educational_models.CollectiveBooking.collectiveStockId == last_booking_query.c.collectiveStockId,
                educational_models.CollectiveBooking.dateCreated == last_booking_query.c.maxdate,
            ),
        )
    )

    subquery = collective_stock_with_last_booking_status_query.subquery()

    query_with_booking = query.outerjoin(
        subquery,
        and_(
            subquery.c.collectiveOfferId == educational_models.CollectiveOffer.id,
            subquery.c.status.notin_([educational_models.CollectiveBookingStatus.CANCELLED.value]),
        ),
    )

    return subquery, query_with_booking


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
    offer_id: int
    for offer_id, offer_id_at_provider in (
        db.session.query(models.Offer.id, models.Offer.idAtProvider)
        .filter(models.Offer.venueId == venue_id, models.Offer.idAtProvider.in_(id_at_provider_list))
        .all()
    ):
        offers_map[custom_keys.compute_venue_reference(offer_id_at_provider, venue_id)] = offer_id

    return offers_map


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


def is_id_at_provider_taken_by_another_venue_offer(venue_id: int, id_at_provider: str, offer_id: int | None) -> bool:
    """
    Return `True` if `id_at_provider` is already used to identify another venue offer.
    """
    base_query = models.Offer.query.filter(
        models.Offer.venueId == venue_id,
        models.Offer.idAtProvider == id_at_provider,
    )

    if offer_id:
        base_query = base_query.filter(models.Offer.id != offer_id)

    return db.session.query(base_query.exists()).scalar()


def get_active_offers_count_for_venue(venue_id: int) -> int:
    active_offers_query = models.Offer.query.filter(models.Offer.venueId == venue_id)
    active_offers_query = _filter_by_status(active_offers_query, offer_mixin.OfferStatus.ACTIVE.name)

    n_active_offers = active_offers_query.distinct(models.Offer.id).count()

    n_active_collective_offer = (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.venueId == venue_id)
        .filter(educational_models.CollectiveOffer.status == offer_mixin.CollectiveOfferStatus.ACTIVE.name)
        .distinct(educational_models.CollectiveOffer.id)
        .count()
    )

    n_active_collective_offer_template = (
        educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.venueId == venue_id
        )
        .filter(educational_models.CollectiveOfferTemplate.status == offer_mixin.CollectiveOfferStatus.ACTIVE.name)
        .distinct(educational_models.CollectiveOfferTemplate.id)
        .count()
    )

    return n_active_offers + n_active_collective_offer + n_active_collective_offer_template


def get_sold_out_offers_count_for_venue(venue_id: int) -> int:
    sold_out_offers_query = models.Offer.query.filter(models.Offer.venueId == venue_id)
    sold_out_offers_query = _filter_by_status(sold_out_offers_query, offer_mixin.CollectiveOfferStatus.SOLD_OUT.name)

    n_sold_out_offers = sold_out_offers_query.distinct(models.Offer.id).count()

    n_sold_out_collective_offers = (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.venueId == venue_id)
        .filter(educational_models.CollectiveOffer.status == offer_mixin.CollectiveOfferStatus.SOLD_OUT.name)
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
    # Use `with_for_update()` to make sure we lock the stock while performing
    # the booking checks and update the `dnBookedQuantity`
    # This is required to prevent bugs due to concurrent access
    # Also call `populate_existing()` to make sure we don't use something
    # older from the SQLAlchemy's session.
    stock = (
        models.Stock.query.filter_by(id=stock_id)
        .populate_existing()
        .with_for_update()
        .options(sa.orm.joinedload(models.Stock.offer, innerjoin=True))
        .one_or_none()
    )
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


def find_event_stocks_happening_in_x_days(number_of_days: int) -> BaseQuery:
    target_day = datetime.datetime.utcnow() + datetime.timedelta(days=number_of_days)
    start = datetime.datetime.combine(target_day, datetime.time.min)
    end = datetime.datetime.combine(target_day, datetime.time.max)

    return find_event_stocks_day(start, end)


def find_event_stocks_day(start: datetime.datetime, end: datetime.datetime) -> BaseQuery:
    return (
        models.Stock.query.filter(models.Stock.beginningDatetime.between(start, end))
        .join(bookings_models.Booking)
        .filter(bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED)
        .distinct()
    )


def get_expired_offers(interval: list[datetime.datetime]) -> BaseQuery:
    """Return a query of offers whose latest booking limit occurs within
    the given interval.

    Inactive or deleted offers are ignored.
    """
    return (
        models.Offer.query.join(models.Stock)
        .filter(
            models.Offer.isActive.is_(True),
            models.Stock.isSoftDeleted.is_(False),
            models.Stock.bookingLimitDatetime.is_not(None),
        )
        .having(sa.func.max(models.Stock.bookingLimitDatetime).between(*interval))  # type: ignore[arg-type]
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


def delete_future_offer(offer_id: int) -> None:
    models.FutureOffer.query.filter_by(offerId=offer_id).delete()


def get_available_activation_code(stock: models.Stock) -> models.ActivationCode | None:
    activable_code = next(
        (
            code
            for code in stock.activationCodes
            if code.bookingId is None
            and (code.expirationDate is None or code.expirationDate > datetime.datetime.utcnow())
        ),
        None,
    )
    return activable_code


def get_bookings_count_subquery(offer_id: int) -> sa.sql.selectable.ScalarSelect:
    return (
        sa.select(sa.func.coalesce(sa.func.sum(models.Stock.dnBookedQuantity), 0))
        .select_from(models.Stock)
        .where(models.Stock.offerId == models.Offer.id)
        .correlate(models.Offer)
        .scalar_subquery()
    )


def is_non_free_offer_subquery(offer_id: int) -> sa.sql.selectable.Exists:
    return (
        sa.select(1)
        .select_from(models.Stock)
        .where(sa.and_(models.Stock.offerId == models.Offer.id, models.Stock.price > 0))
        .correlate(models.Offer)
        .exists()
    )


def get_pending_bookings_subquery(offer_id: int) -> sa.sql.selectable.Exists:
    return (
        sa.select(bookings_models.Booking.id)
        .join(models.Stock, models.Stock.id == bookings_models.Booking.stockId)
        .filter(
            models.Stock.offerId == offer_id,
            bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
        )
        .exists()
    )


def get_offer_by_id(offer_id: int, load_options: OFFER_LOAD_OPTIONS = ()) -> models.Offer:
    try:
        query = models.Offer.query.filter(models.Offer.id == offer_id)
        if "stock" in load_options:
            query = query.outerjoin(
                models.Stock, sa.and_(models.Stock.offerId == offer_id, sa.not_(models.Stock.isSoftDeleted))
            ).options(sa_orm.contains_eager(models.Offer.stocks))
        if "mediations" in load_options:
            query = query.options(sa_orm.joinedload(models.Offer.mediations))
        if "product" in load_options:
            query = query.options(sa_orm.joinedload(models.Offer.product))
        if "price_category" in load_options:
            query = query.options(
                sa_orm.joinedload(models.Offer.priceCategories).joinedload(models.PriceCategory.priceCategoryLabel)
            )
        if "venue" in load_options:
            query = query.options(
                sa_orm.joinedload(models.Offer.venue, innerjoin=True).joinedload(
                    offerers_models.Venue.managingOfferer,
                    innerjoin=True,
                )
            )
        if "bookings_count" in load_options:
            query = query.options(
                sa_orm.with_expression(models.Offer.bookingsCount, get_bookings_count_subquery(offer_id))
            )
        if "offerer_address" in load_options:
            query = query.options(
                sa_orm.joinedload(models.Offer.offererAddress).joinedload(offerers_models.OffererAddress.address),
                sa_orm.joinedload(models.Offer.offererAddress).with_expression(
                    offerers_models.OffererAddress._isEditable, offerers_models.OffererAddress.isEditable.expression  # type: ignore [attr-defined]
                ),
                sa_orm.joinedload(models.Offer.venue)
                .joinedload(offerers_models.Venue.offererAddress)
                .joinedload(offerers_models.OffererAddress.address),
                sa_orm.joinedload(models.Offer.venue)
                .joinedload(offerers_models.Venue.offererAddress)
                .with_expression(
                    offerers_models.OffererAddress._isEditable, offerers_models.OffererAddress.isEditable.expression  # type: ignore [attr-defined]
                ),
            )
        if "future_offer" in load_options:
            query = query.outerjoin(models.Offer.futureOffer).options(sa_orm.contains_eager(models.Offer.futureOffer))
        if "pending_bookings" in load_options:
            query = query.options(
                sa_orm.with_expression(models.Offer.hasPendingBookings, get_pending_bookings_subquery(offer_id))
            )

        return query.one()
    except sa_orm.exc.NoResultFound:
        raise exceptions.OfferNotFound()


def get_offer_and_extradata(offer_id: int) -> models.Offer | None:
    return (
        db.session.query(models.Offer)
        .filter(models.Offer.id == offer_id)
        .outerjoin(models.Stock, sa.and_(models.Stock.offerId == offer_id, sa.not_(models.Stock.isSoftDeleted)))
        .options(sa_orm.contains_eager(models.Offer.stocks))
        .options(sa_orm.joinedload(models.Offer.mediations))
        .options(sa_orm.joinedload(models.Offer.priceCategories).joinedload(models.PriceCategory.priceCategoryLabel))
        .options(sa_orm.with_expression(models.Offer.isNonFreeOffer, is_non_free_offer_subquery(offer_id)))
        .options(sa_orm.with_expression(models.Offer.bookingsCount, get_bookings_count_subquery(offer_id)))
        .one_or_none()
    )


def offer_has_stocks(offer_id: int) -> bool:
    return db.session.query(
        models.Stock.query.filter(models.Stock.offerId == offer_id, sa.not_(models.Stock.isSoftDeleted)).exists()
    ).scalar()


def offer_has_bookable_stocks(offer_id: int) -> bool:
    return db.session.query(
        models.Stock.query.filter(models.Stock.offerId == offer_id, models.Stock._bookable).exists()
    ).scalar()


def _order_stocks_by(query: BaseQuery, order_by: StocksOrderedBy, order_by_desc: bool) -> BaseQuery:
    column: sa_orm.Mapped[int] | sa.cast[sa.Date | sa.Time, sa_orm.Mapped[datetime.datetime | None]]
    match order_by:
        case StocksOrderedBy.DATE:
            column = sa.cast(models.Stock.beginningDatetime, sa.Date)
        case StocksOrderedBy.TIME:
            column = sa.cast(models.Stock.beginningDatetime, sa.Time)
        case StocksOrderedBy.BEGINNING_DATETIME:
            column = models.Stock.beginningDatetime
        case StocksOrderedBy.PRICE_CATEGORY_ID:
            column = models.Stock.priceCategoryId
        case StocksOrderedBy.BOOKING_LIMIT_DATETIME:
            column = models.Stock.bookingLimitDatetime
        case StocksOrderedBy.REMAINING_QUANTITY:
            column = models.Stock.remainingQuantity  # type: ignore[assignment]
        case StocksOrderedBy.DN_BOOKED_QUANTITY:
            column = models.Stock.dnBookedQuantity
    if order_by_desc:
        return query.order_by(column.desc(), models.Stock.id.desc())
    return query.order_by(column, models.Stock.id)


def get_filtered_stocks(
    offer_id: int,
    venue: offerers_models.Venue,
    date: datetime.date | None = None,
    time: datetime.time | None = None,
    price_category_id: int | None = None,
    order_by: StocksOrderedBy = StocksOrderedBy.BEGINNING_DATETIME,
    order_by_desc: bool = False,
) -> BaseQuery:
    query = (
        models.Stock.query.join(models.Offer)
        .join(offerers_models.Venue)
        .filter(
            models.Stock.offerId == offer_id,
            models.Stock.isSoftDeleted == False,
        )
    )
    if price_category_id is not None:
        query = query.filter(models.Stock.priceCategoryId == price_category_id)
    if date is not None:
        query = query.filter(sa.cast(models.Stock.beginningDatetime, sa.Date) == date)
    if time is not None:
        # Transform user time input into the venue timezone
        dt = datetime.datetime.combine(datetime.datetime.today(), time)
        venue_timezone = pytz.timezone(venue.timezone)  # type: ignore[arg-type]
        venue_time = dt.replace(tzinfo=pytz.utc).astimezone(venue_timezone).time()

        query = query.filter(
            sa.cast(
                sa.func.timezone(
                    offerers_models.Venue.timezone, sa.func.timezone("UTC", models.Stock.beginningDatetime)
                ),
                sa.Time,
            )
            >= venue_time.replace(second=0),
            sa.cast(
                sa.func.timezone(
                    offerers_models.Venue.timezone, sa.func.timezone("UTC", models.Stock.beginningDatetime)
                ),
                sa.Time,
            )
            <= venue_time.replace(second=59),
        )
    return _order_stocks_by(query, order_by, order_by_desc)


def hard_delete_filtered_stocks(
    offer_id: int,
    venue: offerers_models.Venue,
    date: datetime.date | None = None,
    time: datetime.time | None = None,
    price_category_id: int | None = None,
) -> None:
    subquery = get_filtered_stocks(offer_id, venue, date, time, price_category_id)
    subquery = subquery.with_entities(models.Stock.id)
    models.Stock.query.filter(models.Stock.id.in_(subquery)).delete(synchronize_session=False)
    db.session.commit()


def get_paginated_stocks(
    stocks_query: BaseQuery,
    stocks_limit_per_page: int = LIMIT_STOCKS_PER_PAGE,
    page: int = 1,
) -> BaseQuery:
    return stocks_query.offset((page - 1) * stocks_limit_per_page).limit(stocks_limit_per_page)


def get_synchronized_offers_with_provider_for_venue(venue_id: int, provider_id: int) -> BaseQuery:
    return models.Offer.query.filter(models.Offer.venueId == venue_id).filter(
        models.Offer.lastProviderId == provider_id
    )


def update_stock_quantity_to_dn_booked_quantity(stock_id: int | None) -> None:
    if not stock_id:
        return
    models.Stock.query.filter(models.Stock.id == stock_id).update({"quantity": models.Stock.dnBookedQuantity})
    db.session.flush()


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
                providers_models.VenueProvider.isActive.is_(True),
                providers_models.Provider.localClass == providers_constants.PASS_CULTURE_STOCKS_FAKE_CLASS_NAME,
            )
        )
    )


def get_next_offer_id_from_database() -> int:
    sequence: sa.Sequence = sa.Sequence("offer_id_seq")
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


def get_movie_product_by_allocine_id(allocine_id: str) -> models.Product | None:
    return models.Product.query.filter(models.Product.extraData["allocineId"] == allocine_id).one_or_none()


def get_movie_product_by_visa(visa: str) -> models.Product | None:
    return models.Product.query.filter(models.Product.extraData["visa"].astext == visa).one_or_none()
