from datetime import datetime
from datetime import timedelta
from io import BytesIO
import logging
from typing import Optional

from PIL import Image

from pcapi import settings
from pcapi.core.categories import subcategories
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
from pcapi.core.categories.subcategories import WITHDRAWABLE_SUBCATEGORIES
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.finance import repository as finance_repository
from pcapi.core.offers import exceptions
from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import Stock
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.providers.models import Provider
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.feature import FeatureToggle
from pcapi.utils import date


logger = logging.getLogger(__name__)

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

KEY_VALIDATION_CONFIG = {
    "init": ["minimum_score", "rules"],
    "rules": ["name", "factor", "conditions"],
    "conditions": ["model", "attribute", "condition"],
    "condition": ["operator", "comparated"],
}

VALUE_VALIDATION_CONFIG = {
    "name": [str],
    "conditions": [list],
    "model": ["Offer", "Venue", "Offerer", "CollectiveOffer", "CollectiveOfferTemplate", "CollectiveStock"],
    "attribute": [str],
    "type": [str, list],
    "factor": [float, int],
    "operator": [">", ">=", "<", "<=", "==", "!=", "is", "in", "not in", "contains", "contains-exact"],
    "comparated": [str, bool, float, int, list, None],
    "minimum_score": [float, int],
}

OFFER_EXTRA_DATA_MANDATORY_FIELDS = {
    "showType",
    "musicType",
}


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


def check_stock_quantity(quantity: int | None, bookingQuantity: int = 0) -> None:
    api_errors = ApiErrors()

    if quantity is not None and quantity < 0:
        api_errors.add_error("quantity", "Le stock doit être positif")

    if quantity is not None and bookingQuantity and (quantity - bookingQuantity) < 0:
        api_errors.add_error("quantity", "Le stock total ne peut être inférieur au nombre de réservations")

    if api_errors.errors:
        raise api_errors


def check_stock_price(price: float, offer: Offer) -> None:
    if price < 0:
        api_errors = ApiErrors()
        api_errors.add_error("price", "Le prix doit être positif")
        raise api_errors
    if price > 300 and not offer.isEducational and not offer.isEvent:
        api_errors = ApiErrors()
        api_errors.add_error(
            "price300",
            "Le prix d’une offre ne peut excéder 300 euros.",
        )
        raise api_errors
    if finance_repository.has_active_or_future_custom_reimbursement_rule(offer):
        # We obviously look for active rules, but also future ones: if
        # a reimbursement rule has been negotiated that will enter in
        # effect tomorrow, we don't want to let the offerer change its
        # price today.
        error = (
            "Vous ne pouvez pas modifier le prix ou créer un stock pour cette offre, "
            "car elle bénéficie d'un montant de remboursement spécifique."
        )
        current_prices = {stock.price for stock in offer.stocks if not stock.isSoftDeleted}
        if len(current_prices) > 1:
            # This is not supposed to happen, we should be notified.
            logger.error(
                "An offer with a custom reimbursement rule has multiple prices",
                extra={
                    "offer": offer.id,
                    "prices": current_prices,
                },
            )
            raise ApiErrors({"price": [error]})
        if not current_prices:
            # Do not allow an offerer to (soft-)delete all its stocks
            # and create a new one with a different price.
            raise ApiErrors({"price": [error]})
        if current_prices.pop() != price:
            raise ApiErrors({"price": [error]})


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
    check_event_expiration(stock)


def check_event_expiration(stock: CollectiveStock | Stock):  # type: ignore [no-untyped-def]
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


def check_validation_status(offer: Offer | CollectiveOffer | CollectiveOfferTemplate) -> None:
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
        and activation_codes_expiration_datetime < booking_limit_datetime + timedelta(days=7)
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
        if key == "condition" and value["operator"] == "contains" and not isinstance(value["comparated"], list):
            raise TypeError(
                f"The `comparated` argument `{value['comparated']}` for the `contains` operator is not a list"
            )
        if isinstance(value, list) and key in KEY_VALIDATION_CONFIG:
            for item in value:
                check_validation_config_parameters(item, KEY_VALIDATION_CONFIG[key])
        elif isinstance(value, dict):
            check_validation_config_parameters(value, KEY_VALIDATION_CONFIG[key])
        # Note that these are case-senstive
        elif not (value in VALUE_VALIDATION_CONFIG[key] or type(value) in VALUE_VALIDATION_CONFIG[key]):  # type: ignore [operator]
            raise ValueError(f"{value} of type {type(value)} not in: {VALUE_VALIDATION_CONFIG[key]}")


