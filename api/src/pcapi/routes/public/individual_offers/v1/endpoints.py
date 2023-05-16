import copy
import itertools
import logging

import flask
from sqlalchemy import orm as sqla_orm

from pcapi import repository
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.external.attributes import api as attributes_api
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.core.providers import models as providers_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.routes.public import utils as public_utils
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import image_conversion
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key

from . import blueprint
from . import serialization


logger = logging.getLogger(__name__)

PRODUCT_OFFER_TAG = "Product offer"
PRODUCT_EAN_OFFER_TAG = "Bulk product offer operation"
EVENT_OFFER_INFO_TAG = "Event offer main information (except prices and dates)"
EVENT_OFFER_PRICES_TAG = "Event offer prices"
EVENT_OFFER_DATES_TAG = "Event offer dates"
OFFERER_VENUES_TAG = "Offerer and Venues"

MIN_IMAGE_WIDTH = 400
MAX_IMAGE_WIDTH = 800
MIN_IMAGE_HEIGHT = 600
MAX_IMAGE_HEIGHT = 1200
ASPECT_RATIO = image_conversion.ImageRatio.PORTRAIT


@blueprint.v1_blueprint.route("/offerer_venues", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_product_schema, tags=[OFFERER_VENUES_TAG], response_model=serialization.GetOfferersVenuesResponse
)
@api_key_required
def get_offerer_venues(query: serialization.GetOfferersVenuesQuery) -> serialization.GetOfferersVenuesResponse:
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


def _retrieve_venue_from_location(
    location: serialization.DigitalLocation | serialization.PhysicalLocation,
) -> offerers_models.Venue:
    venue = (
        offerers_models.Venue.query.join(providers_models.VenueProvider, offerers_models.Venue.venueProviders)
        .filter(
            offerers_models.Venue.id == location.venue_id,
            providers_models.VenueProvider.provider == current_api_key.provider,
        )
        .one_or_none()
    )
    if not venue:
        raise api_errors.ApiErrors(
            {"venueId": ["There is no venue with this id associated to your API key"]}, status_code=404
        )
    return venue


def _retrieve_offer_tied_to_user_query() -> sqla_orm.Query:
    return (
        offers_models.Offer.query.join(offerers_models.Venue)
        .join(offerers_models.Venue.venueProviders, providers_models.VenueProvider.provider)
        .filter(providers_models.VenueProvider.provider == current_api_key.provider)
    )


def _retrieve_offer_query(offer_id: int) -> sqla_orm.Query:
    return _retrieve_offer_tied_to_user_query().filter(offers_models.Offer.id == offer_id)


def _retrieve_offer_by_ean_query(ean: str) -> sqla_orm.Query:
    return (
        _retrieve_offer_tied_to_user_query()
        .filter(offers_models.Offer.extraData["ean"].astext == ean)
        .order_by(offers_models.Offer.id.desc())
    )


def _retrieve_offer_relations_query(query: sqla_orm.Query) -> sqla_orm.Query:
    return (
        query.options(sqla_orm.joinedload(offers_models.Offer.stocks))
        .options(sqla_orm.joinedload(offers_models.Offer.mediations))
        .options(
            sqla_orm.joinedload(offers_models.Offer.product).load_only(
                offers_models.Product.id, offers_models.Product.thumbCount
            )
        )
        .options(
            sqla_orm.joinedload(offers_models.Offer.priceCategories).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
    )


def _check_venue_id_is_tied_to_api_key(venue_id: int | None) -> None:
    if venue_id is None:
        return

    is_venue_tied_to_api_key = db.session.query(
        providers_models.VenueProvider.query.filter(
            providers_models.VenueProvider.provider == current_api_key.provider,
            providers_models.VenueProvider.venueId == venue_id,
        ).exists()
    ).scalar()
    if not is_venue_tied_to_api_key:
        raise api_errors.ApiErrors({"venue_id": ["The venue could not be found"]}, status_code=404)


def _retrieve_offer_ids(is_event: bool, filtered_venue_id: int | None) -> list[int]:
    offer_ids_query = (
        offers_models.Offer.query.join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.provider == current_api_key.provider)
        .filter(offers_models.Offer.isEvent == is_event)
        .with_entities(offers_models.Offer.id)
        .order_by(offers_models.Offer.id)
    )
    if filtered_venue_id is not None:
        offer_ids_query = offer_ids_query.filter(offers_models.Offer.venueId == filtered_venue_id)

    return [offer_id for offer_id, in offer_ids_query.all()]


