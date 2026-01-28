import datetime
import enum
import logging
import operator
import typing

import psycopg2
import pytz
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.functions import ST_Distance
from geoalchemy2.functions import ST_MakePoint

from pcapi.core.artist import models as artist_models
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.educational import models as educational_models
from pcapi.core.geography import models as geography_models
from pcapi.core.highlights import models as highlights_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers import models as providers_models
from pcapi.core.reactions import models as reactions_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import custom_keys
from pcapi.utils import date as date_utils
from pcapi.utils import string as string_utils
from pcapi.utils.decorators import retry

from . import exceptions
from . import models
from . import utils


logger = logging.getLogger(__name__)


IMPORTED_CREATION_MODE = "imported"
MANUAL_CREATION_MODE = "manual"

LIMIT_STOCKS_PER_PAGE = 20
STOCK_LIMIT_TO_DELETE = 50

OFFER_LOAD_OPTIONS = typing.Iterable[
    typing.Literal[
        "bookings_count",
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
        "meta_data",
        "openingHours",
        "highlight_requests",
        "artists",
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
                models.Offer.subcategoryId,
                models.Offer.validation,
                models.Offer.ean,
                models.Offer._extraData,
                models.Offer.lastProviderId,
                models.Offer.offererAddressId,
                models.Offer.productId,
                models.Offer.url,
                models.Offer.publicationDatetime,
                models.Offer.bookingAllowedDatetime,
            ).joinedload(models.Offer.headlineOffers)
        )
        .options(
            sa_orm.selectinload(models.Offer.highlight_requests).joinedload(
                highlights_models.HighlightRequest.highlight
            )
        )
        .options(
            sa_orm.joinedload(models.Offer.venue).options(
                sa_orm.load_only(
                    offerers_models.Venue.id,
                    offerers_models.Venue.name,
                    offerers_models.Venue.publicName,
                    offerers_models.Venue.isVirtual,
                ),
                sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(
                    offerers_models.Offerer.id, offerers_models.Offerer.name
                ),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            )
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
                models.Mediation.thumbCount,
                models.Mediation.isActive,
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
        .options(sa_orm.joinedload(models.Offer.offererAddress).joinedload(offerers_models.OffererAddress.address))
        .limit(offers_limit)
        .all()
    )

    # Do not use `ORDER BY` in SQL, which sometimes applies on a very large result set
    # _before_ the `LIMIT` clause (and kills performance).
    if len(offers) < offers_limit:
        offers = sorted(offers, key=operator.attrgetter("id"), reverse=True)

    return offers


def get_offers_by_date_field_range(
    date_field: str, lower_bound: datetime.datetime, upper_bound: datetime.datetime
) -> sa_orm.Query:
    column = getattr(models.Offer, date_field)
    return db.session.query(models.Offer).filter(
        column != None,
        column >= lower_bound,
        column <= upper_bound,
    )


def get_offers_by_publication_datetime(start: datetime.datetime, end: datetime.datetime) -> sa_orm.Query:
    return get_offers_by_date_field_range("publicationDatetime", start, end)


def get_offers_by_booking_allowed_datetime(booking_allowed_datetime: datetime.datetime | None = None) -> sa_orm.Query:
    if booking_allowed_datetime is None:
        booking_allowed_datetime = datetime.datetime.now(datetime.timezone.utc)

    # The lower bound is intentionally very far in the past.
    # This function should be called every quarter hour, but filtering the last days allows auto-correction
    # when the function fails (timeout, or lock denied, most of the time)
    upper_bound = booking_allowed_datetime
    lower_bound = upper_bound - datetime.timedelta(hours=24)

    return get_offers_by_date_field_range("bookingAllowedDatetime", lower_bound, upper_bound)


def get_offers_by_ids(user: users_models.User, offer_ids: list[int]) -> sa_orm.Query:
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


