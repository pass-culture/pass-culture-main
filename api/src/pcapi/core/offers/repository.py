import datetime
import enum
import logging
import operator
import typing

import pytz
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql import and_
from sqlalchemy.sql import or_

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models as educational_models
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers import models as providers_models
from pcapi.core.reactions import models as reactions_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.models.pc_object import BaseQuery
from pcapi.utils import custom_keys
from pcapi.utils import string as string_utils
from pcapi.utils.decorators import retry

from . import exceptions
from . import models


logger = logging.getLogger(__name__)


IMPORTED_CREATION_MODE = "imported"
MANUAL_CREATION_MODE = "manual"

LIMIT_STOCKS_PER_PAGE = 20
STOCK_LIMIT_TO_DELETE = 50

OFFER_LOAD_OPTIONS = typing.Iterable[
    typing.Literal[
        "bookings_count",
        "event_opening_hours",
        "future_offer",
        "headline_offer",
        "is_non_free_offer",
        "mediations",
        "offerer_address",
        "pending_bookings",
        "price_category",
        "product",
        "stock",
        "venue",
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
    *,
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
            sa_orm.load_only(
                models.Offer.id,
                models.Offer.name,
                models.Offer.isActive,
                models.Offer.subcategoryId,
                models.Offer.validation,
                models.Offer.ean,
                models.Offer._extraData,
                models.Offer.lastProviderId,
                models.Offer.offererAddressId,
                models.Offer.url,
            ).joinedload(models.Offer.headlineOffers)
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
                offerers_models.OffererAddress._isLinkedToVenue,
                offerers_models.OffererAddress.isLinkedToVenue.expression,  # type: ignore [attr-defined]
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
                offerers_models.OffererAddress._isLinkedToVenue,
                offerers_models.OffererAddress.isLinkedToVenue.expression,  # type: ignore [attr-defined]
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


def get_offers_by_publication_date(
    publication_date: datetime.datetime | None = None,
) -> tuple[BaseQuery, BaseQuery]:
    if publication_date is None:
        publication_date = datetime.datetime.utcnow()

    upper_bound = publication_date
    lower_bound = upper_bound - datetime.timedelta(minutes=15)

    future_offers_subquery = db.session.query(models.FutureOffer).filter(
        models.FutureOffer.publicationDate <= upper_bound,
        models.FutureOffer.publicationDate > lower_bound,
        sa.not_(models.FutureOffer.isSoftDeleted),
    )
    offer_ids_future = [future_offer.offerId for future_offer in future_offers_subquery]
    return (
        db.session.query(models.Offer).filter(models.Offer.id.in_(offer_ids_future)),
        future_offers_subquery,
    )


def get_offers_by_ids(user: users_models.User, offer_ids: list[int]) -> BaseQuery:
    query = db.session.query(models.Offer)
    if not user.has_admin_role:
        query = (
            query.join(offerers_models.Venue)
            .join(offerers_models.Offerer)
            .join(offerers_models.UserOfferer)
            .filter(
                offerers_models.UserOfferer.userId == user.id,
                offerers_models.UserOfferer.isValidated,
            )
        )
    query = query.filter(models.Offer.id.in_(offer_ids))
    return query


def get_offers_data_from_top_offers(top_offers: list[dict]) -> list[dict]:
    offer_data_by_id = {item["offerId"]: item for item in top_offers}
    offers = (
        db.session.query(models.Offer)
        .options(
            sa_orm.joinedload(models.Offer.mediations).load_only(
                models.Mediation.id,
                models.Mediation.isActive,
                models.Mediation.dateCreated,
                models.Mediation.thumbCount,
                models.Mediation.credit,
            )
        )
        .options(sa_orm.joinedload(models.Offer.headlineOffers))
        .options(
            sa_orm.joinedload(models.Offer.stocks).load_only(
                models.Stock.quantity,
                models.Stock.isSoftDeleted,
                models.Stock.beginningDatetime,
                models.Stock.dnBookedQuantity,
                models.Stock.bookingLimitDatetime,
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
        .filter(models.Offer.id.in_(offer_data_by_id.keys()))
        .order_by(models.Offer.id)
    )
    merged_data_list = []
    for offer in offers:
        if offer.id in offer_data_by_id:
            merged_data = {
                **{
                    "offerName": offer.name,
                    "image": offer.image,
                    "isHeadlineOffer": offer.is_headline_offer,
                },
                **offer_data_by_id[offer.id],
            }
            merged_data_list.append(merged_data)

    sorted_data_list = sorted(merged_data_list, key=lambda x: x["numberOfViews"], reverse=True)
    return sorted_data_list


def get_offers_details(offer_ids: list[int]) -> BaseQuery:
    return (
        db.session.query(models.Offer)
        .options(
            sa_orm.load_only(
                models.Offer.id,
                models.Offer.name,
                models.Offer.ean,
                models.Offer._extraData,
                models.Offer.withdrawalDetails,
                models.Offer.subcategoryId,
                models.Offer.url,
                models.Offer.isActive,
                models.Offer.lastProviderId,
                models.Offer.audioDisabilityCompliant,
                models.Offer.mentalDisabilityCompliant,
                models.Offer.motorDisabilityCompliant,
                models.Offer.visualDisabilityCompliant,
                models.Offer.venueId,
                models.Offer.isDuo,
                models.Offer.externalTicketOfficeUrl,
                models.Offer.productId,
            )
        )
        .options(
            sa_orm.selectinload(models.Offer.stocks)
            .load_only(
                models.Stock.idAtProviders,
                models.Stock.beginningDatetime,
                models.Stock.bookingLimitDatetime,
                models.Stock.features,
                models.Stock.price,
                models.Stock.offerId,
                models.Stock.isSoftDeleted,
                models.Stock.quantity,
                models.Stock.dnBookedQuantity,
            )
            .joinedload(models.Stock.priceCategory)
            .joinedload(models.PriceCategory.priceCategoryLabel)
        )
        .options(
            sa_orm.joinedload(models.Offer.venue)
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isPermanent,
                offerers_models.Venue.isOpenToPublic,
                offerers_models.Venue.bannerUrl,
                offerers_models.Venue.venueTypeCode,
                offerers_models.Venue.timezone,
            )
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.name,
                offerers_models.Offerer.validationStatus,
                offerers_models.Offerer.isActive,
            )
        )
        .options(sa_orm.joinedload(models.Offer.venue).joinedload(offerers_models.Venue.googlePlacesInfo))
        .options(
            sa_orm.joinedload(models.Offer.venue)
            .joinedload(offerers_models.Venue.offererAddress)
            .joinedload(offerers_models.OffererAddress.address)
        )
        .options(sa_orm.joinedload(models.Offer.offererAddress).joinedload(offerers_models.OffererAddress.address))
        .options(sa_orm.selectinload(models.Offer.mediations))
        .options(sa_orm.with_expression(models.Offer.likesCount, get_offer_reaction_count_subquery()))
        .options(
            sa_orm.joinedload(models.Offer.product)
            .load_only(
                models.Product.id,
                models.Product.description,
                models.Product.extraData,
                models.Product.last_30_days_booking,
                models.Product.thumbCount,
                models.Product.durationMinutes,
            )
            .options(sa_orm.with_expression(models.Product.likesCount, get_product_reaction_count_subquery()))
            .joinedload(models.Product.productMediations)
        )
        .options(sa_orm.joinedload(models.Offer.product).selectinload(models.Product.artists))
        .options(sa_orm.joinedload(models.Offer.headlineOffers))
        .outerjoin(models.Offer.lastProvider)
        .options(sa_orm.contains_eager(models.Offer.lastProvider).load_only(providers_models.Provider.localClass))
        .filter(
            models.Offer.id.in_(offer_ids),
            models.Offer.validation == models.OfferValidationStatus.APPROVED,
        )
    )


def get_offers_by_filters(
    *,
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
    query = db.session.query(models.Offer)

    if not user_is_admin:
        query = (
            query.join(offerers_models.Venue)
            .join(offerers_models.Offerer)
            .join(offerers_models.UserOfferer)
            .filter(
                offerers_models.UserOfferer.userId == user_id,
                offerers_models.UserOfferer.isValidated,
            )
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
            query = query.filter(models.Offer.ean == name_keywords_or_ean)
        else:
            search = name_keywords_or_ean
            if len(name_keywords_or_ean) > 3:
                search = "%{}%".format(name_keywords_or_ean)
            query = query.filter(models.Offer.name.ilike(search))
    if status is not None:
        query = _filter_by_status(query, status)
    if period_beginning_date is not None or period_ending_date is not None:
        offer_alias = sa_orm.aliased(models.Offer)
        stock_query = (
            db.session.query(models.Stock)
            .join(offer_alias)
            .outerjoin(
                offerers_models.OffererAddress,
                offer_alias.offererAddressId == offerers_models.OffererAddress.id,
            )
            .join(
                geography_models.Address,
                offerers_models.OffererAddress.addressId == geography_models.Address.id,
            )
            .filter(models.Stock.isSoftDeleted.is_(False))
            .filter(models.Stock.offerId == models.Offer.id)
        )
        target_timezone = sa.func.coalesce(geography_models.Address.timezone, offerers_models.Venue.timezone)
        if period_beginning_date is not None:
            stock_query = stock_query.filter(
                sa.func.timezone(
                    target_timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                )
                >= period_beginning_date
            )
        if period_ending_date is not None:
            stock_query = stock_query.filter(
                sa.func.timezone(
                    target_timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                )
                <= datetime.datetime.combine(period_ending_date, datetime.time.max),
            )

        query = query.filter(stock_query.exists())
    return query


def get_collective_offers_by_filters(
    *,
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None = None,
    statuses: list[educational_models.CollectiveOfferDisplayedStatus] | None = None,
    venue_id: int | None = None,
    provider_id: int | None = None,
    name_keywords: str | None = None,
    period_beginning_date: datetime.date | None = None,
    period_ending_date: datetime.date | None = None,
    formats: list[EacFormat] | None = None,
) -> BaseQuery:
    query = db.session.query(educational_models.CollectiveOffer)

    if not user_is_admin:
        query = (
            query.join(offerers_models.Venue)
            .join(offerers_models.Offerer)
            .join(offerers_models.UserOfferer)
            .filter(
                offerers_models.UserOfferer.userId == user_id,
                offerers_models.UserOfferer.isValidated,
            )
        )

    if offerer_id is not None:
        if user_is_admin:
            query = query.join(offerers_models.Venue)
        query = query.filter(offerers_models.Venue.managingOffererId == offerer_id)

    if venue_id is not None:
        query = query.filter(educational_models.CollectiveOffer.venueId == venue_id)

    if provider_id is not None:
        query = query.filter(educational_models.CollectiveOffer.providerId == provider_id)

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
            db.session.query(educational_models.CollectiveStock)
            .with_entities(educational_models.CollectiveStock.collectiveOfferId)
            .distinct(educational_models.CollectiveStock.collectiveOfferId)
            .join(educational_models.CollectiveOffer)
            .join(offerers_models.Venue)
        )
        if period_beginning_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", educational_models.CollectiveStock.startDatetime),
                )
                >= period_beginning_date
            )
        if period_ending_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", educational_models.CollectiveStock.startDatetime),
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
                .filter(
                    offerers_models.UserOfferer.userId == user_id,
                    offerers_models.UserOfferer.isValidated,
                )
            )
        q2 = subquery.subquery()
        query = query.join(q2, q2.c.collectiveOfferId == educational_models.CollectiveOffer.id)

    if formats:
        query = query.filter(
            educational_models.CollectiveOffer.formats.overlap(postgresql.array((format.name for format in formats)))
        )

    return query