def _save_image(image_body: serialization.ImageBody, offer: offers_models.Offer) -> None:
    try:
        image_as_bytes = public_utils.get_bytes_from_base64_string(image_body.file)
    except public_utils.InvalidBase64Exception:
        raise api_errors.ApiErrors(errors={"imageFile": ["The value must be a valid base64 string."]})
    try:
        offers_api.create_mediation(
            user=None,
            offer=offer,
            credit=image_body.credit,
            image_as_bytes=image_as_bytes,
            min_width=MIN_IMAGE_WIDTH,
            min_height=MIN_IMAGE_HEIGHT,
            max_width=MAX_IMAGE_WIDTH,
            max_height=MAX_IMAGE_HEIGHT,
            aspect_ratio=ASPECT_RATIO,
        )
    except offers_exceptions.ImageValidationError as error:
        if isinstance(error, offers_exceptions.ImageTooSmall):
            message = f"The image is too small. It must be above {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT} pixels."
        elif isinstance(error, offers_exceptions.ImageTooLarge):
            message = f"The image is too large. It must be below {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT} pixels."
        elif isinstance(error, offers_exceptions.UnacceptedFileType):
            message = f"The image format is not accepted. It must be in {offers_validation.ACCEPTED_THUMBNAIL_FORMATS}."
        elif isinstance(error, offers_exceptions.UnidentifiedImage):
            message = "The file is not a valid image."
        elif isinstance(error, offers_exceptions.FileSizeExceeded):
            message = f"The file is too large. It must be less than {offers_validation.MAX_THUMBNAIL_SIZE} bytes."
        else:
            message = "The image is not valid."
        raise api_errors.ApiErrors(errors={"imageFile": message})
    except image_conversion.ImageRatioError as error:
        raise api_errors.ApiErrors(
            errors={"imageFile": f"Bad image ratio: expected {str(error.expected)[:4]}, found {str(error.found)[:4]}"}
        )


@blueprint.v1_blueprint.route("/products", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_product_schema, tags=[PRODUCT_OFFER_TAG], response_model=serialization.ProductOfferResponse
)
@api_key_required
def post_product_offer(body: serialization.ProductOfferCreation) -> serialization.ProductOfferResponse:
    """
    Create a CD or vinyl product.
    """
    venue = _retrieve_venue_from_location(body.location)

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
                _save_image(body.image, created_offer)

            offers_api.publish_offer(created_offer, user=None)

    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.ProductOfferResponse.build_product_offer(created_offer)


@blueprint.v1_blueprint.route("/products/ean", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_product_schema, tags=[PRODUCT_EAN_OFFER_TAG], response_model=serialization.ProductOfferResponse
)
@api_key_required
def post_product_offer_by_ean(body: serialization.ProductOfferByEanCreation) -> serialization.ProductOfferResponse:
    """
    Create a product offer using its European Article Number (EAN-13).
    """
    allowed_product_subcategories = [subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id, subcategories.LIVRE_PAPIER.id]
    product = offers_models.Product.query.filter(
        offers_models.Product.extraData["ean"].astext == body.ean,
        offers_models.Product.subcategoryId.in_(allowed_product_subcategories),
    ).one_or_none()
    if not product:
        raise api_errors.ApiErrors({"ean": ["The product is not present in pass Culture's database"]}, status_code=404)

    venue = _retrieve_venue_from_location(body.location)
    try:
        with repository.transaction():
            created_offer = _create_offer_from_product(
                venue,
                product,
                body.id_at_provider,
                current_api_key.provider.id,
                body.accessibility,
            )

            if body.stock:
                offers_api.create_stock(
                    offer=created_offer,
                    price=finance_utils.to_euros(body.stock.price),
                    quantity=serialization.deserialize_quantity(body.stock.quantity),
                    booking_limit_datetime=body.stock.booking_limit_datetime,
                    creating_provider=current_api_key.provider,
                )

            offers_api.publish_offer(created_offer, user=None)

    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.ProductOfferResponse.build_product_offer(created_offer)