def get_offers_details(offer_ids: list[int]) -> sa_orm.Query:
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
                models.Offer.publicationDatetime,
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
                offerers_models.Venue.isSoftDeleted,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isPermanent,
                offerers_models.Venue.isOpenToPublic,
                offerers_models.Venue._bannerUrl,
                offerers_models.Venue.venueTypeCode,
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
        .options(sa_orm.with_expression(models.Offer.chroniclesCount, get_offer_chronicles_count_subquery()))
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
                models.Product.chroniclesCount,
                models.Product.likesCount,
            )
            .joinedload(models.Product.productMediations)
        )
        .options(sa_orm.joinedload(models.Offer.metaData))
        .options(
            sa_orm.joinedload(models.Offer.product)
            .selectinload(models.Product.artistLinks)
            .joinedload(artist_models.ArtistProductLink.artist)
        )
        .options(sa_orm.joinedload(models.Offer.headlineOffers))
        .outerjoin(models.Offer.lastProvider)
        .options(sa_orm.contains_eager(models.Offer.lastProvider).load_only(providers_models.Provider.localClass))
        .filter(
            models.Offer.id.in_(offer_ids),
            models.Offer.validation == models.OfferValidationStatus.APPROVED,
        )
        .options(sa_orm.selectinload(models.Offer.openingHours))
    )


def get_nearby_bookable_screenings_from_product(
    product: models.Product,
    latitude: float,
    longitude: float,
    around_radius: int,
    from_datetime: datetime.datetime,
    to_datetime: datetime.datetime,
) -> list[dict[str, typing.Any]]:
    request_location = sa.cast(
        ST_MakePoint(longitude, latitude), Geography(None)
    )  # `None` is used not to have to specify SRID
    offer_location = sa.cast(
        ST_MakePoint(
            sa.cast(geography_models.Address.longitude, sa.DOUBLE_PRECISION),
            sa.cast(geography_models.Address.latitude, sa.DOUBLE_PRECISION),
        ),
        Geography(None),
    )

    # In the _where_ clause, in `ST_DWithin` filter, `False` is the value for parameter `use_spheroid`,
    # see the doc here: https://postgis.net/docs/ST_DWithin.html.
    # It cannot be a keyword argument since kwargs, except special ones, are not taken into account by `ST_DWithin`.
    stock_ids = db.session.scalars(
        sa.select(models.Stock.id)
        .select_from(geography_models.Address)
        .join(offerers_models.OffererAddress)
        .join(models.Offer)
        .join(models.Stock)
        .where(
            ST_DWithin(offer_location, request_location, around_radius, False),
            models.Offer.productId == product.id,
            models.Offer.is_eligible_for_search.is_(True),
            models.Stock.beginningDatetime >= from_datetime,
            models.Stock.beginningDatetime < to_datetime,
        )
    )

    result_objects_query = (
        sa.select(
            ST_Distance(offer_location, request_location).label("distance"),
            models.Stock.id.label("stock_id"),
            models.Stock.beginningDatetime.label("beginning_datetime"),
            models.Stock.features,
            models.Stock.price,
            geography_models.Address.city,
            geography_models.Address.postalCode.label("postal_code"),
            geography_models.Address.street.label("street"),
            sa.func.coalesce(offerers_models.OffererAddress.label, offerers_models.Venue.publicName).label("label"),
            offerers_models.Venue.id.label("venue_id"),
            offerers_models.Venue.bannerUrl.label("thumb_url"),
        )
        .select_from(models.Stock)
        .join(models.Offer)
        .join(offerers_models.Venue)
        .join(offerers_models.OffererAddress, models.Offer.offererAddressId == offerers_models.OffererAddress.id)
        .join(geography_models.Address)
        .where(models.Stock.id.in_(stock_ids))
        .order_by("distance")
    )

    result = db.session.execute(result_objects_query).mappings()
    return [dict(**row) for row in result]