def get_collective_offers_template_by_filters(
    *,
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None = None,
    statuses: list[educational_models.CollectiveOfferDisplayedStatus] | None = None,
    venue_id: int | None = None,
    name_keywords: str | None = None,
    period_beginning_date: datetime.date | None = None,
    period_ending_date: datetime.date | None = None,
    formats: list[EacFormat] | None = None,
) -> BaseQuery:
    query = db.session.query(educational_models.CollectiveOfferTemplate)

    if period_beginning_date is not None or period_ending_date is not None:
        query = query.filter(sa.false())

    if not user_is_admin:
        query = (
            query.join(offerers_models.Venue)
            .join(offerers_models.Offerer)
            .join(offerers_models.UserOfferer)
            .filter(
                offerers_models.UserOfferer.userId == user_id,
                offerers_models.UserOfferer.isValidated,
            )
        )

    if offerer_id is not None:
        if user_is_admin:
            query = query.join(offerers_models.Venue)
        query = query.filter(offerers_models.Venue.managingOffererId == offerer_id)

    if venue_id is not None:
        query = query.filter(educational_models.CollectiveOfferTemplate.venueId == venue_id)

    if name_keywords is not None:
        search = name_keywords
        if len(name_keywords) > 3:
            search = "%{}%".format(name_keywords)
        # We should really be using `union` instead of `union_all` here since we don't want duplicates but
        # 1. it's unlikely that a book will contain its EAN in its name
        # 2. we need to migrate models.Offer.extraData to JSONB in order to use `union`
        query = query.filter(educational_models.CollectiveOfferTemplate.name.ilike(search))

    if statuses:
        template_statuses = set(statuses) & set(educational_models.COLLECTIVE_OFFER_TEMPLATE_STATUSES)
        status_values = [status.value for status in template_statuses]
        query = query.filter(educational_models.CollectiveOfferTemplate.displayedStatus.in_(status_values))  # type: ignore[attr-defined]

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


