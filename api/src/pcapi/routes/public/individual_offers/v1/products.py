import copy
import datetime
import itertools
import logging

import flask
import sqlalchemy as sqla

from pcapi import repository
from pcapi.core import search
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.core.providers import models as providers_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.workers import worker
from pcapi.workers.decorators import job

from . import blueprint
from . import constants
from . import serialization
from . import utils


logger = logging.getLogger(__name__)


@blueprint.v1_blueprint.route("/offerer_venues", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_product_schema,
    tags=[constants.OFFERER_VENUES_TAG],
    response_model=serialization.GetOfferersVenuesResponse,
)
@api_key_required
def get_offerer_venues(
    query: serialization.GetOfferersVenuesQuery,
) -> serialization.GetOfferersVenuesResponse:
    """
    Get offerer attached the API key used and its venues.
    """
    offerers_query = (
        db.session.query(offerers_models.Offerer, offerers_models.Venue)
        .join(offerers_models.Venue, offerers_models.Offerer.managedVenues)
        .join(providers_models.VenueProvider, offerers_models.Venue.venueProviders)
        .filter(providers_models.VenueProvider.provider == current_api_key.provider)
        .order_by(offerers_models.Offerer.id, offerers_models.Venue.id)
    )

    if query.siren:
        offerers_query = offerers_query.filter(offerers_models.Offerer.siren == query.siren)

    accessible_venues_and_offerer = []
    for offerer, group in itertools.groupby(offerers_query, lambda row: row.Offerer):
        accessible_venues_and_offerer.append(
            {
                "offerer": offerer,
                "venues": [serialization.VenueResponse.build_model(row.Venue) for row in group],
            }
        )
    return serialization.GetOfferersVenuesResponse(__root__=accessible_venues_and_offerer)  # type: ignore [arg-type]


def _retrieve_offer_by_eans_query(eans: list[str]) -> sqla.orm.Query:
    return (
        utils._retrieve_offer_tied_to_user_query()
        .filter(offers_models.Offer.extraData["ean"].astext.in_(eans))
        .order_by(offers_models.Offer.id.desc())
    )