def get_bookable_screenings_from_venue(
    venue_id: int,
    from_datetime: datetime.datetime,
    to_datetime: datetime.datetime,
) -> list[models.Offer]:
    offers = (
        db.session.scalars(
            sa.select(models.Offer)
            .join(models.Stock)
            .options(sa_orm.load_only(models.Offer.id, models.Offer.name))
            .options(
                sa_orm.contains_eager(models.Offer.stocks).load_only(
                    models.Stock.beginningDatetime,
                    models.Stock.price,
                    models.Stock.features,
                )
            )
            .options(
                sa_orm.joinedload(models.Offer.mediations).load_only(
                    models.Mediation.isActive,
                    models.Mediation.dateCreated,
                    models.Mediation.thumbCount,
                )
            )
            .options(
                sa_orm.joinedload(models.Offer.product)
                .load_only(
                    models.Product.durationMinutes,
                    models.Product.extraData,
                    models.Product.last_30_days_booking,
                    models.Product.name,
                    models.Product.thumbCount,
                )
                .joinedload(models.Product.productMediations)
                .load_only(models.ProductMediation.imageType, models.ProductMediation.uuid)
            )
            .where(
                models.Offer.venueId == venue_id,
                models.Offer.subcategoryId == subcategories.SEANCE_CINE.id,
                models.Offer.is_eligible_for_search.is_(True),
                models.Stock.beginningDatetime >= from_datetime,
                models.Stock.beginningDatetime < to_datetime,
            )
        )
        .unique()
        .all()
    )
    return list(offers)


def get_offers_by_filters(
    *,
    user_id: int,
    offerer_id: int | None = None,
    status: str | None = None,
    venue_id: int | None = None,
    category_id: str | None = None,
    offerer_address_id: int | None = None,
    name_keywords_or_ean: str | None = None,
    creation_mode: str | None = None,
    period_beginning_date: datetime.date | None = None,
    period_ending_date: datetime.date | None = None,
) -> sa_orm.Query:
    query = (
        db.session.query(models.Offer)
        .join(models.Offer.venue)
        .join(offerers_models.Venue.managingOfferer)
        .join(offerers_models.Offerer.UserOfferers)
        .filter(
            offerers_models.UserOfferer.userId == user_id,
            offerers_models.UserOfferer.isValidated,
        )
    )
    if offerer_id is not None:
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
        venue_oa_alias = sa_orm.aliased(offerers_models.OffererAddress)
        venue_address_alias = sa_orm.aliased(geography_models.Address)
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
            .join(venue_oa_alias.venue)
            .filter(venue_oa_alias.type == offerers_models.LocationType.VENUE_LOCATION)
            .join(venue_address_alias, venue_address_alias.id == venue_oa_alias.addressId)
            .filter(models.Stock.isSoftDeleted.is_(False))
            .filter(models.Stock.offerId == models.Offer.id)
        )
        target_timezone = sa.func.coalesce(geography_models.Address.timezone, venue_address_alias.timezone)
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


def _filter_by_creation_mode(query: sa_orm.Query, creation_mode: str) -> sa_orm.Query:
    if creation_mode == MANUAL_CREATION_MODE:
        query = query.filter(models.Offer.lastProviderId.is_(None))
    if creation_mode == IMPORTED_CREATION_MODE:
        query = query.filter(models.Offer.lastProviderId.is_not(None))

    return query


def _filter_by_status(query: sa_orm.Query, status: str) -> sa_orm.Query:
    return query.filter(models.Offer.status == offer_mixin.OfferStatus[status].name)


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
            models.Offer.venueId == venue.id,
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
        .options(sa_orm.load_only(models.Stock.id))
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


def find_event_stocks_happening_in_x_days(number_of_days: int) -> sa_orm.Query:
    target_day = date_utils.get_naive_utc_now() + datetime.timedelta(days=number_of_days)
    start = datetime.datetime.combine(target_day, datetime.time.min)
    end = datetime.datetime.combine(target_day, datetime.time.max)

    return find_event_stocks_day(start, end)


def find_event_stocks_day(start: datetime.datetime, end: datetime.datetime) -> sa_orm.Query:
    return (
        db.session.query(models.Stock)
        .filter(models.Stock.beginningDatetime.between(start, end))
        .join(bookings_models.Booking)
        .filter(bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED)
        .distinct()
    )