def _create_offer_from_product(
    venue: offerers_models.Venue,
    product: offers_models.Product,
    id_at_provider: str | None,
    provider_id: int | None,
    accessibility: serialization.Accessibility | None,
) -> offers_models.Offer:
    if venue.isVirtual and accessibility is None:
        raise api_errors.ApiErrors(
            {"accessibility": ["The accessibility is required when the location type is digital"]}
        )

    if product.extraData:
        offers_validation.check_isbn_or_ean_does_not_exist(
            product.extraData.get("ean"), product.extraData.get("isbn"), venue
        )

    offer = offers_api.build_new_offer_from_product(venue, product, id_at_provider, provider_id)
    if accessibility:
        offer.audioDisabilityCompliant = accessibility.audio_disability_compliant
        offer.mentalDisabilityCompliant = accessibility.mental_disability_compliant
        offer.motorDisabilityCompliant = accessibility.motor_disability_compliant
        offer.visualDisabilityCompliant = accessibility.visual_disability_compliant
    else:
        offer.audioDisabilityCompliant = venue.audioDisabilityCompliant
        offer.mentalDisabilityCompliant = venue.mentalDisabilityCompliant
        offer.motorDisabilityCompliant = venue.motorDisabilityCompliant
        offer.visualDisabilityCompliant = venue.visualDisabilityCompliant

    repository.repository.add_to_session(offer)
    db.session.flush()

    logger.info(
        "models.Offer has been created",
        extra={"offer_id": offer.id, "venue_id": venue.id, "product_id": offer.productId},
        technical_message_id="offer.created",
    )

    attributes_api.update_external_pro(venue.bookingEmail)

    return offer


def _deserialize_ticket_collection(
    ticket_collection: serialization.SentByEmailDetails | serialization.OnSiteCollectionDetails | None,
    subcategory_id: str,
) -> tuple[offers_models.WithdrawalTypeEnum | None, int | None]:
    if not ticket_collection:
        if subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id].can_be_withdrawable:
            return offers_models.WithdrawalTypeEnum.NO_TICKET, None
        return None, None
    if isinstance(ticket_collection, serialization.SentByEmailDetails):
        return offers_models.WithdrawalTypeEnum.BY_EMAIL, ticket_collection.daysBeforeEvent * 24 * 3600
    return offers_models.WithdrawalTypeEnum.ON_SITE, ticket_collection.minutesBeforeEvent * 60


@blueprint.v1_blueprint.route("/events", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[EVENT_OFFER_INFO_TAG], response_model=serialization.EventOfferResponse
)
@api_key_required
def post_event_offer(body: serialization.EventOfferCreation) -> serialization.EventOfferResponse:
    """
    Post an event offer.
    """
    venue = _retrieve_venue_from_location(body.location)
    withdrawal_type, withdrawal_delay = _deserialize_ticket_collection(
        body.ticket_collection, body.category_related_fields.subcategory_id
    )
    try:
        with repository.transaction():
            created_offer = offers_api.create_offer(
                audio_disability_compliant=body.accessibility.audio_disability_compliant,
                booking_email=body.booking_email,
                description=body.description,
                duration_minutes=body.duration_minutes,
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
                withdrawal_delay=withdrawal_delay,
                withdrawal_details=body.withdrawal_details,
                withdrawal_type=withdrawal_type,
            )
            # To create the priceCategories, the offer needs to have an id
            db.session.flush()

            price_categories = body.price_categories or []
            for price_category in price_categories:
                euro_price = finance_utils.to_euros(price_category.price)
                offers_api.create_price_category(created_offer, price_category.label, euro_price)

            if body.image:
                _save_image(body.image, created_offer)

            offers_api.publish_offer(created_offer, user=None)

    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.EventOfferResponse.build_event_offer(created_offer)


@blueprint.v1_blueprint.route("/events/<int:event_id>/price_categories", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[EVENT_OFFER_PRICES_TAG], response_model=serialization.PriceCategoriesResponse
)
@api_key_required
def post_event_price_categories(
    event_id: int, body: serialization.PriceCategoriesCreation
) -> serialization.PriceCategoriesResponse:
    """
    Post price categories.
    """
    offer = _retrieve_offer_query(event_id).filter(offers_models.Offer.isEvent == True).one_or_none()
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    created_price_categories: list[offers_models.PriceCategory] = []
    with repository.transaction():
        for price_category in body.price_categories:
            euro_price = finance_utils.to_euros(price_category.price)
            created_price_categories.append(offers_api.create_price_category(offer, price_category.label, euro_price))

    return serialization.PriceCategoriesResponse.build_price_categories(created_price_categories)


