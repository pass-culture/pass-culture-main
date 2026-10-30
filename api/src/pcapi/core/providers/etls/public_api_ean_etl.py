import datetime
import logging
import typing

import sqlalchemy as sa

from pcapi.core.categories import subcategories
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.routes.provider.individual_offers.v1 import utils as individual_offers_v1_utils
from pcapi.utils import date as utils_date
from pcapi.utils import repository


logger = logging.getLogger(__name__)


class _ExtractResult(typing.TypedDict):
    venue: offerers_models.Venue
    provider: providers_models.Provider
    products_by_ean: dict[str, offers_models.Product]
    offerer_addres: offerers_models.OffererAddress
    offers_by_id_at_provider: dict[str, offers_models.Offer]


def _extract(request_payload: offers_schemas.CreateOrUpdateEANOffersRequest) -> _ExtractResult:
    """Extract existing EAN offer data without creating offers, stocks or addresses."""
    provider = db.session.query(providers_models.Provider).filter_by(id=request_payload.provider_id).one()
    venue = db.session.query(offerers_models.Venue).filter_by(id=request_payload.venue_id).one()
    requested_eans = set(request_payload.serialized_products_stocks)

    offers_to_update = _get_existing_offers(requested_eans, venue)
    offer_to_update_by_ean = {}
    ean_list_to_update: set[str] = set()
    ean_list_to_create = requested_eans - ean_list_to_update

    for offer in offers_to_update:
        offer_ean = offer.ean
        assert offer_ean is not None
        ean_list_to_update.add(offer_ean)
        offer_to_update_by_ean[offer_ean] = offer

    offerer_address = None
    products_by_ean = {}
    with repository.transaction():
        if request_payload.address_id:
            offerer_address = offerers_api.get_or_create_offer_location(
                offerer_id=venue.managingOffererId,
                venue_id=venue.id,
                address_id=request_payload.address_id,
                label=request_payload.address_label,
            )
        else:
            offerer_address = offers_api.get_or_create_offerer_address_from_address_body(
                offerers_schemas.LocationOnlyOnVenueModel(),
                venue,
            )

        if ean_list_to_create:
            products = _get_existing_products(ean_list_to_create)
            for product in products:
                assert product.ean is not None
                products_by_ean[product.ean] = product

    return {
        "venue": venue,
        "provider": provider,
        "products_by_ean": products_by_ean,
        "offerer_address": offerer_address,
        "offers_by_id_at_provider": offer_to_update_by_ean,
    }


class _TransformResult(typing.TypedDict):
    offers_to_update: list[offers_models.Offer] = []
    offers_to_create: list[offers_models.Offer] = []


def _transform(
    request_payload: offers_schemas.CreateOrUpdateEANOffersRequest,
    extract_result: _ExtractResult,
) -> _TransformResult:
    offers_to_create: list[offers_models.Offer] = []

    requested_eans = set(request_payload.serialized_products_stocks.keys())
    for requested_ean in requested_eans:
        if requested_ean not in extract_result["products_by_ean"]:
            logger.warning(
                "Product with ean not found",
                extra={
                    "ean": requested_ean,
                    "venue": request_payload.venue_id,
                    "feature": "ean",
                    "action": "not_found",
                },
                technical_message_id="product.not_found",
            )
    for product in extract_result["products_by_ean"].values():
        try:
            assert product.ean  # to make mypy happy
            stock_data = request_payload.serialized_products_stocks[product.ean]
            created_offer = _create_offer_from_product(
                extract_result["venue"],
                product,
                extract_result["provider"],
                offererAddress=extract_result["offerer_address"],
                publicationDatetime=stock_data["publication_datetime"],
                bookingAllowedDatetime=stock_data["booking_allowed_datetime"],
                externalTicketOfficeUrl=str(stock_data["external_ticket_office_url"])
                if stock_data["external_ticket_office_url"]
                else None,
            )
            offers_to_create.append(created_offer)
        except offers_exceptions.OfferException as exc:
            logger.warning(
                "Error while creating offer by ean",
                extra={
                    "ean": product.ean,
                    "venue_id": request_payload.venue_id,
                    "provider_id": request_payload.provider_id,
                    "exc": exc.__class__.__name__,
                },
            )

    return {
        "offers_to_create": offers_to_create,
        "offers_to_update": set(extract_result["offers_by_id_at_provider"].values()),
    }