def get_expired_offer_ids(
    start_time: datetime.datetime, end_time: datetime.datetime, offset: int | None = None, limit: int | None = None
) -> typing.Sequence[int]:
    """Return ids of offers whose latest booking limit occurs within
    the interval [`start_time`, `end_time`].

    Inactive offers are ignored.
    """
    exists_future_stock = (
        sa.select(models.Stock.id)
        .where(
            models.Stock.offerId == models.Offer.id,
            models.Stock.bookingLimitDatetime > end_time,
            models.Stock.isSoftDeleted.is_(False),
        )
        .exists()
        .correlate(models.Offer)
    )
    query = (
        sa.select(models.Offer.id.distinct())
        .select_from(models.Offer)
        .join(models.Offer.stocks)
        .where(
            models.Offer.isActive.is_(True),
            models.Stock.isSoftDeleted.is_(False),
            models.Stock.bookingLimitDatetime.is_not(None),
            models.Stock.bookingLimitDatetime.between(start_time, end_time),
            sa.not_(exists_future_stock),
        )
        .order_by(models.Offer.id)
    )
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    return db.session.execute(query).scalars().all()


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
        base_query.join(models.Offer)
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


def get_available_activation_code(stock: models.Stock) -> models.ActivationCode | None:
    activable_code = next(
        (
            code
            for code in stock.activationCodes
            if code.bookingId is None
            and (code.expirationDate is None or code.expirationDate > date_utils.get_naive_utc_now())
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


def get_offer_chronicles_count_subquery() -> sa.sql.selectable.ScalarSelect:
    return (
        sa.select(sa.func.count())
        .select_from(chronicles_models.OfferChronicle)
        .join(
            chronicles_models.Chronicle, chronicles_models.Chronicle.id == chronicles_models.OfferChronicle.chronicleId
        )
        .where(
            chronicles_models.OfferChronicle.offerId == models.Offer.id,
            chronicles_models.Chronicle.isPublished.is_(True),
        )
        .correlate(models.Offer)
        .scalar_subquery()
    )


def get_offer_reaction_count_subquery() -> sa.sql.selectable.ScalarSelect:
    return (
        sa.select(sa.func.count())
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
            models.HeadlineOffer.timespan.contains(date_utils.get_naive_utc_now()),
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
                models.Offer.status != offer_mixin.OfferStatus.ACTIVE.name,
                sa.and_(
                    models.ProductMediation.id.is_(None),
                    models.Mediation.id.is_(None),
                ),
            ),
            sa.or_(
                # We don't want to fetch HeadlineOffers that have already been marked as finished
                sa.func.upper(models.HeadlineOffer.timespan) > date_utils.get_naive_utc_now(),
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
            models.Offer.isActive,
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
        if "meta_data" in load_options:
            query = query.options(sa_orm.joinedload(models.Offer.metaData))
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
                sa_orm.defaultload(models.Offer.venue)
                .joinedload(offerers_models.Venue.offererAddress)
                .joinedload(offerers_models.OffererAddress.address),
            )
        if "pending_bookings" in load_options:
            query = query.options(
                sa_orm.with_expression(
                    models.Offer.hasPendingBookings,
                    get_pending_bookings_subquery(offer_id),
                )
            )
        if "openingHours" in load_options:
            query = query.options(sa_orm.joinedload(models.Offer.openingHours))
        if "highlight_requests" in load_options:
            query = query.options(
                sa_orm.joinedload(models.Offer.highlight_requests).joinedload(
                    highlights_models.HighlightRequest.highlight
                ),
            )
        if "artists" in load_options:
            query = query.options(
                sa_orm.selectinload(models.Offer.artistOfferLinks)
                .joinedload(artist_models.ArtistOfferLink.artist)
                .load_only(
                    artist_models.Artist.id,
                    artist_models.Artist.name,
                )
            )
        return query.one()
    except sa_orm.exc.NoResultFound:
        raise exceptions.OfferNotFound(offer_id=offer_id)


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
        .options(
            sa_orm.joinedload(models.Offer.highlight_requests).joinedload(highlights_models.HighlightRequest.highlight)
        )
        .options(sa_orm.joinedload(models.Offer.venue))
        .options(sa_orm.joinedload(models.Offer.metaData))
        .options(
            sa_orm.selectinload(models.Offer.artistOfferLinks)
            .joinedload(artist_models.ArtistOfferLink.artist)
            .load_only(
                artist_models.Artist.id,
                artist_models.Artist.name,
            )
        )
        .one_or_none()
    )


def offer_has_bookable_stocks(offer_id: int) -> bool:
    return db.session.query(
        db.session.query(models.Stock).filter(models.Stock.offerId == offer_id, models.Stock._bookable).exists()
    ).scalar()


def _order_stocks_by(query: sa_orm.Query, order_by: StocksOrderedBy, order_by_desc: bool) -> sa_orm.Query:
    column: (
        sa_orm.Mapped[int | None]
        | sa.Cast[datetime.date]
        | sa.Cast[datetime.time]
        | sa_orm.Mapped[datetime.datetime | None]
    )
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
    offer: models.Offer,
    venue: offerers_models.Venue,
    date: datetime.date | None = None,
    time: datetime.time | None = None,
    price_category_id: int | None = None,
    order_by: StocksOrderedBy = StocksOrderedBy.BEGINNING_DATETIME,
    order_by_desc: bool = False,
) -> sa_orm.Query:
    query = (
        db.session.query(models.Stock)
        .join(models.Offer)
        .join(offerers_models.Venue)
        .outerjoin(offerers_models.Venue.offererAddress)
        .outerjoin(offerers_models.OffererAddress.address)
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

        if offer.offererAddress:
            timezone = pytz.timezone(offer.offererAddress.address.timezone)
        else:
            timezone = pytz.timezone(venue.offererAddress.address.timezone)

        address_time = dt.replace(tzinfo=pytz.utc).astimezone(timezone).time()

        query = query.filter(
            sa.cast(
                sa.func.timezone(
                    geography_models.Address.timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                ),
                sa.Time,
            )
            >= address_time.replace(second=0),
            sa.cast(
                sa.func.timezone(
                    geography_models.Address.timezone,
                    sa.func.timezone("UTC", models.Stock.beginningDatetime),
                ),
                sa.Time,
            )
            <= address_time.replace(second=59),
        )
    return _order_stocks_by(query, order_by, order_by_desc)


def hard_delete_filtered_stocks(
    offer: models.Offer,
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
    stocks_query: sa_orm.Query,
    stocks_limit_per_page: int = LIMIT_STOCKS_PER_PAGE,
    page: int = 1,
) -> sa_orm.Query:
    return stocks_query.offset((page - 1) * stocks_limit_per_page).limit(stocks_limit_per_page)


def get_synchronized_offers_with_provider_for_venue(venue_id: int, provider_id: int) -> sa_orm.Query:
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
        .filter(models.Offer.isActive)
        .order_by(models.Offer.id)
        .offset((page - 1) * batch_size)  # first page is 1, not 0
        .limit(batch_size)
    )
    return [offer_id for (offer_id,) in query]