@blueprint.v1_blueprint.route("/products", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_product_schema,
    tags=[constants.PRODUCT_OFFER_TAG],
    response_model=serialization.ProductOfferResponse,
)
@api_key_required
def post_product_offer(
    body: serialization.ProductOfferCreation,
) -> serialization.ProductOfferResponse:
    """
    Create a book, CD or vinyl product.
    """
    venue = utils.retrieve_venue_from_location(body.location)

    try:
        with repository.transaction():
            created_offer = offers_api.create_offer(
                audio_disability_compliant=body.accessibility.audio_disability_compliant,
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

            # To create the stock, the offer needs to have an id
            db.session.flush()
            if body.stock:
                offers_api.create_stock(
                    offer=created_offer,
                    price=finance_utils.to_euros(body.stock.price),
                    quantity=serialization.deserialize_quantity(body.stock.quantity),
                    booking_limit_datetime=body.stock.booking_limit_datetime,
                    creating_provider=current_api_key.provider,
                )
            if body.image:
                utils.save_image(body.image, created_offer)

            offers_api.publish_offer(created_offer, user=None)

    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.ProductOfferResponse.build_product_offer(created_offer)


@blueprint.v1_blueprint.route("/products/ean", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_product_schema,
    tags=[constants.PRODUCT_EAN_OFFER_TAG],
    on_success_status=204,
)
@api_key_required
def post_product_offer_by_ean(body: serialization.ProductsOfferByEanCreation) -> None:
    """
    Create products offer using their European Article Number (EAN-13).
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

    offers_to_update = _get_existing_offers(ean_to_create_or_update, venue, provider)

    offer_to_update_by_ean = {}
    ean_list_to_update = set()
    for offer in offers_to_update:
        ean_list_to_update.add(offer.extraData["ean"])  # type: ignore [index]
        offer_to_update_by_ean[offer.extraData["ean"]] = offer  # type: ignore [index]

    ean_list_to_create = ean_to_create_or_update - ean_list_to_update
    offers_to_index = []

    if ean_list_to_create:
        created_offers = []
        existing_products = _get_existing_products(ean_list_to_create)
        product_by_ean = {product.extraData["ean"]: product for product in existing_products}  # type: ignore [index]
        for product in existing_products:
            try:
                ean = product.extraData["ean"]  # type: ignore [index]
                stock_data = serialized_products_stocks[ean]
                created_offer = _create_offer_from_product(
                    venue,
                    product_by_ean[ean],
                    stock_data["id_at_provider"],
                    current_api_key.provider,
                )
                created_offers.append(created_offer)

            except offers_exceptions.OfferCreationBaseException as exc:
                logger.exception("Error while creating offer by ean", extra={"exc": exc})
                continue

        db.session.bulk_save_objects(created_offers)
        db.session.commit()

        reloaded_offers = _get_existing_offers(ean_list_to_create, venue, provider)
        for offer in reloaded_offers:
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
                creating_provider=current_api_key.provider,
            )
    for offer in offers_to_update:
        try:
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
        except offers_exceptions.OfferCreationBaseException:
            logger.exception("Error while creating offer by ean", extra={"exc": exc})
            continue

    search.async_index_offer_ids(offers_to_index)


def _get_existing_products(ean_to_create: set[str]) -> list[offers_models.Product]:
    allowed_product_subcategories = [
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        subcategories.LIVRE_PAPIER.id,
    ]
    return offers_models.Product.query.filter(
        offers_models.Product.extraData["ean"].astext.in_(ean_to_create),
        offers_models.Product.can_be_synchronized == True,
        offers_models.Product.subcategoryId.in_(allowed_product_subcategories),
    ).all()


def _get_existing_offers(
    ean_to_create_or_update: set[str],
    venue: offerers_models.Venue,
    provider: providers_models.Provider,
) -> list[offers_models.Offer]:
    return (
        utils.retrieve_offer_relations_query(offers_models.Offer.query)
        .filter(offers_models.Offer.isEvent == False)
        .filter(offers_models.Offer.venue == venue)
        .filter(offers_models.Offer.lastProvider == provider)  # pylint: disable=comparison-with-callable
        .filter(offers_models.Offer.extraData["ean"].astext.in_(ean_to_create_or_update))
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
            "id_at_provider": product.id_at_provider,
        }
    return stock_details


def _create_offer_from_product(
    venue: offerers_models.Venue,
    product: offers_models.Product,
    id_at_provider: str | None,
    provider: providers_models.Provider,
) -> offers_models.Offer:
    if product.extraData:
        offers_validation.check_ean_does_not_exist(product.extraData.get("ean"), venue)

    offer = offers_api.build_new_offer_from_product(venue, product, id_at_provider, provider.id)

    offer.audioDisabilityCompliant = venue.audioDisabilityCompliant
    offer.mentalDisabilityCompliant = venue.mentalDisabilityCompliant
    offer.motorDisabilityCompliant = venue.motorDisabilityCompliant
    offer.visualDisabilityCompliant = venue.visualDisabilityCompliant

    offer.isActive = True
    offer.lastValidationDate = datetime.datetime.utcnow()
    offer.lastValidationType = OfferValidationType.AUTO

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


@blueprint.v1_blueprint.route("/products/<int:product_id>", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_product_schema,
    tags=[constants.PRODUCT_OFFER_TAG],
    response_model=serialization.ProductOfferResponse,
)
@api_key_required
def get_product(product_id: int) -> serialization.ProductOfferResponse:
    """
    Get a product offer.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(product_id))
        .filter(sqla.not_(offers_models.Offer.isEvent))
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"product_id": ["The product offer could not be found"]}, status_code=404)

    return serialization.ProductOfferResponse.build_product_offer(offer)