def check_offer_is_eligible_for_educational(subcategory_id: str, is_educational: bool) -> None:
    if is_educational:
        subcategory = subcategories.ALL_SUBCATEGORIES_DICT.get(subcategory_id)
        if not subcategory or not subcategory.can_be_educational:
            raise exceptions.SubcategoryNotEligibleForEducationalOffer()


def check_offer_withdrawal(
    withdrawal_type: Optional[WithdrawalTypeEnum], withdrawal_delay: Optional[int], subcategory_id: Optional[str]
) -> None:
    if subcategory_id not in WITHDRAWABLE_SUBCATEGORIES and withdrawal_type is not None:
        raise exceptions.NonWithdrawableEventOfferCantHaveWithdrawal()

    if (
        FeatureToggle.PRO_DISABLE_EVENTS_QRCODE.is_active()
        and subcategory_id in WITHDRAWABLE_SUBCATEGORIES
        and withdrawal_type is None
    ):
        raise exceptions.WithdrawableEventOfferMustHaveWithdrawal()

    if withdrawal_type == WithdrawalTypeEnum.NO_TICKET and withdrawal_delay is not None:
        raise exceptions.NoDelayWhenEventWithdrawalTypeHasNoTicket()

    if withdrawal_type in (WithdrawalTypeEnum.ON_SITE, WithdrawalTypeEnum.BY_EMAIL) and withdrawal_delay is None:
        raise exceptions.EventWithTicketMustHaveDelay()


def check_offer_subcategory_is_valid(offer_subcategory_id):  # type: ignore [no-untyped-def]
    if offer_subcategory_id not in ALL_SUBCATEGORIES_DICT:
        raise exceptions.UnknownOfferSubCategory()
    if not ALL_SUBCATEGORIES_DICT[offer_subcategory_id].is_selectable:
        raise exceptions.SubCategoryIsInactive()


def check_booking_limit_datetime(
    stock: Optional[CollectiveStock | Stock],
    beginning: Optional[datetime],
    booking_limit_datetime: Optional[datetime],
) -> None:
    if stock:
        if beginning is None:
            beginning = stock.beginningDatetime
        if booking_limit_datetime is None:
            booking_limit_datetime = stock.bookingLimitDatetime

        if isinstance(stock, CollectiveStock):
            offer = stock.collectiveOffer
        else:
            offer = stock.offer

        if beginning and booking_limit_datetime and offer and offer.venue.departementCode is not None:
            beginning_tz = date.utc_datetime_to_department_timezone(beginning, offer.venue.departementCode)
            booking_limit_datetime_tz = date.utc_datetime_to_department_timezone(
                booking_limit_datetime, offer.venue.departementCode
            )

            same_date = beginning_tz.date() == booking_limit_datetime_tz.date()
            if not same_date and booking_limit_datetime_tz > beginning_tz:
                raise exceptions.BookingLimitDatetimeTooLate()
            return

    if beginning and booking_limit_datetime and booking_limit_datetime > beginning:
        raise exceptions.BookingLimitDatetimeTooLate()


def check_offer_extra_data(offer: Optional[Offer], subcategory_id: str, extra_data: dict) -> dict:
    api_errors = ApiErrors()
    subcategory = ALL_SUBCATEGORIES_DICT[subcategory_id]
    mandatory_fields = OFFER_EXTRA_DATA_MANDATORY_FIELDS & set(subcategory.conditional_fields)
    if not extra_data:
        extra_data = {}

    for field in mandatory_fields:
        if offer and offer.extraData and offer.extraData.get(field):  # type: ignore [union-attr]
            extra_data[field] = offer.extraData.get(field)  # type: ignore [union-attr]
        elif not extra_data or not extra_data.get(field):
            api_errors.add_error(field, "Ce champ est obligatoire")

    if api_errors.errors:
        raise api_errors

    return extra_data
