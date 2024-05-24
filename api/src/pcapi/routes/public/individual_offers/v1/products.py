import copy
import datetime
import logging

from flask import request
import sqlalchemy as sqla

from pcapi import repository
from pcapi.core import search
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.categories.categories import TITELIVE_MUSIC_TYPES
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.constants import TITELIVE_MUSIC_GENRES_BY_GTL_ID
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.serialization import venues as venues_serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils import image_conversion
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.workers import worker
from pcapi.workers.decorators import job

from . import blueprint
from . import constants
from . import serialization
from . import utils


logger = logging.getLogger(__name__)


@blueprint.v1_offers_blueprint.route("/offerer_venues", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.OFFERER_VENUES_TAG],
    response_model=venues_serialization.GetOfferersVenuesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (venues_serialization.GetOfferersVenuesResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@api_key_required
def get_offerer_venues(
    query: venues_serialization.GetOfferersVenuesQuery,
) -> venues_serialization.GetOfferersVenuesResponse:
    """
    Get offerer venues

    Return all the venues attached to the API key for given offerer.
    """
    rows = offerers_api.get_providers_offerer_and_venues(current_api_key.provider, query.siren)
    return venues_serialization.GetOfferersVenuesResponse.serialize_offerers_venues(rows)


@blueprint.v1_offers_blueprint.route("/show_types", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.OFFER_ATTRIBUTES],
    response_model=serialization.GetShowTypesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetShowTypesResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@api_key_required
def get_show_types() -> serialization.GetShowTypesResponse:
    """
    Get all the show types
    """
    # Individual offers API only relies on show subtypes, not show types.
    # To make it simpler for the provider using this API, we only expose show subtypes and call them show types.
    return serialization.GetShowTypesResponse(
        __root__=[
            serialization.ShowTypeResponse(id=show_type_slug, label=show_type.label)
            for show_type_slug, show_type in show_types.SHOW_SUB_TYPES_BY_SLUG.items()
        ]
    )


@blueprint.v1_offers_blueprint.route("/music_types", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.OFFER_ATTRIBUTES],
    response_model=serialization.GetMusicTypesResponse,
    deprecated=True,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetMusicTypesResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@api_key_required
def get_music_types() -> serialization.GetMusicTypesResponse:
    """
    [LEGACY] Get music types

    ⚠️ This is a DEPRACTED endpoint. It should not be used.
    """
    # Individual offers API only relies on music subtypes, not music types.
    # To make it simpler for the provider using this API, we only expose music subtypes and call them music types.

    return serialization.GetMusicTypesResponse(
        __root__=[
            serialization.MusicTypeResponse(id=music_type_slug, label=music_type.label)
            for music_type_slug, music_type in music_types.MUSIC_SUB_TYPES_BY_SLUG.items()
        ]
    )


@blueprint.v1_offers_blueprint.route("/music_types/all", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.OFFER_ATTRIBUTES],
    response_model=serialization.GetMusicTypesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetMusicTypesResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@api_key_required
def get_all_titelive_music_types() -> serialization.GetMusicTypesResponse:
    """
    Get all music types

    Return all the music types.
    """
    return serialization.GetMusicTypesResponse(
        __root__=[
            serialization.TiteliveMusicTypeResponse(
                id=TITELIVE_MUSIC_GENRES_BY_GTL_ID[music_type.gtl_id], label=music_type.label
            )
            for music_type in TITELIVE_MUSIC_TYPES
        ]
    )


@blueprint.v1_offers_blueprint.route("/music_types/event", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.OFFER_ATTRIBUTES],
    response_model=serialization.GetMusicTypesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetMusicTypesResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@api_key_required
def get_event_titelive_music_types() -> serialization.GetMusicTypesResponse:
    """
    Get events music types

    Return all eligible music types for events.
    """
    return serialization.GetMusicTypesResponse(
        __root__=[
            serialization.TiteliveMusicTypeResponse(
                id=TITELIVE_MUSIC_GENRES_BY_GTL_ID[music_type.gtl_id], label=music_type.label
            )
            for music_type in TITELIVE_MUSIC_TYPES
            if music_type.can_be_event
        ]
    )


@blueprint.v1_offers_blueprint.route("/products", methods=["POST"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFER_TAG],
    response_model=serialization.ProductOfferResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_201": (serialization.ProductOfferResponse, "The product offer have been created successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_VENUE_NOT_FOUND
        )
    ),
)
@api_key_required
def post_product_offer(body: serialization.ProductOfferCreation) -> serialization.ProductOfferResponse:
    """
    Create product

    Create a product in authorized categories.
    """
    venue = utils.retrieve_venue_from_location(body.location)

    try:
        with repository.transaction():
            created_offer = offers_api.create_offer(
                audio_disability_compliant=body.accessibility.audio_disability_compliant,
                booking_contact=body.booking_contact,
                booking_email=body.booking_email,
                description=body.description,
                external_ticket_office_url=body.external_ticket_office_url,
                extra_data=serialization.deserialize_extra_data(body.category_related_fields),
                is_duo=body.is_duo,
                mental_disability_compliant=body.accessibility.mental_disability_compliant,
                motor_disability_compliant=body.accessibility.motor_disability_compliant,
                name=body.name,
                provider=current_api_key.provider,
                subcategory_id=body.category_related_fields.subcategory_id,
                url=body.location.url if isinstance(body.location, serialization.DigitalLocation) else None,
                venue=venue,
                visual_disability_compliant=body.accessibility.visual_disability_compliant,
                withdrawal_details=body.withdrawal_details,
            )

            if body.image:
                utils.save_image(body.image, created_offer)

            # To create stocks or publishing the offer we need to flush
            # the session to get the offer id
            db.session.flush()
            if body.stock:
                offers_api.create_stock(
                    offer=created_offer,
                    price=finance_utils.to_euros(body.stock.price),
                    quantity=serialization.deserialize_quantity(body.stock.quantity),
                    booking_limit_datetime=body.stock.booking_limit_datetime,
                    creating_provider=current_api_key.provider,
                )

            offers_api.publish_offer(created_offer, user=None)

    except (offers_exceptions.OfferCreationBaseException, offers_exceptions.OfferEditionBaseException) as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.ProductOfferResponse.build_product_offer(created_offer)