def _filter_collective_offers_by_statuses(
    query: BaseQuery,
    statuses: list[educational_models.CollectiveOfferDisplayedStatus] | None,
) -> BaseQuery:
    """
    Filter a SQLAlchemy query for CollectiveOffers based on a list of statuses.

    This function modifies the input query to filter CollectiveOffers based on their CollectiveOfferDisplayedStatus.

    Args:
      query (BaseQuery): The initial query to be filtered.
      statuses (list[CollectiveOfferDisplayedStatus]): A list of status strings to filter by.

    Returns:
      BaseQuery: The modified query with applied filters.
    """
    on_collective_offer_filters: list = []
    on_booking_status_filter: list = []

    if not statuses:
        # if statuses is empty we return all offers
        return query

    offer_id_with_booking_status_subquery, query_with_booking = add_last_booking_status_to_collective_offer_query(query)

    if educational_models.CollectiveOfferDisplayedStatus.ARCHIVED in statuses:
        on_collective_offer_filters.append(educational_models.CollectiveOffer.isArchived == True)

    if educational_models.CollectiveOfferDisplayedStatus.DRAFT in statuses:
        on_collective_offer_filters.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.DRAFT,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )

    if educational_models.CollectiveOfferDisplayedStatus.UNDER_REVIEW in statuses:
        on_collective_offer_filters.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )

    if educational_models.CollectiveOfferDisplayedStatus.REJECTED in statuses:
        on_collective_offer_filters.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.REJECTED,
                educational_models.CollectiveOffer.isArchived == False,
            )
        )

    if educational_models.CollectiveOfferDisplayedStatus.HIDDEN in statuses:
        # if the statuses filter contains HIDDEN only, we need to return no collective_offer
        # otherwise we return offers depending on the other statuses in the filter
        on_collective_offer_filters.append(sa.false())

    if educational_models.CollectiveOfferDisplayedStatus.PUBLISHED in statuses:
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == None,
                educational_models.CollectiveOffer.hasBookingLimitDatetimesPassed == False,
            )
        )

    if educational_models.CollectiveOfferDisplayedStatus.PREBOOKED in statuses:
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == educational_models.CollectiveBookingStatus.PENDING,
                educational_models.CollectiveOffer.hasBookingLimitDatetimesPassed == False,
            )
        )

    if educational_models.CollectiveOfferDisplayedStatus.BOOKED in statuses:
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == educational_models.CollectiveBookingStatus.CONFIRMED,
                educational_models.CollectiveOffer.hasEndDatetimePassed == False,
            )
        )

    if educational_models.CollectiveOfferDisplayedStatus.ENDED in statuses:
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                or_(
                    offer_id_with_booking_status_subquery.c.status == educational_models.CollectiveBookingStatus.USED,
                    offer_id_with_booking_status_subquery.c.status
                    == educational_models.CollectiveBookingStatus.CONFIRMED,
                ),
                educational_models.CollectiveOffer.hasEndDatetimePassed == True,
            )
        )

    if educational_models.CollectiveOfferDisplayedStatus.REIMBURSED in statuses:
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == educational_models.CollectiveBookingStatus.REIMBURSED,
            )
        )

    if educational_models.CollectiveOfferDisplayedStatus.EXPIRED in statuses:
        # expired with a pending booking or no booking
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                educational_models.CollectiveOffer.hasBookingLimitDatetimesPassed == True,
                educational_models.CollectiveOffer.hasStartDatetimePassed == False,
                or_(
                    offer_id_with_booking_status_subquery.c.status
                    == educational_models.CollectiveBookingStatus.PENDING,
                    offer_id_with_booking_status_subquery.c.status == None,
                ),
            )
        )
        # expired with a booking cancelled with reason EXPIRED
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                educational_models.CollectiveOffer.hasBookingLimitDatetimesPassed == True,
                educational_models.CollectiveOffer.hasStartDatetimePassed == False,
                offer_id_with_booking_status_subquery.c.status == educational_models.CollectiveBookingStatus.CANCELLED,
                offer_id_with_booking_status_subquery.c.cancellationReason
                == educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            )
        )

    if educational_models.CollectiveOfferDisplayedStatus.CANCELLED in statuses:
        # Cancelled due to expired booking
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == educational_models.CollectiveBookingStatus.CANCELLED,
                offer_id_with_booking_status_subquery.c.cancellationReason
                == educational_models.CollectiveBookingCancellationReasons.EXPIRED,
                educational_models.CollectiveOffer.hasStartDatetimePassed == True,
            )
        )

        # Cancelled by admin / CA or on ADAGE
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == educational_models.CollectiveBookingStatus.CANCELLED,
                offer_id_with_booking_status_subquery.c.cancellationReason
                != educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            ),
        )

        # Cancelled due to no booking when the event has started
        on_booking_status_filter.append(
            and_(
                educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                educational_models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == None,
                educational_models.CollectiveOffer.hasStartDatetimePassed == True,
            ),
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
) -> typing.Tuple[typing.Any, BaseQuery]:
    last_booking_query = (
        db.session.query(educational_models.CollectiveBooking)
        .with_entities(
            educational_models.CollectiveBooking.collectiveStockId,
            sa.func.max(educational_models.CollectiveBooking.dateCreated).label("maxdate"),
        )
        .group_by(educational_models.CollectiveBooking.collectiveStockId)
        .subquery()
    )

    collective_stock_with_last_booking_status_query = (
        db.session.query(educational_models.CollectiveStock)
        .with_entities(
            educational_models.CollectiveStock.collectiveOfferId,
            educational_models.CollectiveStock.bookingLimitDatetime,
            educational_models.CollectiveBooking.status,
            educational_models.CollectiveBooking.cancellationReason,
        )
        .outerjoin(
            educational_models.CollectiveBooking,
            educational_models.CollectiveStock.collectiveBookings,
        )
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
        subquery.c.collectiveOfferId == educational_models.CollectiveOffer.id,
    )

    return subquery, query_with_booking


