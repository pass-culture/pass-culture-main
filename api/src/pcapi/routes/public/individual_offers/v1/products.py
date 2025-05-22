import copy
import datetime
import logging

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from flask import request
from psycopg2.errorcodes import UNIQUE_VIOLATION

from pcapi import repository
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.categories.genres import show
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import tasks as offers_tasks
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.offers import constants as offers_constants
from pcapi.core.offers import validation as offers_validation
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.constants import TITELIVE_MUSIC_GENRES_BY_GTL_ID
from pcapi.core.providers.constants import TITELIVE_MUSIC_TYPES
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public import utils as public_utils
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.services import authorization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils import image_conversion
from pcapi.utils.custom_keys import get_field
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import provider_api_key_required
from pcapi.workers import worker
from pcapi.workers.decorators import job

from . import constants
from . import serialization
from . import utils


logger = logging.getLogger(__name__)


@blueprints.public_api.route("/public/offers/v1/show_types", methods=["GET"])
@provider_api_key_required
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
def get_show_types() -> serialization.GetShowTypesResponse:
    """
    Get Show Types

    Return show types.
    """
    # Individual offers API only relies on show subtypes, not show types.
    # To make it simpler for the provider using this API, we only expose show subtypes and call them show types.
    return serialization.GetShowTypesResponse(
        __root__=[
            serialization.ShowTypeResponse(id=show_type_slug, label=show_type.label)
            for show_type_slug, show_type in show.SHOW_SUB_TYPES_BY_SLUG.items()
        ]
    )


@blueprints.public_api.route("/public/offers/v1/music_types", methods=["GET"])
@provider_api_key_required
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
            for music_type_slug, music_type in music.MUSIC_SUB_TYPES_BY_SLUG.items()
        ]
    )


@blueprints.public_api.route("/public/offers/v1/music_types/all", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.OFFER_ATTRIBUTES],
    response_model=serialization.GetTiteliveMusicTypesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetTiteliveMusicTypesResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def get_all_titelive_music_types() -> serialization.GetTiteliveMusicTypesResponse:
    """
    Get Music Types

    Return music types. Not all the music types returned by this endpoint are suitable
    for events. For events, use the [Get events music types endpoint](/rest-api#tag/Offer-Attributes/operation/GetEventTiteliveMusicTypes).
    """
    return serialization.GetTiteliveMusicTypesResponse(
        __root__=[
            serialization.TiteliveMusicTypeResponse(
                id=TITELIVE_MUSIC_GENRES_BY_GTL_ID[music_type.gtl_id], label=music_type.label
            )
            for music_type in TITELIVE_MUSIC_TYPES
        ]
    )


@blueprints.public_api.route("/public/offers/v1/music_types/event", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.OFFER_ATTRIBUTES],
    response_model=serialization.GetTiteliveEventMusicTypesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetTiteliveEventMusicTypesResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def get_event_titelive_music_types() -> serialization.GetTiteliveEventMusicTypesResponse:
    """
    Get Events Music Types

    Return eligible music types for events.
    """
    return serialization.GetTiteliveEventMusicTypesResponse(
        __root__=[
            serialization.TiteliveEventMusicTypeResponse(
                id=TITELIVE_MUSIC_GENRES_BY_GTL_ID[music_type.gtl_id], label=music_type.label
            )
            for music_type in TITELIVE_MUSIC_TYPES
            if music_type.can_be_event
        ]
    )


def _create_stock(product: offers_models.Offer, body: serialization.ProductOfferCreation) -> None:
    if not body.stock:
        return

    if body.stock.quantity == 0:
        return

    try:
        offers_api.create_stock(
            offer=product,
            price=finance_utils.cents_to_full_unit(body.stock.price),
            quantity=serialization.deserialize_quantity(body.stock.quantity),
            booking_limit_datetime=body.stock.booking_limit_datetime,
            creating_provider=current_api_key.provider,
        )
    except sa_exc.SQLAlchemyError as error:
        raise offers_exceptions.CreateStockDBError() from error
    except Exception as error:
        raise offers_exceptions.CreateStockError() from error


