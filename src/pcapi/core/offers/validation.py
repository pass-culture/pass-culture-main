from datetime import datetime
from datetime import timedelta
from io import BytesIO
from typing import Optional
from typing import Union

from PIL import Image

from pcapi import settings
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.utils import requests as pcapi_requests

from . import exceptions
from ..providers.models import Provider
from .models import ActivationCode
from .models import OfferValidationStatus


EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER = {
    "audioDisabilityCompliant",
    "externalTicketOfficeUrl",
    "mentalDisabilityCompliant",
    "motorDisabilityCompliant",
    "visualDisabilityCompliant",
}
EDITABLE_FIELDS_FOR_ALLOCINE_OFFER = {"isDuo"} | EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER
EDITABLE_FIELDS_FOR_ALLOCINE_STOCK = {"bookingLimitDatetime", "price", "quantity"}

MAX_THUMBNAIL_SIZE = 10_000_000
MIN_THUMBNAIL_WIDTH = 400
MIN_THUMBNAIL_HEIGHT = 400
ACCEPTED_THUMBNAIL_FORMATS = (
    "png",
    "jpg",
    "jpeg",
)
DISTANT_IMAGE_REQUEST_TIMEOUT = 5
CHUNK_SIZE_IN_BYTES = 4096


KEY_VALIDATION_CONFIG = {
    "init": ["minimum_score", "rules"],
    "rules": ["name", "factor", "conditions"],
    "conditions": ["model", "attribute", "condition"],
    "condition": ["operator", "comparated"],
}

VALUE_VALIDATION_CONFIG = {
    "name": [str],
    "conditions": [list],
    "model": ["Offer", "Venue", "Offerer"],
    "attribute": [str],
    "type": [str, list],
    "factor": [float, int],
    "operator": [">", ">=", "<", "<=", "==", "!=", "is", "in", "not in", "contains", "contains-exact"],
    "comparated": [str, bool, float, int, list, None],
    "minimum_score": [float, int],
}


def check_user_can_create_activation_event(user: User) -> None:
    if not user.isAdmin:
        error = ForbiddenError()
        error.add_error("type", "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation")
        raise error


def check_offer_existing_stocks_are_editable(offer: Offer) -> None:
    check_validation_status(offer)
    if not offer.isEditable:
        error = ApiErrors()
        error.status_code = 400
        error.add_error("global", "Les offres importées ne sont pas modifiables")
        raise error


def check_update_only_allowed_fields_for_offer_from_provider(updated_fields: set, provider: Provider) -> None:
    if provider.isAllocine:
        rejected_fields = updated_fields - EDITABLE_FIELDS_FOR_ALLOCINE_OFFER
    else:
        rejected_fields = updated_fields - EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER
    if rejected_fields:
        api_error = ApiErrors()
        for field in rejected_fields:
            api_error.add_error(field, "Vous ne pouvez pas modifier ce champ")

        raise api_error


def check_stock_quantity(quantity: Union[int, None], bookingQuantity: int = 0) -> None:
    api_errors = ApiErrors()

    if quantity is not None and quantity < 0:
        api_errors.add_error("quantity", "Le stock doit être positif")

    if quantity is not None and bookingQuantity and (quantity - bookingQuantity) < 0:
        api_errors.add_error("quantity", "Le stock total ne peut être inférieur au nombre de réservations")

    if api_errors.errors:
        raise api_errors


def check_stock_price(price: float, offer_is_event: bool) -> None:
    if price < 0:
        api_errors = ApiErrors()
        api_errors.add_error("price", "Le prix doit être positif")
        raise api_errors
    if price > 300 and offer_is_event == False:
        api_errors = ApiErrors()
        api_errors.add_error(
            "priceexceeds300",
            "Le prix d’une offre ne peut excéder 300 euros.",
        )
        raise api_errors


def check_required_dates_for_stock(
    offer: Offer,
    beginning: Optional[datetime],
    booking_limit_datetime: Optional[datetime],
) -> None:
    if offer.isThing:
        if beginning:
            raise ApiErrors(
                {
                    "global": [
                        "Impossible de mettre une date de début si l'offre ne porte pas sur un événement",
                    ]
                }
            )
    else:
        if not beginning:
            raise ApiErrors({"beginningDatetime": ["Ce paramètre est obligatoire"]})

        if not booking_limit_datetime:
            raise ApiErrors({"bookingLimitDatetime": ["Ce paramètre est obligatoire"]})


def check_stock_can_be_created_for_offer(offer: Offer) -> None:
    check_validation_status(offer)
    if offer.isFromProvider:
        api_errors = ApiErrors()
        api_errors.add_error("global", "Les offres importées ne sont pas modifiables")
        raise api_errors


def check_stock_is_updatable(stock: Stock) -> None:
    check_offer_existing_stocks_are_editable(stock.offer)
    if stock.isEventExpired:
        api_errors = ApiErrors()
        api_errors.add_error("global", "Les événements passés ne sont pas modifiables")
        raise api_errors


def check_stock_is_deletable(stock: Stock) -> None:
    check_offer_existing_stocks_are_editable(stock.offer)
    if not stock.isEventDeletable:
        raise exceptions.TooLateToDeleteStock()


def check_update_only_allowed_stock_fields_for_allocine_offer(updated_fields: set) -> None:
    if not updated_fields.issubset(EDITABLE_FIELDS_FOR_ALLOCINE_STOCK):
        api_errors = ApiErrors()
        api_errors.status_code = 400
        api_errors.add_error("global", "Pour les offres importées, certains champs ne sont pas modifiables")
        raise api_errors