def get_paginated_offer_ids_by_artist_id(artist_id: str, chunk_size: int) -> typing.Iterator[list[int]]:
    query = (
        db.session.query(models.Offer.id)
        .join(artist_models.ArtistProductLink, models.Offer.productId == artist_models.ArtistProductLink.product_id)
        .filter(artist_models.ArtistProductLink.artist_id == artist_id)
    )
    yield from utils.yield_field_batch_from_query(query, chunk_size)


def get_paginated_offer_ids_by_venue_id(venue_id: int, chunk_size: int) -> typing.Iterator[list[int]]:
    query = db.session.query(models.Offer.id).filter(models.Offer.venueId == venue_id)
    yield from utils.yield_field_batch_from_query(query, chunk_size)


def get_offer_price_categories(offer_id: int, id_at_provider_list: list[str] | None = None) -> sa_orm.Query:
    """Return price categories for given offer, with the possibility to filter on `idAtProvider`"""
    query = db.session.query(models.PriceCategory).filter(
        models.PriceCategory.offerId == offer_id,
    )

    if id_at_provider_list is not None:
        query = query.filter(models.PriceCategory.idAtProvider.in_(id_at_provider_list))

    return query


def get_venue_price_category_labels(venue_id: int) -> list[models.PriceCategoryLabel]:
    return db.session.query(models.PriceCategoryLabel).filter(models.PriceCategoryLabel.venueId == venue_id).all()


def get_offer_by_venue_and_movie_uuid(venue_id: int, movie_uuid: str) -> models.Offer | None:
    return (
        db.session.query(models.Offer)
        .filter(models.Offer.idAtProvider == movie_uuid, models.Offer.venueId == venue_id)
        .one_or_none()
    )