# Extract helpers

ALLOWED_PRODUCT_SUBCATEGORIES = [
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    subcategories.LIVRE_PAPIER.id,
]


def _get_existing_offers(
    ean_to_create_or_update: set[str],
    venue: offerers_models.Venue,
) -> list[offers_models.Offer]:
    subquery = (
        db.session.query(
            sa.func.max(offers_models.Offer.id).label("max_id"),
        )
        .filter(offers_models.Offer.isEvent == False)
        .filter(offers_models.Offer.venueId == venue.id)
        .filter(offers_models.Offer.ean.in_(ean_to_create_or_update))
        .group_by(
            offers_models.Offer.ean,
            offers_models.Offer.venueId,
        )
        .subquery()
    )

    return (
        individual_offers_v1_utils.retrieve_offer_relations_query(db.session.query(offers_models.Offer))
        .join(subquery, offers_models.Offer.id == subquery.c.max_id)
        .all()
    )


def _get_existing_products(ean_to_create: set[str]) -> list[offers_models.Product]:
    return (
        db.session.query(offers_models.Product)
        .filter(
            offers_models.Product.ean.in_(ean_to_create),
            offers_models.Product.can_be_synchronized == True,
            offers_models.Product.subcategoryId.in_(ALLOWED_PRODUCT_SUBCATEGORIES),
        )
        .all()
    )


def _create_offer_from_product(
    venue: offerers_models.Venue,
    product: offers_models.Product,
    provider: providers_models.Provider,
    offererAddress: offerers_models.OffererAddress,
    publicationDatetime: datetime.datetime | None,
    bookingAllowedDatetime: datetime.datetime | None,
    externalTicketOfficeUrl: str | None,
) -> offers_models.Offer:
    offer = offers_api.build_new_offer_from_product(
        venue,
        product,
        id_at_provider=None,
        provider_id=provider.id,
        offerer_address_id=offererAddress.id,
    )

    offer.audioDisabilityCompliant = venue.audioDisabilityCompliant
    offer.mentalDisabilityCompliant = venue.mentalDisabilityCompliant
    offer.motorDisabilityCompliant = venue.motorDisabilityCompliant
    offer.visualDisabilityCompliant = venue.visualDisabilityCompliant

    offer.publicationDatetime = _ensure_timezone_exists(publicationDatetime)
    offer.bookingAllowedDatetime = _ensure_timezone_exists(bookingAllowedDatetime)
    offer.lastValidationDate = utils_date.get_naive_utc_now()
    offer.lastValidationType = offer_mixin.OfferValidationType.AUTO
    offer.lastValidationAuthorUserId = None
    offer.externalTicketOfficeUrl = externalTicketOfficeUrl

    db.session.add(offer)
    db.session.flush()

    offers_api.finalize_offer(
        offer, publication_datetime=publicationDatetime, booking_allowed_datetime=bookingAllowedDatetime
    )

    logger.info(
        "models.Offer has been created",
        extra={
            "offer_id": offer.id,
            "venue_id": venue.id,
            "product_id": offer.productId,
            "feature": "offer",
            "action": "created",
        },
        technical_message_id="offer.created",
    )

    return offer


def _ensure_timezone_exists(dt: datetime.datetime | None) -> datetime.datetime | None:
    # TODO(jbaudet-pass - 12/2025): this utility can be removed once we
    # can be 100% sure that incoming data used to create products, offers
    # and stocks will always have a timezone.
    # Until then, please keep this function: removing it because it
    # SHOULD be ok might be a little bit risky.
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)
    return dt
