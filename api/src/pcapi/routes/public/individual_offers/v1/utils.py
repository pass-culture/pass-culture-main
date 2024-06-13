import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.core.providers import models as providers_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.routes.public import utils as public_utils
from pcapi.utils import image_conversion
from pcapi.validation.routes.users_authentifications import current_api_key

from . import constants
from . import serialization


def retrieve_venue_from_location(
    location: serialization.DigitalLocation | serialization.PhysicalLocation,
) -> offerers_models.Venue:
    venue = (
        offerers_models.Venue.query.join(providers_models.VenueProvider, offerers_models.Venue.venueProviders)
        .filter(
            offerers_models.Venue.id == location.venue_id,
            providers_models.VenueProvider.provider == current_api_key.provider,
            providers_models.VenueProvider.isActive,
        )
        .options(sqla.orm.joinedload(offerers_models.Venue.offererAddress))
        .one_or_none()
    )
    if not venue:
        raise api_errors.ApiErrors(
            {"venueId": ["There is no venue with this id associated to your API key"]}, status_code=404
        )
    return venue


def retrieve_offer_relations_query(query: sqla_orm.Query) -> sqla_orm.Query:
    return (
        query.options(sqla_orm.joinedload(offers_models.Offer.stocks))
        .options(sqla_orm.joinedload(offers_models.Offer.mediations))
        .options(
            sqla_orm.joinedload(offers_models.Offer.product)
            .load_only(offers_models.Product.id, offers_models.Product.thumbCount)
            .joinedload(offers_models.Product.productMediations)
        )
        .options(
            sqla_orm.joinedload(offers_models.Offer.priceCategories).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
    )


def check_venue_id_is_tied_to_api_key(venue_id: int | None) -> None:
    if venue_id is None:
        return

    is_venue_tied_to_api_key = db.session.query(
        providers_models.VenueProvider.query.filter(
            providers_models.VenueProvider.provider == current_api_key.provider,
            providers_models.VenueProvider.venueId == venue_id,
            providers_models.VenueProvider.isActive,
        ).exists()
    ).scalar()
    if not is_venue_tied_to_api_key:
        raise api_errors.ApiErrors({"venue_id": ["The venue could not be found"]}, status_code=404)


def compute_accessibility_edition_fields(accessibility_payload: dict | None) -> dict:
    if not accessibility_payload:
        return {}
    return {
        "audioDisabilityCompliant": accessibility_payload.get("audio_disability_compliant", offers_api.UNCHANGED),
        "mentalDisabilityCompliant": accessibility_payload.get("mental_disability_compliant", offers_api.UNCHANGED),
        "motorDisabilityCompliant": accessibility_payload.get("motor_disability_compliant", offers_api.UNCHANGED),
        "visualDisabilityCompliant": accessibility_payload.get("visual_disability_compliant", offers_api.UNCHANGED),
    }


def check_offer_subcategory(
    body: serialization.ProductOfferEdition | serialization.EventOfferEdition, offer_subcategory_id: str
) -> None:
    if body.category_related_fields is not None and (
        body.category_related_fields.subcategory_id != offer_subcategory_id
    ):
        raise api_errors.ApiErrors({"categoryRelatedFields.category": ["The category cannot be changed"]})


def retrieve_offer_query(offer_id: int) -> sqla_orm.Query:
    return _retrieve_offer_tied_to_user_query().filter(offers_models.Offer.id == offer_id)


def _retrieve_offer_tied_to_user_query() -> sqla_orm.Query:
    return (
        offers_models.Offer.query.join(offerers_models.Venue)
        .join(offerers_models.Venue.venueProviders)
        .join(providers_models.VenueProvider.provider)
        .filter(providers_models.VenueProvider.provider == current_api_key.provider)
        .filter(providers_models.VenueProvider.isActive)
    )


def retrieve_offers(
    is_event: bool, firstIndex: int, filtered_venue_id: int, ids_at_provider: list[str] | None
) -> sqla_orm.Query:
    offers_query = (
        offers_models.Offer.query.join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.provider == current_api_key.provider)
        .filter(offers_models.Offer.venueId == filtered_venue_id)
        .filter(offers_models.Offer.isEvent == is_event)
        .filter(offers_models.Offer.id >= firstIndex)
        .order_by(offers_models.Offer.id)
    )

    if ids_at_provider:
        offers_query = offers_query.filter(offers_models.Offer.idAtProvider.in_(ids_at_provider))

    return retrieve_offer_relations_query(offers_query)


def save_image(image_body: serialization.ImageBody, offer: offers_models.Offer) -> None:
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
            min_width=constants.MIN_IMAGE_WIDTH,
            min_height=constants.MIN_IMAGE_HEIGHT,
            max_width=constants.MAX_IMAGE_WIDTH,
            max_height=constants.MAX_IMAGE_HEIGHT,
            aspect_ratio=constants.ASPECT_RATIO,
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
        raise api_errors.ApiErrors(errors={"imageFile": message})
    except image_conversion.ImageRatioError as error:
        raise api_errors.ApiErrors(
            errors={"imageFile": f"Bad image ratio: expected {str(error.expected)[:4]}, found {str(error.found)[:4]}"}
        )


def get_event_with_details(event_id: int) -> offers_models.Offer | None:
    return (
        retrieve_offer_query(event_id)
        .filter(offers_models.Offer.isEvent)
        .outerjoin(offers_models.Offer.stocks.and_(sqla.not_(offers_models.Stock.isEventExpired)))
        .options(sqla.orm.contains_eager(offers_models.Offer.stocks))
        .options(
            sqla.orm.joinedload(offers_models.Offer.priceCategories).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
        .one_or_none()
    )


def get_price_category_from_event(
    event: offers_models.Offer, price_category_id: int
) -> offers_models.PriceCategory | None:
    try:
        return next(cat for cat in event.priceCategories if cat.id == price_category_id)
    except StopIteration:
        return None