def get_stock_by_movie_stock_uuid(stock_uuid: str) -> models.Stock | None:
    return db.session.query(models.Stock).filter(models.Stock.idAtProviders == stock_uuid).one_or_none()


def exclude_offers_from_inactive_venue_provider(query: sa_orm.Query) -> sa_orm.Query:
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
    return typing.cast(int, db.session.execute(sequence))


def has_active_offer_with_ean(ean: str | None, venue: offerers_models.Venue, offer_id: int | None) -> bool:
    if not ean:
        # We should never be there (an ean or an ean must be given), in case we are alert sentry.
        logger.error("Could not search for an offer without ean")
    base_query = db.session.query(models.Offer).filter(
        models.Offer.venueId == venue.id,
        models.Offer.isActive,
        models.Offer.ean == ean,
    )

    if offer_id is not None:
        base_query = base_query.filter(models.Offer.id != offer_id)

    return db.session.query(base_query.exists()).scalar()


def get_movie_products_matching_allocine_id_or_film_visa(
    allocine_id: str | None,
    visa: str | None,
) -> list[models.Product]:
    """
    One of the two parameters must be defined.

    As there are unique indexes on `extraData["allocineId"]` and `extraData["visa"]`,
    this function can return at most 2 products.
    """
    filters = []

    if not allocine_id and not visa:
        raise ValueError("`allocine_id` or `visa` must be defined")

    if allocine_id:
        filters.append((models.Product.extraData.op("->")("allocineId") == str(allocine_id)))

    if visa:
        filters.append((models.Product.extraData["visa"].astext == visa))

    return db.session.query(models.Product).filter(sa.or_(*filters)).all()


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
        db.session.query(db.session.query(models.Offer).filter(models.Offer.venueId.in_(venue_ids)).exists()).scalar(),
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


def get_unbookable_unbooked_old_offer_ids(
    min_id: int, max_id: int, batch_size: int = 5_000
) -> typing.Generator[int, None, None]:
    """Find unbookable unbooked old offer ids.

    * An unbookable offer is an offer without any stock OR with only soft
    deleted stocks OR whose stocks have all passed their booking limit date.
    * An unbooked offer is an offer without any known booking (not event
    cancelled).
    * An old offer is an offer that has been created more than a year ago.

    Notes:
        Offer ids are yielded using multiple queries over small intervals. If
        an error occurs, the query is retried a couple times at most. If this
        is not enough or a really unexpected error happens, the batch is
        ignored.
        -> This means rows might be ignored. But it is better than
        stopping everything.
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
            -- at all, or no one with a quantity > 0) and whose
            -- validation status is not REJECTED (rejected offers
            -- cannot be booked).
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
                    ) AND offer.validation != 'REJECTED'
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

    def run_with_retry(query: str, start_id: int, batch_size: int) -> set[int]:  # type: ignore[return]
        for idx in reversed(range(5)):
            try:
                rows = db.session.execute(sa.text(query), {"min_id": start_id, "max_id": start_id + batch_size})
                return {row[0] for row in rows}
            except psycopg2.errors.OperationalError as e:
                error_msg = "Error: %s between rows %s and %s"
                logger.info(error_msg, type(e).__name__, start_id, start_id + batch_size)

                db.session.rollback()

                if idx == 0:
                    raise

    while min_id < max_id:
        try:
            yield from run_with_retry(query, min_id, batch_size)
        except psycopg2.errors.OperationalError as e:
            # duplicate information to simplify some search
            extra = {"min_id": min_id, "max_id": min_id + batch_size, "error": str(e)}
            error_msg = "Too many retries: could not fetch rows between %d and %d: %s"
            logger.error(error_msg, min_id, min_id + batch_size, str(e), extra=extra)
        except Exception as err:
            # duplicate information to simplify some search
            extra = {"min_id": min_id, "max_id": min_id + batch_size, "error": str(err)}
            error_msg = "Failed to fetch rows"
            logger.error(error_msg, min_id, min_id + batch_size, extra=extra)

        min_id += batch_size
