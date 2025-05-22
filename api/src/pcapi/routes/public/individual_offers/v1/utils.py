import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.core.providers import models as providers_models
from pcapi.models import api_errors, db
from pcapi.routes.public import utils as public_utils
from pcapi.utils import image_conversion
from pcapi.validation.routes.users_authentifications import current_api_key

from . import constants, serialization


def get_venue_with_offerer_address(venue_id: int) -> offerers_models.Venue:
    return (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id == venue_id)
        .options(sa_orm.joinedload(offerers_models.Venue.offererAddress))
        .one()
    )


def check_venue_id_is_tied_to_api_key(venue_id: int | None) -> None:
    if venue_id is None:
        return

    is_venue_tied_to_api_key = db.session.query(
        db.session.query(providers_models.VenueProvider)
        .filter(
            providers_models.VenueProvider.provider == current_api_key.provider,
            providers_models.VenueProvider.venueId == venue_id,
            providers_models.VenueProvider.isActive,
        )
        .exists()
    ).scalar()
    if not is_venue_tied_to_api_key:
        raise api_errors.ApiErrors(
            {"venue_id": ["The venue could not be found"]}, status_code=404
        )


def check_offer_subcategory(
    body: serialization.ProductOfferEdition | serialization.EventOfferEdition,
    offer_subcategory_id: str,
) -> None:
    if body.category_related_fields is not None and (
        body.category_related_fields.subcategory_id != offer_subcategory_id
    ):
        raise api_errors.ApiErrors(
            {"categoryRelatedFields.category": ["The category cannot be changed"]}
        )


def retrieve_offer_query(offer_id: int) -> sa_orm.Query:
    return _retrieve_offer_tied_to_user_query().filter(
        offers_models.Offer.id == offer_id
    )


def _retrieve_offer_tied_to_user_query() -> sa_orm.Query:
    return (
        db.session.query(offers_models.Offer)
        .join(offerers_models.Venue)
        .join(offerers_models.Venue.venueProviders)
        .join(providers_models.VenueProvider.provider)
        .filter(providers_models.VenueProvider.provider == current_api_key.provider)
        .filter(providers_models.VenueProvider.isActive)
        .options(sa_orm.joinedload(offers_models.Offer.venue))
    )


def save_image(image_body: serialization.ImageBody, offer: offers_models.Offer) -> None:
    try:
        image_as_bytes = public_utils.get_bytes_from_base64_string(image_body.file)
    except public_utils.InvalidBase64Exception:
        raise api_errors.ApiErrors(
            errors={"imageFile": ["The value must be a valid base64 string."]}
        )
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
            errors={
                "imageFile": f"Bad image ratio: expected {str(error.expected)[:4]}, found {str(error.found)[:4]}"
            }
        )


def get_event_with_details(event_id: int) -> offers_models.Offer | None:
    return (
        retrieve_offer_query(event_id)
        .filter(offers_models.Offer.isEvent)
        .outerjoin(
            offers_models.Offer.stocks.and_(sa.not_(offers_models.Stock.isEventExpired))
        )
        .options(sa_orm.contains_eager(offers_models.Offer.stocks))
        .options(
            sa_orm.joinedload(offers_models.Offer.priceCategories).joinedload(
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


def load_venue_and_provider_query(query: sa_orm.Query) -> sa_orm.Query:
    return query.options(
        sa_orm.joinedload(offers_models.Offer.lastProvider).joinedload(
            providers_models.Provider.offererProvider
        ),
        sa_orm.joinedload(offers_models.Offer.venue).load_only(
            offerers_models.Venue.isVirtual
        ),
    )


def extract_venue_and_offerer_address_from_location(
    body: serialization.OfferEditionBase,
) -> tuple[offerers_models.Venue | None, offerers_models.OffererAddress | None]:
    location = body.location
    if not location:
        return None, None

    venue = get_venue_with_offerer_address(location.venue_id)

    if location.type == "address":
        address = public_utils.get_address_or_raise_404(location.address_id)
        offerer_address = offerers_api.get_or_create_offerer_address(
            offerer_id=venue.managingOffererId,
            address_id=address.id,
            label=location.address_label,
        )

        return venue, offerer_address

    return venue, venue.offererAddress