def get_products_map_by_provider_reference(
    id_at_providers: list[str],
) -> dict[str, models.Product]:
    products = (
        db.session.query(models.Product)
        .filter(models.Product.can_be_synchronized)
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
        .filter(
            models.Offer.idAtProvider.in_(id_at_provider_list),
            models.Offer.venue == venue,
        )
        .all()
    ):
        offers_map[offer_id_at_provider] = offer_id

    return offers_map


def get_offers_map_by_venue_reference(id_at_provider_list: list[str], venue_id: int) -> dict[str, int]:
    offers_map = {}
    offer_id: int
    for offer_id, offer_id_at_provider in (
        db.session.query(models.Offer.id, models.Offer.idAtProvider)
        .filter(
            models.Offer.venueId == venue_id,
            models.Offer.idAtProvider.in_(id_at_provider_list),
        )
        .all()
    ):
        offers_map[custom_keys.compute_venue_reference(offer_id_at_provider, venue_id)] = offer_id

    return offers_map


def get_stocks_by_id_at_providers(id_at_providers: list[str]) -> dict:
    stocks = (
        db.session.query(models.Stock)
        .filter(models.Stock.idAtProviders.in_(id_at_providers))
        .with_entities(
            models.Stock.id,
            models.Stock.idAtProviders,
            models.Stock.dnBookedQuantity,
            models.Stock.quantity,
            models.Stock.price,
        )
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
    base_query = db.session.query(models.Offer).filter(
        models.Offer.venueId == venue_id,
        models.Offer.idAtProvider == id_at_provider,
    )

    if offer_id:
        base_query = base_query.filter(models.Offer.id != offer_id)

    return db.session.query(base_query.exists()).scalar()


def is_id_at_provider_taken_by_another_offer_price_category(
    offer_id: int,
    id_at_provider: str,
    price_category_id: int | None,
) -> bool:
    """
    Return `True` if `id_at_provider` is already used to identify another offer price category
    """
    base_query = db.session.query(models.PriceCategory).filter(
        models.PriceCategory.offerId == offer_id,
        models.PriceCategory.idAtProvider == id_at_provider,
    )

    if price_category_id:
        base_query = base_query.filter(models.PriceCategory.id != price_category_id)

    return db.session.query(base_query.exists()).scalar()


def is_id_at_provider_taken_by_another_offer_stock(
    offer_id: int,
    id_at_provider: str,
    stock_id: int | None,
) -> bool:
    """
    Return `True` if `id_at_provider` is already used to identify another offer stock
    """
    base_query = db.session.query(models.Stock).filter(
        models.Stock.offerId == offer_id,
        models.Stock.idAtProviders == id_at_provider,
    )

    if stock_id:
        base_query = base_query.filter(models.Stock.id != stock_id)

    return db.session.query(base_query.exists()).scalar()


def lock_stocks_for_venue(venue_id: int) -> None:
    """Lock all stocks for the given venue. This is used to prevent concurrent
    modifications of stocks for the given venue.
    """
    (
        db.session.query(models.Stock)
        .join(models.Stock.offer)
        .filter(models.Offer.venueId == venue_id)
        .with_for_update()
        .options(sa.orm.load_only(models.Stock.id))
        .all()
    )


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
        db.session.query(models.Stock)
        .filter_by(id=stock_id)
        .populate_existing()
        .with_for_update()
        .options(sa_orm.joinedload(models.Stock.offer, innerjoin=True))
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
        db.session.query(models.Stock)
        .filter(models.Stock.beginningDatetime.between(start, end))
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
        db.session.query(models.Offer)
        .join(models.Stock)
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
        sa.not_(geography_models.Address.departmentCode.startswith("97")),
        sa.not_(geography_models.Address.departmentCode.startswith("98")),
    )

    return _find_today_event_stock_ids_filter_by_departments(today_min, today_max, not_overseas_france)


