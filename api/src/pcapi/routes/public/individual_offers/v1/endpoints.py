import logging

from pcapi import repository
from pcapi import settings
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.models import api_errors
from pcapi.routes.public import utils as public_utils
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import image_conversion
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key

from . import blueprint
from . import serialization


logger = logging.getLogger(__name__)

PRODUCT_OFFERS_TAG = "Product offers"
EVENT_OFFERS_TAG = "Event offers"

MIN_IMAGE_WIDTH = 400
MAX_IMAGE_WIDTH = 800
MIN_IMAGE_HEIGHT = 600
MAX_IMAGE_HEIGHT = 1200
ASPECT_RATIO = image_conversion.ImageRatio.PORTRAIT


def _retrieve_venue_from_location(
    location: serialization.DigitalLocation | serialization.PhysicalLocation,
) -> offerers_models.Venue:
    offerer_id = current_api_key.offererId  # type: ignore[attr-defined]
    if isinstance(location, serialization.PhysicalLocation):
        venue = offerers_models.Venue.query.filter(
            offerers_models.Venue.id == location.venue_id,
            offerers_models.Venue.managingOffererId == offerer_id,
        ).one_or_none()
        if not venue:
            raise api_errors.ApiErrors(
                {"venueId": ["There is no venue with this id associated to your API key"]}, status_code=404
            )

    else:
        venue = offerers_models.Venue.query.filter(
            offerers_models.Venue.managingOffererId == offerer_id, offerers_models.Venue.isVirtual
        ).one_or_none()
        if not venue:
            logger.error("No digital venue found for offerer %s", offerer_id)
            raise api_errors.ApiErrors(
                {
                    "global": [
                        f"The digital venue associated to your API key could not be automatically determined. Please contact support at {settings.SUPPORT_PRO_EMAIL_ADDRESS}."
                    ]
                },
                status_code=400,
            )
    return venue


def _retrieve_offer(offer_id: int) -> offers_models.Offer | None:
    return (
        offers_models.Offer.query.join(offerers_models.Venue)
        .filter(
            offers_models.Offer.id == offer_id, offerers_models.Venue.managingOffererId == current_api_key.offererId  # type: ignore[attr-defined]
        )
        .first()
    )