def check_stock_has_no_custom_reimbursement_rule(stock: Stock):
    if stock.offer.custom_reimbursement_rules:
        api_errors = ApiErrors()
        api_errors.status_code = 400
        api_errors.add_error("price", "Vous ne pouvez pas modifier le prix de cette offre")
        raise api_errors


def get_distant_image(
    url: str,
    accepted_types: tuple = ACCEPTED_THUMBNAIL_FORMATS,
    max_size: int = MAX_THUMBNAIL_SIZE,
) -> bytes:
    try:
        streaming_response = pcapi_requests.get(
            url, timeout=DISTANT_IMAGE_REQUEST_TIMEOUT, stream=True, log_at_error_level=False
        )
        streaming_response.raise_for_status()
    except Exception:
        raise exceptions.FailureToRetrieve()

    # These two headers are recommended to be included by the server, but they could be missing
    content_type = streaming_response.headers.get("Content-Type", "")
    if content_type and content_type.lstrip("image/") not in accepted_types:
        raise exceptions.UnacceptedFileType(accepted_types=accepted_types)

    content_length = streaming_response.headers.get("Content-Length", 0)
    if int(content_length) > max_size:
        raise exceptions.FileSizeExceeded(max_size=max_size)

    response_content = b""
    for chunk in streaming_response.iter_content(CHUNK_SIZE_IN_BYTES):
        response_content += chunk
        if len(response_content) > max_size:
            streaming_response.close()
            raise exceptions.FileSizeExceeded(max_size=max_size)
    return response_content


def get_uploaded_image(image_as_bytes: bytes, max_size: int = MAX_THUMBNAIL_SIZE) -> bytes:
    if len(image_as_bytes) > max_size:
        raise exceptions.FileSizeExceeded(max_size=max_size)
    return image_as_bytes


def check_image(
    image_as_bytes: bytes,
    accepted_types: tuple = ACCEPTED_THUMBNAIL_FORMATS,
    min_width: int = MIN_THUMBNAIL_WIDTH,
    min_height: int = MIN_THUMBNAIL_HEIGHT,
) -> None:
    try:
        image = Image.open(BytesIO(image_as_bytes))
    except Exception:
        raise exceptions.UnacceptedFileType(accepted_types)

    if image.format.lower() not in accepted_types:
        raise exceptions.UnacceptedFileType(accepted_types)

    if image.width < min_width or image.height < min_height:
        raise exceptions.ImageTooSmall(min_width, min_height)


def check_validation_status(offer: Offer) -> None:
    if offer.validation in (OfferValidationStatus.REJECTED, OfferValidationStatus.PENDING):
        error = ApiErrors()
        error.add_error("global", "Les offres refusées ou en attente de validation ne sont pas modifiables")
        raise error


def check_offer_is_digital(offer: Offer) -> None:
    if not offer.isDigital:
        errors = ApiErrors()
        errors.add_error(
            "global",
            "Impossible de créer des codes d'activation sur une offre non-numérique",
        )
        raise errors


def check_activation_codes_expiration_datetime(
    activation_codes_expiration_datetime: Optional[datetime],
    booking_limit_datetime: Optional[datetime],
) -> None:
    if activation_codes_expiration_datetime is None:
        return

    if booking_limit_datetime is None and activation_codes_expiration_datetime is not None:
        errors = ApiErrors()
        errors.add_error(
            "bookingLimitDatetime",
            (
                "Une date limite de validité a été renseignée. Dans ce cas, il faut également"
                " renseigner une date limite de réservation qui doit être antérieure d'au moins 7 jours."
            ),
        )
        raise errors

    if (
        booking_limit_datetime is not None
        and activation_codes_expiration_datetime < booking_limit_datetime + timedelta(days=7)  # type: ignore[operator]
    ):
        errors = ApiErrors()
        errors.add_error(
            "activationCodesExpirationDatetime",
            (
                "La date limite de validité des codes d'activation doit être ultérieure"
                " d'au moins 7 jours à la date limite de réservation"
            ),
        )
        raise errors


def check_activation_codes_expiration_datetime_on_stock_edition(
    activation_codes: Optional[list[ActivationCode]],
    booking_limit_datetime: Optional[datetime],
) -> None:
    if activation_codes is None or len(activation_codes) == 0:
        return

    activation_codes_expiration_datetime = activation_codes[0].expirationDate
    check_activation_codes_expiration_datetime(activation_codes_expiration_datetime, booking_limit_datetime)


def check_user_can_load_config(user: User) -> None:
    if settings.IS_PROD and user.email not in settings.SUPER_ADMIN_EMAIL_ADDRESSES:
        error = ForbiddenError()
        error.add_error("type", "Seuls les membres de l'équipe de validation peuvent éditer cette configuration")
        raise error


def check_validation_config_parameters(config_as_dict: dict, valid_keys: list) -> None:
    for key, value in config_as_dict.items():
        if key not in valid_keys:
            raise KeyError(f"Wrong key: {key}")

        if isinstance(value, list) and key in KEY_VALIDATION_CONFIG:
            for item in value:
                check_validation_config_parameters(item, KEY_VALIDATION_CONFIG[key])
        elif isinstance(value, dict):
            check_validation_config_parameters(value, KEY_VALIDATION_CONFIG[key])
        # Note that these are case-senstive
        elif not (value in VALUE_VALIDATION_CONFIG[key] or type(value) in VALUE_VALIDATION_CONFIG[key]):
            raise ValueError(f"{value} of type {type(value)} not in: {VALUE_VALIDATION_CONFIG[key]}")