@blueprint.v1_blueprint.route("/events/<int:event_id>/dates", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[EVENT_OFFER_DATES_TAG], response_model=serialization.PostDatesResponse
)
@api_key_required
def post_event_dates(event_id: int, body: serialization.DatesCreation) -> serialization.PostDatesResponse:
    """
    Add dates to an event offer.
    Each date is attached to a price category so if there are several prices categories, several dates must be added.
    """
    offer = (
        _retrieve_offer_query(event_id)
        .options(sqla_orm.joinedload(offers_models.Offer.priceCategories))
        .filter(offers_models.Offer.isEvent == True)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    new_dates: list[offers_models.Stock] = []
    try:
        with repository.transaction():
            for date in body.dates:
                price_category = next((c for c in offer.priceCategories if c.id == date.price_category_id), None)
                if not price_category:
                    raise api_errors.ApiErrors(
                        {"price_category_id": ["The price category could not be found"]}, status_code=404
                    )

                new_dates.append(
                    offers_api.create_stock(
                        offer=offer,
                        price_category=price_category,
                        quantity=serialization.deserialize_quantity(date.quantity),
                        beginning_datetime=date.beginning_datetime,
                        booking_limit_datetime=date.booking_limit_datetime,
                        creating_provider=current_api_key.provider,
                    )
                )
    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.PostDatesResponse(
        dates=[serialization.DateResponse.build_date(new_date) for new_date in new_dates]
    )


@blueprint.v1_blueprint.route("/products/<int:product_id>", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_product_schema, tags=[PRODUCT_OFFER_TAG], response_model=serialization.ProductOfferResponse
)
@api_key_required
def get_product(product_id: int) -> serialization.ProductOfferResponse:
    """
    Get a product offer.
    """
    offer: offers_models.Offer | None = (
        _retrieve_offer_relations_query(_retrieve_offer_query(product_id))
        .filter(offers_models.Offer.isEvent == False)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"product_id": ["The product offer could not be found"]}, status_code=404)

    return serialization.ProductOfferResponse.build_product_offer(offer)


@blueprint.v1_blueprint.route("/products/ean/<string:ean>", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_product_schema, tags=[PRODUCT_EAN_OFFER_TAG], response_model=serialization.ProductOfferResponse
)
@api_key_required
def get_product_by_ean(ean: str) -> serialization.ProductOfferResponse:
    """
    Get a product offer using its European Article Number (EAN-13).
    """
    if len(ean) != 13:
        raise api_errors.ApiErrors({"ean": ["Only 13 characters EAN are accepted"]})

    offer: offers_models.Offer | None = (
        _retrieve_offer_relations_query(_retrieve_offer_by_ean_query(ean))
        .filter(offers_models.Offer.isEvent == False)
        .first()
    )
    if not offer:
        raise api_errors.ApiErrors({"ean": ["The product offer could not be found"]}, status_code=404)

    return serialization.ProductOfferResponse.build_product_offer(offer)