@blueprint.v1_offers_blueprint.route("/products/ean", methods=["POST"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_EAN_OFFER_TAG],
    on_success_status=204,
    resp=SpectreeResponse(
        **(
            {"HTTP_204": (None, "The product offers have been created successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_VENUE_NOT_FOUND
        )
    ),
)
@api_key_required
def post_product_offer_by_ean(body: serialization.ProductsOfferByEanCreation) -> None:
    """
    Batch create offers

    Batch create offers using products EAN. EAN is the European Article Number identifiying each product sold in the european market (EAN-13).
    """
    venue = utils.retrieve_venue_from_location(body.location)
    if venue.isVirtual:
        raise api_errors.ApiErrors({"location": ["Cannot create product offer for virtual venues"]})
    serialized_products_stocks = _serialize_products_from_body(body.products)
    _create_or_update_ean_offers.delay(serialized_products_stocks, venue.id, current_api_key.provider.id)


@job(worker.low_queue)
def _create_or_update_ean_offers(serialized_products_stocks: dict, venue_id: int, provider_id: int) -> None:
    provider = providers_models.Provider.query.filter_by(id=provider_id).one()
    venue = offerers_models.Venue.query.filter_by(id=venue_id).one()

    ean_to_create_or_update = set(serialized_products_stocks.keys())

    offers_to_update = _get_existing_offers(ean_to_create_or_update, venue)

    offer_to_update_by_ean = {}
    ean_list_to_update = set()
    for offer in offers_to_update:
        ean_list_to_update.add(offer.extraData["ean"])  # type: ignore [index]
        offer_to_update_by_ean[offer.extraData["ean"]] = offer  # type: ignore [index]

    ean_list_to_create = ean_to_create_or_update - ean_list_to_update
    offers_to_index = []
    with repository.transaction():
        if ean_list_to_create:
            created_offers = []
            existing_products = _get_existing_products(ean_list_to_create)
            product_by_ean = {product.extraData["ean"]: product for product in existing_products}  # type: ignore [index]
            not_found_eans = [ean for ean in ean_list_to_create if ean not in product_by_ean.keys()]
            if not_found_eans:
                logger.warning(
                    "Some provided eans were not found",
                    extra={"eans": ",".join(not_found_eans), "venue": venue_id},
                    technical_message_id="ean.not_found",
                )
            for product in existing_products:
                try:
                    ean = product.extraData["ean"] if product.extraData else None
                    stock_data = serialized_products_stocks[ean]
                    created_offer = _create_offer_from_product(
                        venue,
                        product_by_ean[ean],
                        provider,
                    )
                    created_offers.append(created_offer)

                except (
                    offers_exceptions.OfferCreationBaseException,
                    offers_exceptions.OfferEditionBaseException,
                ) as exc:
                    logger.info(
                        "Error while creating offer by ean",
                        extra={
                            "ean": ean,
                            "venue_id": venue_id,
                            "provider_id": provider_id,
                            "exc": exc.__class__.__name__,
                        },
                    )

            db.session.bulk_save_objects(created_offers)

            reloaded_offers = _get_existing_offers(ean_list_to_create, venue)
            for offer in reloaded_offers:
                try:
                    ean = offer.extraData["ean"]  # type: ignore [index]
                    stock_data = serialized_products_stocks[ean]
                    # FIXME (mageoffray, 2023-05-26): stock saving optimisation
                    # Stocks are inserted one by one for now, we need to improve create_stock to remove the repository.session.add()
                    # It will be done before the release of this API
                    offers_api.create_stock(
                        offer=offer,
                        price=finance_utils.to_euros(stock_data["price"]),
                        quantity=serialization.deserialize_quantity(stock_data["quantity"]),
                        booking_limit_datetime=stock_data["booking_limit_datetime"],
                        creating_provider=provider,
                    )
                except (
                    offers_exceptions.OfferCreationBaseException,
                    offers_exceptions.OfferEditionBaseException,
                ) as exc:
                    logger.info(
                        "Error while creating offer by ean",
                        extra={
                            "ean": ean,
                            "venue_id": venue_id,
                            "provider_id": provider_id,
                            "exc": exc.__class__.__name__,
                        },
                    )

        for offer in offers_to_update:
            try:
                offer.lastProvider = provider
                offer.isActive = True

                ean = offer.extraData["ean"]  # type: ignore [index]
                stock_data = serialized_products_stocks[ean]
                # FIXME (mageoffray, 2023-05-26): stock upserting optimisation
                # Stocks are edited one by one for now, we need to improve edit_stock to remove the repository.session.add()
                # It will be done before the release of this API
                _upsert_product_stock(
                    offer_to_update_by_ean[ean],
                    serialization.StockEdition(
                        **{
                            "price": stock_data["price"],
                            "quantity": stock_data["quantity"],
                            "booking_limit_datetime": stock_data["booking_limit_datetime"],
                        }
                    ),
                    provider,
                )
                offers_to_index.append(offer_to_update_by_ean[ean].id)
            except (offers_exceptions.OfferCreationBaseException, offers_exceptions.OfferEditionBaseException) as exc:
                logger.info(
                    "Error while creating offer by ean",
                    extra={"ean": ean, "venue_id": venue_id, "provider_id": provider_id, "exc": exc.__class__.__name__},
                )

    search.async_index_offer_ids(
        offers_to_index,
        reason=search.IndexationReason.OFFER_UPDATE,
        log_extra={"venue_id": venue_id, "source": "offers_public_api"},
    )


def _get_existing_products(ean_to_create: set[str]) -> list[offers_models.Product]:
    allowed_product_subcategories = [
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
        subcategories.LIVRE_PAPIER.id,
    ]
    return offers_models.Product.query.filter(
        offers_models.Product.extraData["ean"].astext.in_(ean_to_create),
        offers_models.Product.can_be_synchronized == True,
        offers_models.Product.subcategoryId.in_(allowed_product_subcategories),
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
            sqla.func.max(offers_models.Offer.id).label("max_id"),
        )
        .filter(offers_models.Offer.isEvent == False)
        .filter(offers_models.Offer.venue == venue)
        .filter(offers_models.Offer.extraData["ean"].astext.in_(ean_to_create_or_update))
        .group_by(offers_models.Offer.extraData["ean"], offers_models.Offer.venueId)
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
) -> offers_models.Offer:
    ean = product.extraData.get("ean") if product.extraData else None

    offer = offers_api.build_new_offer_from_product(venue, product, ean, provider.id)

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


@blueprint.v1_offers_blueprint.route("/products/<int:product_id>", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFER_TAG],
    response_model=serialization.ProductOfferResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.ProductOfferResponse, "The product offer")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_404_PRODUCT_NOT_FOUND
        )
    ),
)
@api_key_required
def get_product(product_id: int) -> serialization.ProductOfferResponse:
    """
    Get product offer

    Return a product offer by id.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(product_id))
        .filter(sqla.not_(offers_models.Offer.isEvent))
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"product_id": ["The product offer could not be found"]}, status_code=404)

    return serialization.ProductOfferResponse.build_product_offer(offer)


@blueprint.v1_offers_blueprint.route("/products/ean", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_EAN_OFFER_TAG],
    response_model=serialization.ProductOffersByEanResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.ProductOffersByEanResponse, "The product offers")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@api_key_required
def get_product_by_ean(
    query: serialization.GetProductsListByEansQuery,
) -> serialization.ProductOffersByEanResponse:
    """
    Get product offers by EAN

    Return all the product offers of a given venue matching given EANs (European Article Number, EAN-13).
    """
    utils.check_venue_id_is_tied_to_api_key(query.venueId)
    offers: list[offers_models.Offer] | None = (
        utils.retrieve_offer_relations_query(_retrieve_offer_by_eans_query(query.eans, query.venueId))  # type: ignore [arg-type]
        .filter(sqla.not_(offers_models.Offer.isEvent))
        .all()
    )

    if not offers:
        return serialization.ProductOffersByEanResponse(products=[])

    return serialization.ProductOffersByEanResponse(
        products=[serialization.ProductOfferResponse.build_product_offer(offer) for offer in offers]
    )


def _retrieve_offer_by_eans_query(eans: list[str], venueId: int) -> sqla.orm.Query:
    return (
        utils._retrieve_offer_tied_to_user_query()
        .filter(
            offers_models.Offer.extraData["ean"].astext.in_(eans),
            offers_models.Offer.venueId == venueId,
        )
        .order_by(offers_models.Offer.id.desc())
    )


@blueprint.v1_offers_blueprint.route("/products", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFER_TAG],
    response_model=serialization.ProductOffersResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.ProductOffersResponse, "The product offers")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_404_VENUE_NOT_FOUND
        )
    ),
)
@api_key_required
def get_products(
    query: serialization.GetOffersQueryParams,
) -> serialization.ProductOffersResponse:
    """
    Get venue products

    Return all products linked to a venue. Results are paginated (by default `50` products by page).
    """
    utils.check_venue_id_is_tied_to_api_key(query.venue_id)
    total_offers_query = utils.retrieve_offers(
        is_event=False, firstIndex=query.firstIndex, filtered_venue_id=query.venue_id
    ).limit(query.limit)

    return serialization.ProductOffersResponse(
        products=[serialization.ProductOfferResponse.build_product_offer(offer) for offer in total_offers_query],
    )


def _check_offer_can_be_edited(offer: offers_models.Offer) -> None:
    allowed_product_subcategory_ids = [category.id for category in serialization.ALLOWED_PRODUCT_SUBCATEGORIES]
    if offer.subcategoryId not in allowed_product_subcategory_ids:
        raise api_errors.ApiErrors(
            {
                "product.subcategory": [
                    "Only "
                    + ", ".join((subcategory.id for subcategory in serialization.ALLOWED_PRODUCT_SUBCATEGORIES))
                    + " products can be edited"
                ]
            }
        )


@blueprint.v1_offers_blueprint.route("/products", methods=["PATCH"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFER_TAG],
    response_model=serialization.ProductOfferResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.ProductOfferResponse, "The product offer have been edited successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRODUCT_NOT_FOUND
        )
    ),
)
@api_key_required
def edit_product(body: serialization.ProductOfferEdition) -> serialization.ProductOfferResponse:
    """
    Update product offer

    Will update only the non-blank fields.
    If you want to keep the current value of certains fields, leave them `undefined`.
    """
    offer = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(body.offer_id))
        .filter(sqla.not_(offers_models.Offer.isEvent))
        .one_or_none()
    )

    if not offer:
        raise api_errors.ApiErrors({"offerId": ["The product offer could not be found"]}, status_code=404)

    _check_offer_can_be_edited(offer)
    utils.check_offer_subcategory(body, offer.subcategoryId)
    try:
        with repository.transaction():
            updated_offer_from_body = body.dict(exclude_unset=True)
            updated_offer = offers_api.update_offer(
                offer,
                bookingContact=updated_offer_from_body.get("booking_contact", offers_api.UNCHANGED),
                bookingEmail=updated_offer_from_body.get("booking_email", offers_api.UNCHANGED),
                extraData=(
                    serialization.deserialize_extra_data(body.category_related_fields, copy.deepcopy(offer.extraData))
                    if body.category_related_fields
                    else offers_api.UNCHANGED
                ),
                isActive=updated_offer_from_body.get("is_active", offers_api.UNCHANGED),
                isDuo=updated_offer_from_body.get("is_duo", offers_api.UNCHANGED),
                withdrawalDetails=updated_offer_from_body.get("withdrawal_details", offers_api.UNCHANGED),
                **utils.compute_accessibility_edition_fields(updated_offer_from_body.get("accessibility")),
            )
            if body.image:
                utils.save_image(body.image, updated_offer)
            if "stock" in updated_offer_from_body:
                _upsert_product_stock(updated_offer, body.stock, current_api_key.provider)
    except (offers_exceptions.OfferCreationBaseException, offers_exceptions.OfferEditionBaseException) as e:
        raise api_errors.ApiErrors(e.errors, status_code=400)

    return serialization.ProductOfferResponse.build_product_offer(offer)


def _upsert_product_stock(
    offer: offers_models.Offer,
    stock_body: serialization.StockEdition | None,
    provider: providers_models.Provider,
) -> None:
    existing_stock = next((stock for stock in offer.activeStocks), None)
    if not stock_body:
        if existing_stock:
            offers_api.delete_stock(existing_stock)
        return

    if not existing_stock:
        if not stock_body.price:
            raise api_errors.ApiErrors({"stock.price": ["Required"]})
        offers_api.create_stock(
            offer=offer,
            price=finance_utils.to_euros(stock_body.price),
            quantity=serialization.deserialize_quantity(stock_body.quantity),
            booking_limit_datetime=stock_body.booking_limit_datetime,
            creating_provider=provider,
        )
        return

    stock_update_body = stock_body.dict(exclude_unset=True)
    price = stock_update_body.get("price", offers_api.UNCHANGED)
    quantity = serialization.deserialize_quantity(stock_update_body.get("quantity", offers_api.UNCHANGED))
    offers_api.edit_stock(
        existing_stock,
        quantity=quantity + existing_stock.dnBookedQuantity if isinstance(quantity, int) else quantity,
        price=finance_utils.to_euros(price) if price != offers_api.UNCHANGED else offers_api.UNCHANGED,
        booking_limit_datetime=stock_update_body.get("booking_limit_datetime", offers_api.UNCHANGED),
        editing_provider=provider,
    )


@blueprint.v1_offers_blueprint.route("/products/categories", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFER_TAG],
    response_model=serialization.GetProductCategoriesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetProductCategoriesResponse, "The product categories have been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@api_key_required
def get_product_categories() -> serialization.GetProductCategoriesResponse:
    """
    Get product categories

    Return all product categories with their conditional fields, and whether they are required for product creation.
    """
    # Individual offers API only relies on subcategories, not categories.
    # To make it simpler for the provider using this API, we only expose subcategories and call them categories.
    product_categories_response = [
        serialization.ProductCategoryResponse.build_category(subcategory)
        for subcategory in serialization.ALLOWED_PRODUCT_SUBCATEGORIES
    ]
    return serialization.GetProductCategoriesResponse(__root__=product_categories_response)


@blueprint.v1_offers_blueprint.route("/<int:offer_id>/image", methods=["POST"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.IMAGE_TAG],
    on_success_status=204,
    resp=SpectreeResponse(
        **({"HTTP_204": (None, "Image updated successfully")} | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS),
    ),
)
@api_key_required
def upload_image(offer_id: int, form: serialization.ImageUploadFile) -> None:
    """
    Upload an image

    Upload an image for given offer.
    """
    offer = utils.retrieve_offer_relations_query(utils.retrieve_offer_query(offer_id)).one_or_none()
    if not offer:
        raise api_errors.ApiErrors({"offerId": ["The offer could not be found"]}, status_code=404)
    try:
        image_as_bytes = request.files["file"].read()
    except Exception as err:
        logger.exception("Error while reading image file", extra={"offer_id": offer_id, "err": err})
        raise api_errors.ApiErrors({"file": ["The image is not valid."]}, status_code=400)
    try:
        with repository.transaction():
            offers_api.create_mediation(
                user=None,
                offer=offer,
                credit=form.credit,
                image_as_bytes=image_as_bytes,
            )
    except offers_exceptions.ImageValidationError as error:
        if isinstance(error, offers_exceptions.ImageTooSmall):
            message = f"The image is too small. It must be above {constants.MIN_IMAGE_WIDTH}x{constants.MIN_IMAGE_HEIGHT} pixels."
        elif isinstance(error, offers_exceptions.ImageTooLarge):
            message = f"The image is too large. It must be below {constants.MAX_IMAGE_WIDTH}x{constants.MAX_IMAGE_HEIGHT} pixels."
        elif isinstance(error, offers_exceptions.UnacceptedFileType):
            message = f"The image format is not accepted. It must be in {offers_validation.ACCEPTED_THUMBNAIL_FORMATS}."
        elif isinstance(error, offers_exceptions.UnidentifiedImage):
            message = "The file is not a valid image."
        elif isinstance(error, offers_exceptions.FileSizeExceeded):
            message = f"The file is too large. It must be less than {offers_validation.MAX_THUMBNAIL_SIZE} bytes."
        else:
            message = "The image is not valid."
        raise api_errors.ApiErrors(errors={"file": message})
    except image_conversion.ImageRatioError as error:
        raise api_errors.ApiErrors(
            errors={"file": f"Bad image ratio: expected {str(error.expected)[:4]}, found {str(error.found)[:4]}"}
        )