@blueprints.public_api.route("/public/offers/v1/products", methods=["POST"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFERS],
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
def post_product_offer(body: serialization.ProductOfferCreation) -> serialization.ProductOfferResponse:
    """
    Create Product Offer

    Create a product in authorized categories.
    """
    venue_provider = authorization.get_venue_provider_or_raise_404(body.location.venue_id)
    venue = utils.get_venue_with_offerer_address(venue_provider.venueId)

    try:
        with repository.transaction():
            offerer_address = venue.offererAddress  # default offerer_address

            if body.location.type == "address":
                address = public_utils.get_address_or_raise_404(body.location.address_id)
                offerer_address = offerers_api.get_or_create_offerer_address(
                    offerer_id=venue.managingOffererId,
                    address_id=address.id,
                    label=body.location.address_label,
                )
            product = offers_api.create_product(venue=venue, body=body, offerer_address=offerer_address)

            if body.image:
                utils.save_image(body.image, product)

            _create_stock(product=product, body=body)
            offers_api.update_offer_fraud_information(product, user=None)
            offers_api.publish_offer(product)
    except offers_exceptions.ExistingVenueWithIdAtProviderError as error:
        raise api_errors.ApiErrors({"error": error.msg}, status_code=400)
    except offers_exceptions.CreateProductError as error:
        # This is very unlikely. Therefore, the error should be logged in
        # order to check that there is no bug on our side.
        logger.error("Unlikely create product error encountered", extra={"error": error, "body": body})
        raise api_errors.ApiErrors({"error": error.msg}, status_code=400)
    except offers_exceptions.OfferException as error:
        raise api_errors.ApiErrors(error.errors)

    return serialization.ProductOfferResponse.build_product_offer(product)


@blueprints.public_api.route("/public/offers/v1/products/ean", methods=["POST"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_EAN_OFFERS],
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
def post_product_offer_by_ean(body: serialization.ProductsOfferByEanCreation) -> None:
    """
    Batch Upsert Product Offers by EAN

    This endpoint allows for the batch upsert (update or insert) of product offers and their corresponding stock levels using the **European Article Number (EAN-13)**. It performs the following operations:

    1. **Create Offers:** If a venue does not have an existing offer for a product identified by its EAN, the endpoint creates a new offer.

    2. **Update Offer Stocks:** It updates the stock levels for the product offers. If the stock quantity is set to `0`, the product offer stock is deleted.

    The upsert process is **asynchronous**, meaning the operation may take some time to complete. The success response from this endpoint indicates only that the upsert job has been successfully added to the queue.

    **WARNING:** As it is an asynchronous you won't be given any feedback if one or more EANs is rejected.
    To make sure that your EANs won't be rejected please use [**this endpoint**](/rest-api#tag/Product-Offer-Bulk-Operations/operation/CheckEansAvailability)
    """
    venue_provider = authorization.get_venue_provider_or_raise_404(body.location.venue_id)
    venue = utils.get_venue_with_offerer_address(venue_provider.venueId)
    address_id = None
    address_label = None

    if venue.isVirtual:
        raise api_errors.ApiErrors({"location": ["Cannot create product offer for virtual venues"]})

    if body.location.type == "address":
        address = public_utils.get_address_or_raise_404(body.location.address_id)
        address_id = address.id
        address_label = body.location.address_label

    serialized_products_stocks = _serialize_products_from_body(body.products)
    offers_tasks.create_or_update_ean_offers.delay(
        serialized_products_stocks=serialized_products_stocks,
        venue_id=venue.id,
        provider_id=current_api_key.provider.id,
        address_id=address_id,
        address_label=address_label,
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


@blueprints.public_api.route("/public/offers/v1/products/<int:product_id>", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFERS],
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
def get_product(product_id: int) -> serialization.ProductOfferResponse:
    """
    Get Product Offer

    Return a product offer by id.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(product_id))
        .filter(sa.not_(offers_models.Offer.isEvent))
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"product_id": ["The product offer could not be found"]}, status_code=404)

    return serialization.ProductOfferResponse.build_product_offer(offer)


@blueprints.public_api.route("/public/offers/v1/products/ean", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_EAN_OFFERS],
    response_model=serialization.ProductOffersByEanResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.ProductOffersByEanResponse, "The product offers")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def get_product_by_ean(
    query: serialization.GetProductsListByEansQuery,
) -> serialization.ProductOffersByEanResponse:
    """
    Get Product Offers by EANs

    Return all the product offers of a given venue matching given EANs (European Article Number, EAN-13).
    """
    utils.check_venue_id_is_tied_to_api_key(query.venueId)
    offers: list[offers_models.Offer] | None = (
        utils.retrieve_offer_relations_query(_retrieve_offer_by_eans_query(query.eans, query.venueId))  # type: ignore[arg-type]
        .filter(sa.not_(offers_models.Offer.isEvent))
        .all()
    )

    if not offers:
        return serialization.ProductOffersByEanResponse(products=[])

    return serialization.ProductOffersByEanResponse(
        products=[serialization.ProductOfferResponse.build_product_offer(offer) for offer in offers]
    )


@blueprints.public_api.route("/public/offers/v1/products/ean/check_availability", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_EAN_OFFERS],
    response_model=serialization.AvailableEANsResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.AvailableEANsResponse, "EANs by availability")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def check_eans_availability(
    query: serialization.GetAvailableEANsListQuery,
) -> serialization.AvailableEANsResponse:
    """
    Check EAN Availability for Bulk Upsert

    This endpoint checks the availability of a list of EANs (European Article Numbers) for a bulk upsert operation.
    The response contains the EANs categorized by their availability status.

    **Response Structure**

    - `available`: A list of EANs that are available for upsert.

    - `rejected`: A list of EANs that are not available for upsert, sorted by their rejection reasons.

    **Rejection Reasons**

    An EAN can be rejected for the following reasons:

    - `notFound`: The EAN is not present in our database.

    - `subcategoryNotAllowed`: The product identified by the EAN does not belong to an allowed category (only paper books, CDs, and vinyl records are permitted).

    - `notCompliantWithCgu`: The product identified by the EAN does not comply with our CGU (General Terms and Conditions).
    """
    eans_to_check = set(query.eans)
    existing_products = (
        db.session.query(offers_models.Product)
        .filter(
            offers_models.Product.ean.in_(eans_to_check),
        )
        .all()
    )

    rejected_eans_because_subcategory_is_not_allowed = []
    rejected_eans_for_cgu_violation = []
    available_eans = []

    for product in existing_products:
        product_ean = product.ean
        eans_to_check.remove(product_ean)

        if product.subcategoryId not in offers_constants.ALLOWED_PRODUCT_SUBCATEGORIES:
            rejected_eans_because_subcategory_is_not_allowed.append(product_ean)
        elif not product.can_be_synchronized:
            rejected_eans_for_cgu_violation.append(product_ean)
        else:
            available_eans.append(product_ean)

    return serialization.AvailableEANsResponse.build_response(
        available=available_eans,
        # rejected
        not_compliant_with_cgu=rejected_eans_for_cgu_violation,
        not_found=list(eans_to_check),  # remaining EANs are the ones that were not found
        subcategory_not_allowed=rejected_eans_because_subcategory_is_not_allowed,
    )


def _retrieve_offer_by_eans_query(eans: list[str], venueId: int) -> sa_orm.Query:
    return (
        utils._retrieve_offer_tied_to_user_query()
        .filter(
            offers_models.Offer.ean.in_(eans),
            offers_models.Offer.venueId == venueId,
        )
        .order_by(offers_models.Offer.id.desc())
    )


@blueprints.public_api.route("/public/offers/v1/products", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFERS],
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
def get_products(
    query: serialization.GetOffersQueryParams,
) -> serialization.ProductOffersResponse:
    """
    Get Product Offers

    Return fitered products.

    Results are paginated (by default `50` products by page).
    """
    if query.venue_id:
        authorization.get_venue_provider_or_raise_404(query.venue_id)

    total_offers_query = utils.get_filtered_offers_linked_to_provider(query, is_event=False)

    return serialization.ProductOffersResponse(
        products=[serialization.ProductOfferResponse.build_product_offer(offer) for offer in total_offers_query],
    )



@blueprints.public_api.route("/public/offers/v1/products", methods=["PATCH"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFERS],
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
def edit_product(body: serialization.ProductOfferEdition) -> serialization.ProductOfferResponse:
    """
    Update Product Offer

    Will update only the non-blank fields.
    If you want to keep the current value of certains fields, leave them `undefined`.
    """
    query = utils.retrieve_offer_query(body.offer_id)
    query = utils.retrieve_offer_relations_query(query)
    query = utils.load_venue_and_provider_query(query)
    query = query.filter(sa.not_(offers_models.Offer.isEvent))

    offer = query.one_or_none()

    if not offer:
        raise api_errors.ApiErrors({"offerId": ["The product offer could not be found"]}, status_code=404)

    offers_api.check_offer_can_be_edited(offer)
    utils.check_offer_subcategory(body, offer.subcategoryId)

    venue, offerer_address = utils.extract_venue_and_offerer_address_from_location(body)

    try:
        with repository.transaction():
            updates = body.dict(by_alias=True, exclude_unset=True)
            dc = updates.get("accessibility", {})
            extra_data = copy.deepcopy(offer.extraData)
            offer_body = offers_schemas.UpdateOffer(
                name=get_field(offer, updates, "name"),
                audioDisabilityCompliant=get_field(offer, dc, "audioDisabilityCompliant"),
                mentalDisabilityCompliant=get_field(offer, dc, "mentalDisabilityCompliant"),
                motorDisabilityCompliant=get_field(offer, dc, "motorDisabilityCompliant"),
                visualDisabilityCompliant=get_field(offer, dc, "visualDisabilityCompliant"),
                bookingContact=get_field(offer, updates, "bookingContact"),
                bookingEmail=get_field(offer, updates, "bookingEmail"),
                description=get_field(offer, updates, "description"),
                extraData=(
                    serialization.deserialize_extra_data(
                        body.category_related_fields, extra_data, venue_id=venue.id if venue else None
                    )
                    if "categoryRelatedFields" in updates
                    else extra_data
                ),
                isActive=get_field(offer, updates, "isActive"),
                idAtProvider=get_field(offer, updates, "idAtProvider"),
                isDuo=get_field(offer, updates, "enableDoubleBookings", col="isDuo"),
                withdrawalDetails=get_field(offer, updates, "itemCollectionDetails", col="withdrawalDetails"),
            )  # type: ignore[call-arg]
            updated_offer = offers_api.update_offer(offer, offer_body, venue=venue, offerer_address=offerer_address)
            if body.image:
                utils.save_image(body.image, updated_offer)
            if "stock" in updates:
                offers_api.upsert_product_stock(updated_offer, body.stock, current_api_key.provider)
    except offers_exceptions.OfferException as e:
        raise api_errors.ApiErrors(e.errors)

    # TODO(jeremieb): this should not be needed. BUT since datetime from
    # db are not timezone aware and those from the request are...
    # things get complicated during serialization (which does not
    # know how to serialize timezone-aware datetime). So... reload
    # everything and use data from the db.
    offer = query.one_or_none()
    return serialization.ProductOfferResponse.build_product_offer(offer)


@blueprints.public_api.route("/public/offers/v1/products/categories", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PRODUCT_OFFERS],
    response_model=serialization.GetProductCategoriesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetProductCategoriesResponse, "The product categories have been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def get_product_categories() -> serialization.GetProductCategoriesResponse:
    """
    Get Product Categories

    Return all product categories with their conditional fields, and whether they are required for product creation.
    """
    # Individual offers API only relies on subcategories, not categories.
    # To make it simpler for the provider using this API, we only expose subcategories and call them categories.
    product_categories_response = [
        serialization.ProductCategoryResponse.build_category(subcategory)
        for subcategory in serialization.ALLOWED_PRODUCT_SUBCATEGORIES
    ]
    return serialization.GetProductCategoriesResponse(__root__=product_categories_response)


@blueprints.public_api.route("/public/offers/v1/<int:offer_id>/image", methods=["POST"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.IMAGE],
    on_success_status=204,
    resp=SpectreeResponse(
        **({"HTTP_204": (None, "Image updated successfully")} | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS),
    ),
)
def upload_image(offer_id: int, form: serialization.ImageUploadFile) -> None:
    """
    Upload an Image

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