def find_today_event_stock_ids_from_departments(
    today_min: datetime.datetime,
    today_max: datetime.datetime,
    postal_codes_prefixes: typing.Any,
) -> set[int]:
    departments_query = sa.or_(
        *[geography_models.Address.departmentCode.startswith(code) for code in postal_codes_prefixes]
    )
    return _find_today_event_stock_ids_filter_by_departments(today_min, today_max, departments_query)


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

    query = (
        base_query.join(offers_models.Offer)
        .join(offerers_models.OffererAddress)
        .join(geography_models.Address)
        .filter(departments_filter)
        .with_entities(models.Stock.id)
    )

    # add stocks with a virtual Venue with an address in the departement filter to the query
    query = query.union(
        base_query.join(offerers_models.Venue)
        .filter(offerers_models.Venue.isVirtual == True)
        .with_entities(models.Stock.id)
    )

    return {stock.id for stock in query}


def delete_future_offer(offer_id: int) -> None:
    db.session.query(models.FutureOffer).filter_by(offerId=offer_id).delete()


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


def get_offer_reaction_count_subquery() -> sa.sql.selectable.ScalarSelect:
    return (
        sa.select(sa.func.count(reactions_models.Reaction.id))
        .select_from(reactions_models.Reaction)
        .where(reactions_models.Reaction.offerId == models.Offer.id)
        .where(reactions_models.Reaction.reactionType == reactions_models.ReactionTypeEnum.LIKE)
        .correlate(models.Offer)
        .scalar_subquery()
    )


def get_current_headline_offer(offerer_id: int) -> models.HeadlineOffer | None:
    return (
        db.session.query(models.HeadlineOffer)
        .join(
            offerers_models.Venue,
            models.HeadlineOffer.venueId == offerers_models.Venue.id,
        )
        .join(
            offerers_models.Offerer,
            offerers_models.Venue.managingOffererId == offerers_models.Offerer.id,
        )
        .filter(
            offerers_models.Offerer.id == offerer_id,
            models.HeadlineOffer.timespan.contains(datetime.datetime.utcnow()),
        )
        .one_or_none()
    )


def get_inactive_headline_offers() -> list[models.HeadlineOffer]:
    return (
        db.session.query(models.HeadlineOffer)
        .join(models.Offer, models.HeadlineOffer.offerId == models.Offer.id)
        .outerjoin(models.Mediation, models.Mediation.offerId == models.Offer.id)
        .outerjoin(models.Product, models.Offer.productId == models.Product.id)
        .outerjoin(
            models.ProductMediation,
            models.ProductMediation.productId == models.Product.id,
        )
        .filter(
            sa.or_(
                models.Offer.status != offer_mixin.OfferStatus.ACTIVE,
                sa.and_(  # type: ignore
                    models.ProductMediation.id.is_(None),
                    models.Mediation.id.is_(None),
                ),
            ),
            sa.or_(
                # We don't want to fetch HeadlineOffers that have already been marked as finished
                sa.func.upper(models.HeadlineOffer.timespan) > datetime.datetime.utcnow(),
                sa.func.upper(models.HeadlineOffer.timespan).is_(None),
            ),
        )
        .all()
    )