def _compute_extra_data(body: serialization.OfferCreationBase) -> dict[str, str]:
    extra_data = {}
    for extra_data_field in serialization.ExtraDataModel.__fields__:
        field_value = getattr(body.category_related_fields, extra_data_field, None)
        if field_value:
            if extra_data_field == "musicType":
                extra_data["musicSubType"] = str(music_types.MUSIC_SUB_TYPES_BY_SLUG[field_value].code)
                extra_data["musicType"] = str(music_types.MUSIC_TYPES_BY_SLUG[field_value].code)
            elif extra_data_field == "showType":
                extra_data["showSubType"] = str(show_types.SHOW_SUB_TYPES_BY_SLUG[field_value].code)
                extra_data["showType"] = str(show_types.SHOW_TYPES_BY_SLUG[field_value].code)
            else:
                extra_data[extra_data_field] = field_value

    return extra_data


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
            message = (
                f"The image is too small. It must be It must be above {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT} pixels."
            )
        elif isinstance(error, offers_exceptions.ImageTooLarge):
            message = f"The image is too large. It must be It must be blow {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT} pixels."
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
    api=blueprint.v1_schema, tags=[PRODUCT_OFFERS_TAG], response_model=serialization.ProductOfferResponse
)
@api_key_required
def post_product_offer(body: serialization.ProductOfferCreation) -> serialization.ProductOfferResponse:
    """
    Post a product offer.
    """
    venue = _retrieve_venue_from_location(body.location)

    try:
        with repository.transaction():
            created_offer = offers_api.create_offer(
                audio_disability_compliant=body.disability_compliance.audio_disability_compliant,
                booking_email=body.booking_email,
                description=body.description,
                external_ticket_office_url=body.external_ticket_office_url,
                extra_data=_compute_extra_data(body),
                is_duo=body.is_duo,
                mental_disability_compliant=body.disability_compliance.mental_disability_compliant,
                motor_disability_compliant=body.disability_compliance.motor_disability_compliant,
                name=body.name,
                subcategory_id=body.category_related_fields.subcategory_id,
                url=body.location.url if isinstance(body.location, serialization.DigitalLocation) else None,
                venue=venue,
                visual_disability_compliant=body.disability_compliance.visual_disability_compliant,
                withdrawal_details=body.withdrawal_details,
            )

            if body.stock:
                created_stock = offers_api.create_stock(
                    offer=created_offer,
                    price=finance_utils.to_euros(body.stock.price),
                    quantity=body.stock.quantity if body.stock.quantity != "unlimited" else None,
                    booking_limit_datetime=body.stock.booking_limit_datetime,
                )
            else:
                created_stock = None
            if body.image:
                _save_image(body.image, created_offer)

            offers_api.publish_offer(created_offer, user=None)

    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    created_offer.stock = created_stock
    return serialization.ProductOfferResponse.from_orm(created_offer)


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
@spectree_serialize(api=blueprint.v1_schema, tags=[EVENT_OFFERS_TAG])
@api_key_required
def post_event_offer(body: serialization.EventOfferCreation) -> serialization.OfferResponse:
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
                audio_disability_compliant=body.disability_compliance.audio_disability_compliant,
                booking_email=body.booking_email,
                description=body.description,
                duration_minutes=body.event_duration,
                external_ticket_office_url=body.external_ticket_office_url,
                extra_data=_compute_extra_data(body),
                is_duo=body.is_duo,
                mental_disability_compliant=body.disability_compliance.mental_disability_compliant,
                motor_disability_compliant=body.disability_compliance.motor_disability_compliant,
                name=body.name,
                subcategory_id=body.category_related_fields.subcategory_id,
                url=body.location.url if isinstance(body.location, serialization.DigitalLocation) else None,
                venue=venue,
                visual_disability_compliant=body.disability_compliance.visual_disability_compliant,
                withdrawal_delay=withdrawal_delay,
                withdrawal_details=body.withdrawal_details,
                withdrawal_type=withdrawal_type,
            )

            if body.dates:
                for date in body.dates:
                    offers_api.create_stock(
                        offer=created_offer,
                        price=finance_utils.to_euros(date.price),
                        quantity=date.quantity if date.quantity != "unlimited" else None,
                        beginning_datetime=date.beginning_datetime,
                        booking_limit_datetime=date.booking_limit_datetime,
                    )

            if body.image:
                _save_image(body.image, created_offer)

            offers_api.publish_offer(created_offer, user=None)

    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.OfferResponse.from_orm(created_offer)


@blueprint.v1_blueprint.route("/events/<int:event_id>/dates", methods=["POST"])
@spectree_serialize(api=blueprint.v1_schema, tags=[EVENT_OFFERS_TAG])
@api_key_required
def post_event_date(
    event_id: int, body: serialization.AdditionalDatesCreation
) -> serialization.AdditionalDatesResponse:
    """
    Add dates to an event offer.
    """
    offer = _retrieve_offer(event_id)
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    new_dates: list[offers_models.Stock] = []
    if body.additional_dates:
        try:
            with repository.transaction():
                for date in body.additional_dates:
                    new_dates.append(
                        offers_api.create_stock(
                            offer=offer,
                            price=finance_utils.to_euros(date.price),
                            quantity=date.quantity if date.quantity != "unlimited" else None,
                            beginning_datetime=date.beginning_datetime,
                            booking_limit_datetime=date.booking_limit_datetime,
                        )
                    )
        except offers_exceptions.OfferCreationBaseException as error:
            raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.AdditionalDatesResponse(
        additional_dates=[serialization.DateResponse.from_orm(new_date) for new_date in new_dates]
    )