@blueprint.v1_blueprint.route("/products", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_product_schema, tags=[PRODUCT_OFFER_TAG], response_model=serialization.ProductOffersResponse
)
@api_key_required
def get_products(query: serialization.GetOffersQueryParams) -> serialization.ProductOffersResponse:
    """
    Get products. Results are paginated.
    """
    _check_venue_id_is_tied_to_api_key(query.venue_id)
    total_offer_ids = _retrieve_offer_ids(is_event=False, filtered_venue_id=query.venue_id)
    offset = query.limit * (query.page - 1)

    if offset > len(total_offer_ids):
        raise api_errors.ApiErrors(
            {
                "page": f"The page you requested does not exist. The maximum page for the specified limit is {len(total_offer_ids)//query.limit+1}"
            },
            status_code=404,
        )

    offers = (
        _retrieve_offer_relations_query(
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


@blueprint.v1_blueprint.route("/events/<int:event_id>", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[EVENT_OFFER_INFO_TAG], response_model=serialization.EventOfferResponse
)
@api_key_required
def get_event(event_id: int) -> serialization.EventOfferResponse:
    """
    Get an event offer.
    """
    offer: offers_models.Offer | None = (
        _retrieve_offer_relations_query(_retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent == True)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event offer could not be found"]}, status_code=404)

    return serialization.EventOfferResponse.build_event_offer(offer)


@blueprint.v1_blueprint.route("/events/<int:event_id>/dates", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[EVENT_OFFER_DATES_TAG], response_model=serialization.GetDatesResponse
)
@api_key_required
def get_event_dates(event_id: int, query: serialization.GetDatesQueryParams) -> serialization.GetDatesResponse:
    """
    Get dates of an event. Results are paginated.
    """
    offer = _retrieve_offer_query(event_id).filter(offers_models.Offer.isEvent == True).one_or_none()
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    stock_id_query = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offer.id, offers_models.Stock.isSoftDeleted == False
    ).with_entities(offers_models.Stock.id)
    total_stock_ids = [stock_id for (stock_id,) in stock_id_query.all()]

    offset = query.limit * (query.page - 1)
    if offset > len(total_stock_ids):
        raise api_errors.ApiErrors(
            {
                "page": f"The page you requested does not exist. The maximum page for the specified limit is {len(total_stock_ids)//query.limit+1}"
            },
            status_code=404,
        )

    stocks = (
        offers_models.Stock.query.filter(offers_models.Stock.id.in_(total_stock_ids[offset : offset + query.limit]))
        .options(
            sqla_orm.joinedload(offers_models.Stock.priceCategory).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
        .order_by(offers_models.Stock.id)
        .all()
    )

    return serialization.GetDatesResponse(
        dates=[serialization.DateResponse.build_date(stock) for stock in stocks],
        pagination=serialization.Pagination.build_pagination(
            flask.url_for(".get_event_dates", event_id=event_id, _external=True),
            query.page,
            len(stocks),
            len(total_stock_ids),
            query.limit,
        ),
    )


@blueprint.v1_blueprint.route("/events", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[EVENT_OFFER_INFO_TAG], response_model=serialization.EventOffersResponse
)
@api_key_required
def get_events(query: serialization.GetOffersQueryParams) -> serialization.EventOffersResponse:
    """
    Get events. Results are paginated.
    """
    _check_venue_id_is_tied_to_api_key(query.venue_id)
    total_offer_ids = _retrieve_offer_ids(is_event=True, filtered_venue_id=query.venue_id)
    offset = query.limit * (query.page - 1)

    if offset > len(total_offer_ids):
        raise api_errors.ApiErrors(
            {
                "page": f"The page you requested does not exist. The maximum page for the specified limit is {len(total_offer_ids)//query.limit+1}"
            },
            status_code=404,
        )

    offers = (
        _retrieve_offer_relations_query(
            offers_models.Offer.query.filter(offers_models.Offer.id.in_(total_offer_ids[offset : offset + query.limit]))
        )
        .order_by(offers_models.Offer.id)
        .all()
    )

    return serialization.EventOffersResponse(
        events=[serialization.EventOfferResponse.build_event_offer(offer) for offer in offers],
        pagination=serialization.Pagination.build_pagination(
            flask.url_for(".get_events", _external=True),
            query.page,
            len(offers),
            len(total_offer_ids),
            query.limit,
            query.venue_id,
        ),
    )


def compute_accessibility_edition_fields(accessibility_payload: dict | None) -> dict:
    if not accessibility_payload:
        return {}
    return {
        "audioDisabilityCompliant": accessibility_payload.get("audio_disability_compliant", offers_api.UNCHANGED),
        "mentalDisabilityCompliant": accessibility_payload.get("mental_disability_compliant", offers_api.UNCHANGED),
        "motorDisabilityCompliant": accessibility_payload.get("motor_disability_compliant", offers_api.UNCHANGED),
        "visualDisabilityCompliant": accessibility_payload.get("visual_disability_compliant", offers_api.UNCHANGED),
    }


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


def _check_offer_subcategory(
    body: serialization.ProductOfferEdition | serialization.EventOfferEdition, offer_subcategory_id: str
) -> None:
    if body.category_related_fields is not None and (
        body.category_related_fields.subcategory_id != offer_subcategory_id
    ):
        raise api_errors.ApiErrors({"categoryRelatedFields.category": ["The category cannot be changed"]})


@blueprint.v1_blueprint.route("/products/<int:product_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprint.v1_product_schema, tags=[PRODUCT_OFFER_TAG], response_model=serialization.ProductOfferResponse
)
@api_key_required
def edit_product(product_id: int, body: serialization.ProductOfferEdition) -> serialization.ProductOfferResponse:
    """
    Edit a CD or vinyl product.

    Leave fields undefined to keep their current value.
    """
    offer: offers_models.Offer | None = (
        _retrieve_offer_relations_query(_retrieve_offer_query(product_id))
        .filter(offers_models.Offer.isEvent == False)
        .one_or_none()
    )

    if not offer:
        raise api_errors.ApiErrors({"product_id": ["The product offer could not be found"]}, status_code=404)

    _check_offer_can_be_edited(offer)
    _check_offer_subcategory(body, offer.subcategoryId)

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
                **compute_accessibility_edition_fields(update_body.get("accessibility")),
            )
            if "stock" in update_body:
                _upsert_product_stock(offer, body.stock, current_api_key.provider)
    except offers_exceptions.OfferCreationBaseException as e:
        raise api_errors.ApiErrors(e.errors, status_code=400)

    return serialization.ProductOfferResponse.build_product_offer(offer)


@blueprint.v1_blueprint.route("/products/ean/<string:ean>", methods=["PATCH"])
@spectree_serialize(
    api=blueprint.v1_product_schema, tags=[PRODUCT_EAN_OFFER_TAG], response_model=serialization.ProductOfferResponse
)
@api_key_required
def edit_product_by_ean(ean: str, body: serialization.ProductOfferByEanEdition) -> serialization.ProductOfferResponse:
    """
    Edit a product by accessing it through its European Article Number (EAN-13).

    Leave fields undefined to keep their current value.
    """
    if len(ean) != 13:
        raise api_errors.ApiErrors({"ean": ["Only 13 characters EAN are accepted"]})

    offer: offers_models.Offer | None = (
        _retrieve_offer_relations_query(_retrieve_offer_by_ean_query(ean))
        .filter(offers_models.Offer.isEvent == False)
        .first()
    )
    if not offer:
        raise api_errors.ApiErrors({"ean": ["The product offer could not be found"]}, status_code=404)

    try:
        with repository.transaction():
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


@blueprint.v1_blueprint.route("/events/<int:event_id>/dates/<int:date_id>", methods=["DELETE"])
@spectree_serialize(api=blueprint.v1_event_schema, tags=[EVENT_OFFER_DATES_TAG], on_success_status=204)
@api_key_required
def delete_event_date(event_id: int, date_id: int) -> None:
    """
    Delete an event date.

    All cancellable bookings (i.e not used) will be cancelled. To prevent from further bookings, you may alternatively update the date's quantity to the bookedQuantity (but not below).
    """
    offer = (
        _retrieve_offer_query(event_id)
        .filter(offers_models.Offer.isEvent == True)
        .options(sqla_orm.joinedload(offers_models.Offer.stocks))
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)
    stock_to_delete = next((stock for stock in offer.stocks if stock.id == date_id and not stock.isSoftDeleted), None)
    if not stock_to_delete:
        raise api_errors.ApiErrors({"date_id": ["The date could not be found"]}, status_code=404)

    offers_api.delete_stock(stock_to_delete)


@blueprint.v1_blueprint.route("/events/<int:event_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[EVENT_OFFER_INFO_TAG], response_model=serialization.EventOfferResponse
)
@api_key_required
def edit_event(event_id: int, body: serialization.EventOfferEdition) -> serialization.EventOfferResponse:
    """
    Edit a event offer.

    Leave fields undefined to keep their current value.
    """
    offer: offers_models.Offer | None = (
        _retrieve_offer_relations_query(_retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent == True)
        .one_or_none()
    )

    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event offer could not be found"]}, status_code=404)
    _check_offer_subcategory(body, offer.subcategoryId)

    update_body = body.dict(exclude_unset=True)

    withdrawal_type, withdrawal_delay = (
        _deserialize_ticket_collection(body.ticket_collection, offer.subcategoryId)
        if update_body.get("ticket_collection")
        else (offers_api.UNCHANGED, offers_api.UNCHANGED)
    )

    try:
        with repository.transaction():
            offer = offers_api.update_offer(
                offer,
                bookingEmail=update_body.get("booking_email", offers_api.UNCHANGED),
                durationMinutes=update_body.get("duration_minutes", offers_api.UNCHANGED),
                extraData=serialization.deserialize_extra_data(
                    body.category_related_fields, copy.deepcopy(offer.extraData)
                )
                if body.category_related_fields
                else offers_api.UNCHANGED,
                isActive=update_body.get("is_active", offers_api.UNCHANGED),
                isDuo=update_body.get("is_duo", offers_api.UNCHANGED),
                withdrawalDetails=update_body.get("withdrawal_details", offers_api.UNCHANGED),
                withdrawalType=withdrawal_type,
                withdrawalDelay=withdrawal_delay,
                **compute_accessibility_edition_fields(update_body.get("accessibility")),
            )
    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.EventOfferResponse.build_event_offer(offer)


@blueprint.v1_blueprint.route("/events/<int:event_id>/price_categories/<int:price_category_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[EVENT_OFFER_PRICES_TAG], response_model=serialization.PriceCategoryResponse
)
@api_key_required
def patch_event_price_categories(
    event_id: int,
    price_category_id: int,
    body: serialization.PriceCategoryEdition,
) -> serialization.PriceCategoryResponse:
    """
    Patch price categories.
    """
    event_offer = (
        _retrieve_offer_query(event_id)
        .filter(offers_models.Offer.isEvent == True)
        .outerjoin(offers_models.Offer.stocks.and_(offers_models.Stock.isEventExpired == False))
        .options(sqla_orm.contains_eager(offers_models.Offer.stocks))
        .options(
            sqla_orm.joinedload(offers_models.Offer.priceCategories).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
        .one_or_none()
    )
    if not event_offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    price_category_to_edit = next(
        (price_category for price_category in event_offer.priceCategories if price_category.id == price_category_id)
    )
    if not price_category_to_edit:
        raise api_errors.ApiErrors({"price_category_id": ["No price category could be found"]}, status_code=404)

    update_body = body.dict(exclude_unset=True)
    with repository.transaction():
        eurocent_price = update_body.get("price", offers_api.UNCHANGED)
        offers_api.edit_price_category(
            event_offer,
            price_category=price_category_to_edit,
            label=update_body.get("label", offers_api.UNCHANGED),
            price=finance_utils.to_euros(eurocent_price)
            if eurocent_price != offers_api.UNCHANGED
            else offers_api.UNCHANGED,
            editing_provider=current_api_key.provider,
        )

    return serialization.PriceCategoryResponse.from_orm(price_category_to_edit)


@blueprint.v1_blueprint.route("/events/<int:event_id>/dates/<int:date_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[EVENT_OFFER_DATES_TAG], response_model=serialization.DateResponse
)
@api_key_required
def patch_event_date(
    event_id: int,
    date_id: int,
    body: serialization.DateEdition,
) -> serialization.DateResponse:
    """
    Patch an event date.
    """
    offer: offers_models.Offer | None = (
        _retrieve_offer_relations_query(_retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent == True)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    stock_to_edit = next((stock for stock in offer.stocks if stock.id == date_id and not stock.isSoftDeleted), None)
    if not stock_to_edit:
        raise api_errors.ApiErrors({"date_id": ["No date could be found"]}, status_code=404)

    update_body = body.dict(exclude_unset=True)
    try:
        with repository.transaction():
            price_category_id = update_body.get("price_category_id", None)
            price_category = (
                next((c for c in offer.priceCategories if c.id == price_category_id), None)
                if price_category_id is not None
                else offers_api.UNCHANGED
            )
            if not price_category:
                raise api_errors.ApiErrors(
                    {"price_category_id": ["The price category could not be found"]}, status_code=404
                )

            quantity = update_body.get("quantity", offers_api.UNCHANGED)
            edited_date, _ = offers_api.edit_stock(
                stock_to_edit,
                quantity=serialization.deserialize_quantity(quantity),
                price_category=price_category,
                booking_limit_datetime=update_body.get("booking_limit_datetime", offers_api.UNCHANGED),
                beginning_datetime=update_body.get("beginning_datetime", offers_api.UNCHANGED),
                editing_provider=current_api_key.provider,
            )
    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)
    return serialization.DateResponse.build_date(edited_date)