def get_product_reaction_count_subquery() -> sa.sql.selectable.ScalarSelect:
    return (
        sa.select(sa.func.count(reactions_models.Reaction.id))
        .select_from(reactions_models.Reaction)
        .where(reactions_models.Reaction.productId == models.Product.id)
        .where(reactions_models.Reaction.reactionType == reactions_models.ReactionTypeEnum.LIKE)
        .correlate(models.Product)
        .scalar_subquery()
    )


def get_active_offer_by_venue_id_and_ean(venue_id: int, ean: str) -> models.Offer:
    """Search (active) offer by venue and EAN.

    Notes:
        a venue might have more than one offer sharing the same EAN.
        It should not happen but it can. If so, the error should be
        logged and the most recent one should be returned.
    """
    offers = (
        db.session.query(models.Offer)
        .filter(
            models.Offer.venueId == venue_id,
            models.Offer.isActive.is_(True),
            models.Offer.ean == ean,
        )
        .order_by(models.Offer.dateCreated.desc())
        .all()
    )

    if not offers:
        raise exceptions.OfferNotFound()

    if len(offers) > 1:
        logger.warning(
            "EAN shared by more than one offer across a venue",
            extra={
                "ean": ean,
                "venue_id": venue_id,
                "offers_ids": [offer.id for offer in offers],
            },
        )

    return offers[0]


def get_offer_by_id(offer_id: int, load_options: OFFER_LOAD_OPTIONS = ()) -> models.Offer:
    try:
        query = db.session.query(models.Offer).filter(models.Offer.id == offer_id)
        if "stock" in load_options:
            query = query.outerjoin(
                models.Stock,
                sa.and_(
                    models.Stock.offerId == offer_id,
                    sa.not_(models.Stock.isSoftDeleted),
                ),
            ).options(sa_orm.contains_eager(models.Offer.stocks))
        if "mediations" in load_options:
            query = query.options(sa_orm.joinedload(models.Offer.mediations))
        if "product" in load_options:
            query = query.options(sa_orm.joinedload(models.Offer.product).joinedload(models.Product.productMediations))
        if "headline_offer" in load_options:
            query = query.options(sa_orm.joinedload(models.Offer.headlineOffers))
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
        if "is_non_free_offer" in load_options:
            query = query.options(
                sa_orm.with_expression(models.Offer.isNonFreeOffer, is_non_free_offer_subquery(offer_id))
            )

        if "offerer_address" in load_options:
            query = query.options(
                sa_orm.joinedload(models.Offer.offererAddress).joinedload(offerers_models.OffererAddress.address),
                sa_orm.joinedload(models.Offer.offererAddress).with_expression(
                    offerers_models.OffererAddress._isLinkedToVenue,
                    offerers_models.OffererAddress.isLinkedToVenue.expression,  # type: ignore [attr-defined]
                ),
                sa_orm.joinedload(models.Offer.venue)
                .joinedload(offerers_models.Venue.offererAddress)
                .joinedload(offerers_models.OffererAddress.address),
                sa_orm.joinedload(models.Offer.venue)
                .joinedload(offerers_models.Venue.offererAddress)
                .with_expression(
                    offerers_models.OffererAddress._isLinkedToVenue,
                    offerers_models.OffererAddress.isLinkedToVenue.expression,  # type: ignore [attr-defined]
                ),
            )
        if "future_offer" in load_options:
            query = query.outerjoin(models.Offer.futureOffer).options(sa_orm.contains_eager(models.Offer.futureOffer))
        if "pending_bookings" in load_options:
            query = query.options(
                sa_orm.with_expression(
                    models.Offer.hasPendingBookings,
                    get_pending_bookings_subquery(offer_id),
                )
            )
        if "event_opening_hours" in load_options:
            query = query.outerjoin(
                models.EventOpeningHours,
                and_(
                    models.EventOpeningHours.offerId == models.Offer.id,
                    models.EventOpeningHours.isSoftDeleted.is_(False),
                ),
            ).options(
                sa_orm.contains_eager(models.Offer.eventOpeningHours),
                sa_orm.joinedload(models.Offer.eventOpeningHours).joinedload(
                    models.EventOpeningHours.weekDayOpeningHours
                ),
            )

        return query.one()
    except sa_orm.exc.NoResultFound:
        raise exceptions.OfferNotFound()


