import copy
import datetime
import logging

import sqlalchemy as sqla

from pcapi import repository
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.categories.genres import show
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.offers import tasks as offers_tasks
from pcapi.core.offers import validation as offers_validation
from pcapi.core.offers.schemas import CreateOrUpdateEANOffersRequest
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.constants import TITELIVE_MUSIC_GENRES_BY_GTL_ID
from pcapi.core.providers.constants import TITELIVE_MUSIC_TYPES
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.public import blueprints
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.individual_offers.v1 import serialization
from pcapi.routes.public.individual_offers.v1 import utils as individual_offers_utils
from pcapi.routes.public.services import authorization
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils import image_conversion
from pcapi.utils.custom_keys import get_field
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import provider_api_key_required
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)

ALLOWED_PRODUCT_SUBCATEGORIES = [
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    subcategories.LIVRE_PAPIER.id,
]


@celery_async_task(
    name="tasks.offers.default.create_or_update_ean_offers",
    autoretry_for=(),
    model=CreateOrUpdateEANOffersRequest,
)
def create_or_update_ean_offers_celery(payload: CreateOrUpdateEANOffersRequest) -> None:
    _create_or_update_ean_offers(
        serialized_products_stocks=payload.serialized_products_stocks,
        venue_id=payload.venue_id,
        provider_id=payload.provider_id,
        address_id=payload.address_id,
        address_label=payload.address_label,
    )


@job(worker.low_queue)
def create_or_update_ean_offers_rq(
    *,
    serialized_products_stocks: dict,
    venue_id: int,
    provider_id: int,
    address_id: int | None = None,
    address_label: str | None = None,
) -> None:
    _create_or_update_ean_offers(
        serialized_products_stocks=serialized_products_stocks,
        venue_id=venue_id,
        provider_id=provider_id,
        address_id=address_id,
        address_label=address_label,
    )


def _get_existing_products(ean_to_create: set[str]) -> list[offers_models.Product]:
    return offers_models.Product.query.filter(
        offers_models.Product.ean.in_(ean_to_create),
        offers_models.Product.can_be_synchronized == True,
        offers_models.Product.subcategoryId.in_(ALLOWED_PRODUCT_SUBCATEGORIES),
        # FIXME (cepehang, 2023-09-21) remove these condition when the product table is cleaned up
        offers_models.Product.lastProviderId.is_not(None),
        offers_models.Product.idAtProviders.is_not(None),
    ).all()


def _get_existing_offers(
    ean_to_create_or_update: set[str],
    venue: offerers_models.Venue,
) -> list[offers_models.Offer]:
    subquery = (
        db.session.query(
            sa.func.max(offers_models.Offer.id).label("max_id"),
        )
        .filter(offers_models.Offer.isEvent == False)
        .filter(offers_models.Offer.venue == venue)
        .filter(
            sa.or_(
                # TODO: remove extraData["ean"] when migration is done
                offers_models.Offer.extraData["ean"].astext.in_(ean_to_create_or_update),
                offers_models.Offer.ean.in_(ean_to_create_or_update),
            )
        )
        .group_by(
            # TODO: remove extraData["ean"] when migration is done
            offers_models.Offer.extraData["ean"],
            offers_models.Offer.ean,
            offers_models.Offer.venueId,
        )
        .subquery()
    )

    return (
        utils.retrieve_offer_relations_query(offers_models.Offer.query)
        .join(subquery, offers_models.Offer.id == subquery.c.max_id)
        .all()
    )


def _serialize_products_from_body(
    products: list[serialization.ProductOfferByEanCreation],
) -> dict:
    stock_details = {}
    for product in products:
        stock_details[product.ean] = {
            "quantity": product.stock.quantity,
            "price": product.stock.price,
            "booking_limit_datetime": product.stock.booking_limit_datetime,
        }
    return stock_details


def _create_offer_from_product(
    venue: offerers_models.Venue,
    product: offers_models.Product,
    provider: providers_models.Provider,
    offererAddress: offerers_models.OffererAddress,
) -> offers_models.Offer:
    ean = product.ean

    offer = offers_api.build_new_offer_from_product(
        venue,
        product,
        id_at_provider=ean,
        provider_id=provider.id,
        offerer_address_id=offererAddress.id,
    )

    offer.audioDisabilityCompliant = venue.audioDisabilityCompliant
    offer.mentalDisabilityCompliant = venue.mentalDisabilityCompliant
    offer.motorDisabilityCompliant = venue.motorDisabilityCompliant
    offer.visualDisabilityCompliant = venue.visualDisabilityCompliant

    offer.isActive = True
    offer.lastValidationDate = datetime.datetime.utcnow()
    offer.lastValidationType = OfferValidationType.AUTO
    offer.lastValidationAuthorUserId = None

    logger.info(
        "models.Offer has been created",
        extra={
            "offer_id": offer.id,
            "venue_id": venue.id,
            "product_id": offer.productId,
        },
        technical_message_id="offer.created",
    )

    return offer