@blueprint.v1_blueprint.route("/products/ean", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_product_schema,
    tags=[constants.PRODUCT_EAN_OFFER_TAG],
    response_model=serialization.ProductOffersByEanResponse,
)
@api_key_required
def get_product_by_ean(
    query: serialization.GetProductsListByEansQuery,
) -> serialization.ProductOffersByEanResponse:
    """
    Get bulk product offers using their European Article Number (EAN-13).
    """
    offers: list[offers_models.Offer] | None = (
        utils.retrieve_offer_relations_query(_retrieve_offer_by_eans_query(query.eans))  # type: ignore [arg-type]
        .filter(sqla.not_(offers_models.Offer.isEvent))
        .all()
    )

    if not offers:
        return serialization.ProductOffersByEanResponse(products=[])

    return serialization.ProductOffersByEanResponse(
        products=[serialization.ProductOfferResponse.build_product_offer(offer) for offer in offers]
    )


@blueprint.v1_blueprint.route("/products", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_product_schema,
    tags=[constants.PRODUCT_OFFER_TAG],
    response_model=serialization.ProductOffersResponse,
)
@api_key_required
def get_products(
    query: serialization.GetOffersQueryParams,
) -> serialization.ProductOffersResponse:
    """
    Get products. Results are paginated.
    """
    utils.check_venue_id_is_tied_to_api_key(query.venue_id)
    total_offer_ids = utils.retrieve_offer_ids(is_event=False, filtered_venue_id=query.venue_id)
    offset = query.limit * (query.page - 1)

    if offset > len(total_offer_ids):
        raise api_errors.ApiErrors(
            {
                "page": f"The page you requested does not exist. The maximum page for the specified limit is {len(total_offer_ids)//query.limit+1}"
            },
            status_code=404,
        )

    offers = (
        utils.retrieve_offer_relations_query(
            offers_models.Offer.query.filter(offers_models.Offer.id.in_(total_offer_ids[offset : offset + query.limit]))
        )
        .order_by(offers_models.Offer.id)
        .all()
    )

    return serialization.ProductOffersResponse(
        products=[serialization.ProductOfferResponse.build_product_offer(offer) for offer in offers],
        pagination=serialization.Pagination.build_pagination(
            flask.url_for(".get_products", _external=True),
            query.page,
            len(offers),
            len(total_offer_ids),
            query.limit,
            query.venue_id,
        ),
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


@blueprint.v1_blueprint.route("/products/<int:product_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprint.v1_product_schema,
    tags=[constants.PRODUCT_OFFER_TAG],
    response_model=serialization.ProductOfferResponse,
)
@api_key_required
def edit_product(product_id: int, body: serialization.ProductOfferEdition) -> serialization.ProductOfferResponse:
    """
    Edit a book, CD or vinyl product.

    Leave fields undefined to keep their current value.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(product_id))
        .filter(sqla.not_(offers_models.Offer.isEvent))
        .one_or_none()
    )

    if not offer:
        raise api_errors.ApiErrors({"product_id": ["The product offer could not be found"]}, status_code=404)

    _check_offer_can_be_edited(offer)
    utils.check_offer_subcategory(body, offer.subcategoryId)

    update_body = body.dict(exclude_unset=True)
    try:
        with repository.transaction():
            offers_api.update_offer(
                offer,
                bookingEmail=update_body.get("booking_email", offers_api.UNCHANGED),
                extraData=serialization.deserialize_extra_data(
                    body.category_related_fields, copy.deepcopy(offer.extraData)
                )
                if body.category_related_fields
                else offers_api.UNCHANGED,
                isActive=update_body.get("is_active", offers_api.UNCHANGED),
                isDuo=update_body.get("is_duo", offers_api.UNCHANGED),
                withdrawalDetails=update_body.get("withdrawal_details", offers_api.UNCHANGED),
                **utils.compute_accessibility_edition_fields(update_body.get("accessibility")),
            )
            if "stock" in update_body:
                _upsert_product_stock(offer, body.stock, current_api_key.provider)
    except offers_exceptions.OfferCreationBaseException as e:
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
    quantity = stock_update_body.get("quantity", offers_api.UNCHANGED)
    offers_api.edit_stock(
        existing_stock,
        quantity=serialization.deserialize_quantity(quantity),
        price=finance_utils.to_euros(price) if price != offers_api.UNCHANGED else offers_api.UNCHANGED,
        booking_limit_datetime=stock_update_body.get("booking_limit_datetime", offers_api.UNCHANGED),
        editing_provider=provider,
    )