def get_offer_and_extradata(offer_id: int) -> models.Offer | None:
    return (
        db.session.query(models.Offer)
        .filter(models.Offer.id == offer_id)
        .outerjoin(
            models.Stock,
            sa.and_(models.Stock.offerId == offer_id, sa.not_(models.Stock.isSoftDeleted)),
        )
        .options(sa_orm.contains_eager(models.Offer.stocks))
        .options(sa_orm.joinedload(models.Offer.mediations))
        .options(sa_orm.joinedload(models.Offer.priceCategories).joinedload(models.PriceCategory.priceCategoryLabel))
        .options(sa_orm.with_expression(models.Offer.isNonFreeOffer, is_non_free_offer_subquery(offer_id)))
        .options(sa_orm.with_expression(models.Offer.bookingsCount, get_bookings_count_subquery(offer_id)))
        .options(
            sa_orm.joinedload(models.Offer.offererAddress)
            .load_only(
                offerers_models.OffererAddress.id,
                offerers_models.OffererAddress.label,
                offerers_models.OffererAddress.addressId,
            )
            .joinedload(offerers_models.OffererAddress.address),
        )
        .options(sa_orm.joinedload(models.Offer.venue))
        .options(
            sa_orm.joinedload(models.Offer.eventOpeningHours),
            sa_orm.joinedload(models.Offer.eventOpeningHours).joinedload(models.EventOpeningHours.weekDayOpeningHours),
        )
        .one_or_none()
    )


def offer_has_stocks(offer_id: int) -> bool:
    return db.session.query(
        db.session.query(models.Stock)
        .filter(models.Stock.offerId == offer_id, sa.not_(models.Stock.isSoftDeleted))
        .exists()
    ).scalar()


def offer_has_bookable_stocks(offer_id: int) -> bool:
    return db.session.query(
        db.session.query(models.Stock).filter(models.Stock.offerId == offer_id, models.Stock._bookable).exists()
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
    *,
    offer: offers_models.Offer,
    venue: offerers_models.Venue,
    date: datetime.date | None = None,
    time: datetime.time | None = None,
    price_category_id: int | None = None,
    order_by: StocksOrderedBy = StocksOrderedBy.BEGINNING_DATETIME,
    order_by_desc: bool = False,
) -> BaseQuery:
    query = (
        db.session.query(models.Stock)
        .join(models.Offer)
        .join(offerers_models.Venue)
        .filter(
            models.Stock.offerId == offer.id,
            models.Stock.isSoftDeleted == False,
        )
    )
    if price_category_id is not None:
        query = query.filter(models.Stock.priceCategoryId == price_category_id)
    if date is not None:
        query = query.filter(sa.cast(models.Stock.beginningDatetime, sa.Date) == date)
    if time is not None:
        dt = datetime.datetime.combine(datetime.datetime.today(), time)
        timezone = pytz.timezone(venue.timezone)

        if offer.offererAddress:
            timezone = pytz.timezone(offer.offererAddress.address.timezone)
        elif venue.offererAddress:
            timezone = pytz.timezone(venue.offererAddress.address.timezone)

        address_time = dt.replace(tzinfo=pytz.utc).astimezone(timezone).time()

        query = query.filter(
            sa.cast(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                ),
                sa.Time,
            )
            >= address_time.replace(second=0),
            sa.cast(
                sa.func.timezone(
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                ),
                sa.Time,
            )
            <= address_time.replace(second=59),
        )
    return _order_stocks_by(query, order_by, order_by_desc)


def hard_delete_filtered_stocks(
    offer: offers_models.Offer,
    venue: offerers_models.Venue,
    date: datetime.date | None = None,
    time: datetime.time | None = None,
    price_category_id: int | None = None,
) -> None:
    subquery = get_filtered_stocks(
        offer=offer,
        venue=venue,
        date=date,
        time=time,
        price_category_id=price_category_id,
    )
    subquery = subquery.with_entities(models.Stock.id)
    db.session.query(models.Stock).filter(models.Stock.id.in_(subquery)).delete(synchronize_session=False)
    db.session.flush()


def get_paginated_stocks(
    stocks_query: BaseQuery,
    stocks_limit_per_page: int = LIMIT_STOCKS_PER_PAGE,
    page: int = 1,
) -> BaseQuery:
    return stocks_query.offset((page - 1) * stocks_limit_per_page).limit(stocks_limit_per_page)


def get_synchronized_offers_with_provider_for_venue(venue_id: int, provider_id: int) -> BaseQuery:
    return (
        db.session.query(models.Offer)
        .filter(models.Offer.venueId == venue_id)
        .filter(models.Offer.lastProviderId == provider_id)
    )


def update_stock_quantity_to_dn_booked_quantity(stock_id: int | None) -> None:
    if not stock_id:
        return
    db.session.query(models.Stock).filter(models.Stock.id == stock_id).update(
        {"quantity": models.Stock.dnBookedQuantity}
    )
    db.session.flush()


def get_paginated_active_offer_ids(batch_size: int, page: int = 1) -> list[int]:
    query = (
        db.session.query(models.Offer)
        .with_entities(models.Offer.id)
        .filter(models.Offer.isActive.is_(True))
        .order_by(models.Offer.id)
        .offset((page - 1) * batch_size)  # first page is 1, not 0
        .limit(batch_size)
    )
    return [offer_id for (offer_id,) in query]


def get_paginated_offer_ids_by_venue_id(venue_id: int, limit: int, page: int = 0) -> list[int]:
    query = (
        db.session.query(models.Offer)
        .with_entities(models.Offer.id)
        .filter(models.Offer.venueId == venue_id)
        .order_by(models.Offer.id)
        .offset(page * limit)  # first page is 0
        .limit(limit)
    )
    return [offer_id for (offer_id,) in query]


def get_offer_price_categories(offer_id: int, id_at_provider_list: list[str] | None = None) -> BaseQuery:
    """Return price categories for given offer, with the possibility to filter on `idAtProvider`"""
    query = db.session.query(models.PriceCategory).filter(
        models.PriceCategory.offerId == offer_id,
    )

    if id_at_provider_list is not None:
        query = query.filter(models.PriceCategory.idAtProvider.in_(id_at_provider_list))

    return query


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


def has_active_offer_with_ean(ean: str | None, venue: offerers_models.Venue, offer_id: int | None) -> bool:
    if not ean:
        # We should never be there (an ean or an ean must be given), in case we are alert sentry.
        logger.error("Could not search for an offer without ean")
    base_query = db.session.query(models.Offer).filter(
        models.Offer.venue == venue,
        models.Offer.isActive.is_(True),
        models.Offer.ean == ean,
    )

    if offer_id is not None:
        base_query = base_query.filter(models.Offer.id != offer_id)

    return db.session.query(base_query.exists()).scalar()


def get_movie_product_by_allocine_id(allocine_id: str) -> models.Product | None:
    return db.session.query(models.Product).filter(models.Product.extraData["allocineId"] == allocine_id).one_or_none()


def get_movie_product_by_visa(visa: str) -> models.Product | None:
    return db.session.query(models.Product).filter(models.Product.extraData["visa"].astext == visa).one_or_none()


def _log_deletion_error(_to_keep: models.Product, to_delete: models.Product) -> None:
    logger.info("Failed to delete product %d", to_delete.id)


@retry(
    exception=sa_exc.IntegrityError,
    exception_handler=_log_deletion_error,
    logger=logger,
    max_attempts=3,
)
def merge_products(to_keep: models.Product, to_delete: models.Product) -> models.Product:
    # It has already happened that an offer is created by another SQL session
    # in between the transfer of the offers and the product deletion.
    # This causes the product deletion to fail with an IntegrityError
    # `update or delete on table "product" violates foreign key constraint "offer_productId_fkey" on table "offer"`
    # To fix this race condition requires to force taking an Access Exclusive lock on the product to delete.
    # Because this situation is rare, we use a `retry` instead. That should be sufficient.

    db.session.query(models.Offer).filter(models.Offer.productId == to_delete.id).update({"productId": to_keep.id})
    db.session.query(reactions_models.Reaction).filter(reactions_models.Reaction.productId == to_delete.id).update(
        {"productId": to_keep.id}
    )
    db.session.delete(to_delete)
    db.session.flush()

    return to_keep


def venues_have_individual_and_collective_offers(
    venue_ids: list[int],
) -> tuple[bool, bool]:
    return (
        db.session.query(
            db.session.query(offers_models.Offer).filter(offers_models.Offer.venueId.in_(venue_ids)).exists()
        ).scalar(),
        db.session.query(
            db.session.query(educational_models.CollectiveOffer)
            .filter(educational_models.CollectiveOffer.venueId.in_(venue_ids))
            .exists()
        ).scalar(),
    )


def get_offer_existing_stocks_count(offer_id: int) -> int:
    return (
        db.session.query(models.Stock).filter_by(offerId=offer_id).filter(models.Stock.isSoftDeleted == False).count()
    )


def offer_has_timestamped_stocks(offer_id: int) -> bool:
    return db.session.query(
        db.session.query(models.Stock)
        .filter(
            models.Stock.isSoftDeleted == False,
            models.Stock.offerId == offer_id,
            models.Stock.beginningDatetime != None,
        )
        .exists()
    ).scalar()


def get_unbookable_unbooked_old_offer_ids(
    min_id: int = 0, max_id: int | None = None, batch_size: int = 10_000
) -> typing.Generator[int, None, None]:
    """Find unbookable unbooked old offer ids.

    * An unbookable offer is an offer without any stock OR with only soft
    deleted stocks OR whose stocks have all passed their booking limit date.
    * An unbooked offer is an offer without any known booking (not event
    cancelled).
    * An old offer is an offer that has been created more than a year ago.
    """
    query = """
        SELECT
            offer.id
        FROM
            offer
        WHERE
            offer.id >= :min_id
            AND offer.id < :max_id
            AND offer."dateUpdated" < now() - interval '1 year'
            -- offers without any bookable stock (either no stocks
            -- at all, or no one with a quantity > 0)
            AND offer.id NOT IN (
                SELECT
                    distinct(stock."offerId")
                FROM
                    stock
                WHERE
                    stock."offerId" >= :min_id
                    AND stock."offerId" < :max_id
                    AND stock."isSoftDeleted" IS NOT TRUE
                    AND stock.quantity > 0
                    AND (
                        stock."bookingLimitDatetime" IS NULL
                        OR stock."bookingLimitDatetime" > now()
                    )
            )
            -- offers without any linked booking
            -- (event cancelled ones)
            AND offer.id NOT IN (
                SELECT
                    distinct(stock."offerId")
                FROM
                    stock
                LEFT JOIN
                    booking on booking."stockId" = stock.id
                WHERE
                    stock."offerId" >= :min_id
                    AND stock."offerId" < :max_id
                    AND booking.id IS NOT NULL
            )
    """

    if max_id is None:
        max_id = models.Offer.query.order_by(models.Offer.id.desc()).first().id

    while min_id < max_id:
        rows = db.session.execute(sa.text(query), {"min_id": min_id, "max_id": min_id + batch_size})
        yield from {row[0] for row in rows}
        min_id += batch_size
