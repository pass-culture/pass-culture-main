import datetime
import decimal
from io import BytesIO
import logging
import typing

from PIL import Image
from PIL import UnidentifiedImageError
import flask
import sqlalchemy as sqla

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.categories.subcategories_v2 import ExtraDataFieldEnum
from pcapi.core.educational import models as educational_models
import pcapi.core.educational.api.national_program as np_api
from pcapi.core.finance import repository as finance_repository
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import exceptions
from pcapi.core.offers import models
from pcapi.core.offers import repository
from pcapi.core.providers import models as providers_models
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.models import api_errors
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.public.books_stocks import serialization
from pcapi.utils import date


logger = logging.getLogger(__name__)

EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER = {
    "audioDisabilityCompliant",
    "externalTicketOfficeUrl",
    "mentalDisabilityCompliant",
    "motorDisabilityCompliant",
    "visualDisabilityCompliant",
    "description",
}
EDITABLE_FIELDS_FOR_ALLOCINE_OFFER = {"isDuo"} | EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER
EDITABLE_FIELDS_FOR_ALLOCINE_STOCK = {"bookingLimitDatetime", "price", "priceCategory", "quantity"}
EDITABLE_FIELDS_FOR_INDIVIDUAL_OFFERS_API_PROVIDER = {
    "isActive",
    "isDuo",
    "bookingContact",
    "bookingEmail",
    "extraData",
    "withdrawalDetails",
    "durationMinutes",
    "withdrawalDelay",
    "withdrawalType",
} | EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER

MAX_THUMBNAIL_SIZE = 10_000_000
MIN_THUMBNAIL_WIDTH = 400
MIN_THUMBNAIL_HEIGHT = 400
STANDARD_THUMBNAIL_WIDTH = 400
STANDARD_THUMBNAIL_HEIGHT = 600
ACCEPTED_THUMBNAIL_FORMATS = ("png", "jpg", "jpeg", "mpo", "webp")


AnyCollectiveOffer = educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate


def check_provider_can_edit_stock(
    offer: models.Offer, editing_provider: providers_models.Provider | None = None
) -> None:
    if not offer.isFromProvider:
        return
    if offer.isFromAllocine or offer.isFromCinemaProvider:
        return
    if offer.lastProvider != editing_provider:
        error = api_errors.ApiErrors()
        error.status_code = 400
        error.add_error("global", "Les offres importées ne sont pas modifiables")
        raise error


def check_update_only_allowed_fields_for_offer_from_provider(
    updated_fields: set, provider: providers_models.Provider
) -> None:
    if provider.isAllocine:
        rejected_fields = updated_fields - EDITABLE_FIELDS_FOR_ALLOCINE_OFFER
    elif provider.hasOffererProvider:
        rejected_fields = updated_fields - EDITABLE_FIELDS_FOR_INDIVIDUAL_OFFERS_API_PROVIDER
    else:
        rejected_fields = updated_fields - EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER
    if rejected_fields:
        api_error = api_errors.ApiErrors()
        for field in rejected_fields:
            api_error.add_error(field, "Vous ne pouvez pas modifier ce champ")

        raise api_error


def check_stock_quantity(quantity: int | None, bookingQuantity: int = 0) -> None:
    errors = api_errors.ApiErrors()

    if quantity is not None and quantity < 0:
        errors.add_error("quantity", "Le stock doit être positif")

    if quantity is not None and bookingQuantity and (quantity - bookingQuantity) < 0:
        errors.add_error("quantity", "Le stock total ne peut être inférieur au nombre de réservations")

    if errors.errors:
        raise errors


def check_stocks_price(
    stocks: list[serialization.StockCreationBodyModel] | list[serialization.StockEditionBodyModel],
    offer: models.Offer,
) -> None:
    price_categories = {price_category.id: price_category for price_category in offer.priceCategories}
    for stock in stocks:
        check_stock_has_price_or_price_category(offer, stock, price_categories)
        if stock.price_category_id:
            error_key = "priceCategoryId"
            price = price_categories[stock.price_category_id].price
        else:
            error_key = "price"
            price = stock.price
        check_stock_price(price, offer, error_key=error_key)


def check_stock_price(
    price: decimal.Decimal, offer: models.Offer, old_price: decimal.Decimal | None = None, error_key: str = "price"
) -> None:
    if price < 0:
        errors = api_errors.ApiErrors()
        errors.add_error(error_key, "Le prix doit être positif")
        raise errors
    if price > 300:
        if error_key == "price":
            error_key += "300"
        errors = api_errors.ApiErrors()
        errors.add_error(
            error_key,
            "Le prix d’une offre ne peut excéder 300 euros.",
        )
        raise errors

    offer_price_limitation_rule = models.OfferPriceLimitationRule.query.filter(
        models.OfferPriceLimitationRule.subcategoryId == offer.subcategoryId
    ).one_or_none()
    if (  # pylint: disable=too-many-boolean-expressions
        offer_price_limitation_rule
        and offer.validation is not OfferValidationStatus.DRAFT
        and (offer.extraData is not None and not offer.extraData.get("ean"))
        and (offer.lastValidationPrice is not None or offer.stocks)
    ):
        reference_price = (
            offer.lastValidationPrice
            if offer.lastValidationPrice is not None
            else sorted(offer.stocks, key=lambda s: s.id)[0].price
        )
        if (
            price < (1 - offer_price_limitation_rule.rate) * reference_price
            or price > (1 + offer_price_limitation_rule.rate) * reference_price
        ):
            logger.info(
                "Stock update blocked because of price limitation",
                extra={
                    "offer_id": offer.id,
                    "reference_price": reference_price,
                    "old_price": old_price,
                    "stock_price": price,
                },
                technical_message_id="stock.price.forbidden",
            )

            if error_key == "price":
                error_key += "LimitationRule"
            errors = api_errors.ApiErrors()
            errors.add_error(
                error_key,
                "Le prix indiqué est invalide, veuillez créer une nouvelle offre",
            )
            raise errors

    # Cache this part to avoid N+1 when creating many stocks on the same offer.
    cache_attribute = f"_cached_checked_custom_reimbursement_rules_{offer.id}"
    if not flask.has_request_context() or not getattr(flask.request, cache_attribute, False):
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
                raise api_errors.ApiErrors({"price": [error]})
            if not current_prices:
                # Do not allow an offerer to (soft-)delete all its stocks
                # and create a new one with a different price.
                raise api_errors.ApiErrors({"price": [error]})
            if current_prices.pop() != price:
                raise api_errors.ApiErrors({"price": [error]})
        if flask.has_request_context():
            setattr(flask.request, cache_attribute, True)


def check_required_dates_for_stock(
    offer: models.Offer,
    beginning: datetime.datetime | None,
    booking_limit_datetime: datetime.datetime | None,
) -> None:
    if offer.isThing:
        if beginning:
            raise api_errors.ApiErrors(
                {
                    "global": [
                        "Impossible de mettre une date de début si l'offre ne porte pas sur un évènement",
                    ]
                }
            )
    else:
        if not beginning:
            raise api_errors.ApiErrors({"beginningDatetime": ["Ce paramètre est obligatoire"]})

        if not booking_limit_datetime:
            raise api_errors.ApiErrors({"bookingLimitDatetime": ["Ce paramètre est obligatoire"]})


def check_provider_can_create_stock(
    offer: models.Offer, creating_provider: providers_models.Provider | None = None
) -> None:
    if offer.isFromProvider and offer.lastProvider != creating_provider:
        errors = api_errors.ApiErrors()
        errors.add_error("global", "Les offres importées ne sont pas modifiables")
        raise errors


def check_stock_is_updatable(stock: models.Stock, editing_provider: providers_models.Provider | None = None) -> None:
    if stock.offer.validation == models.OfferValidationStatus.DRAFT:
        return
    check_validation_status(stock.offer)
    check_provider_can_edit_stock(stock.offer, editing_provider)
    check_event_expiration(stock)


def check_price_category_is_updatable(
    price_category: models.PriceCategory, editing_provider: providers_models.Provider | None = None
) -> None:
    check_validation_status(price_category.offer)
    check_provider_can_edit_stock(price_category.offer, editing_provider)


def check_event_expiration(stock: educational_models.CollectiveStock | models.Stock) -> None:
    if stock.isEventExpired:
        errors = api_errors.ApiErrors()
        errors.add_error("global", "Les évènements passés ne sont pas modifiables")
        raise errors


def check_stock_is_deletable(stock: models.Stock) -> None:
    check_validation_status(stock.offer)
    if not stock.isEventDeletable:
        raise exceptions.TooLateToDeleteStock()


def check_can_input_id_at_provider(provider: providers_models.Provider | None, id_at_provider: str | None) -> None:
    if id_at_provider and not provider:
        raise exceptions.CannotSetIdAtProviderWithoutAProvider()


def check_update_only_allowed_stock_fields_for_allocine_offer(updated_fields: set) -> None:
    if not updated_fields.issubset(EDITABLE_FIELDS_FOR_ALLOCINE_STOCK):
        errors = api_errors.ApiErrors()
        errors.status_code = 400
        errors.add_error("global", "Pour les offres importées, certains champs ne sont pas modifiables")
        raise errors


def check_image_size(image_as_bytes: bytes, max_size: int = MAX_THUMBNAIL_SIZE) -> None:
    if len(image_as_bytes) > max_size:
        raise exceptions.FileSizeExceeded(max_size=max_size)


def check_image(
    image_as_bytes: bytes,
    accepted_types: tuple = ACCEPTED_THUMBNAIL_FORMATS,
    min_width: int = MIN_THUMBNAIL_WIDTH,
    min_height: int = MIN_THUMBNAIL_HEIGHT,
    max_width: int | None = None,
    max_height: int | None = None,
    max_size: int = MAX_THUMBNAIL_SIZE,
) -> None:
    check_image_size(image_as_bytes, max_size)
    try:
        image = Image.open(BytesIO(image_as_bytes))
    except UnidentifiedImageError:
        raise exceptions.UnidentifiedImage()
    except Exception:
        raise exceptions.ImageValidationError()
    assert image.format is not None  # helps mypy

    if image.format.lower() not in accepted_types:
        raise exceptions.UnacceptedFileType(accepted_types, image.format)

    if image.width < min_width or image.height < min_height:
        raise exceptions.ImageTooSmall(min_width, min_height)

    if max_width is not None and image.width > max_width or max_height is not None and image.height > max_height:
        raise exceptions.ImageTooLarge(max_width, max_height)


def check_validation_status(
    offer: models.Offer | educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
) -> None:
    if offer.validation in (models.OfferValidationStatus.REJECTED, models.OfferValidationStatus.PENDING):
        raise exceptions.RejectedOrPendingOfferNotEditable()


def check_contact_request(offer: AnyCollectiveOffer, in_data: dict) -> None:
    if isinstance(offer, educational_models.CollectiveOffer):
        # collective offers are not concerned, for now.
        return

    set_email = in_data["contactEmail"] if "contactEmail" in in_data else offer.contactEmail
    set_phone = in_data["contactPhone"] if "contactPhone" in in_data else offer.contactPhone
    set_url = in_data["contactUrl"] if "contactUrl" in in_data else offer.contactUrl
    set_form = in_data["contactForm"] if "contactForm" in in_data else offer.contactForm

    if not any((set_email, set_phone, set_url, set_form)):
        raise exceptions.AllNullContactRequestDataError()

    if set_url and set_form:
        raise exceptions.UrlandFormBothSetError()


def check_offer_is_digital(offer: models.Offer) -> None:
    if not offer.isDigital:
        errors = api_errors.ApiErrors()
        errors.add_error(
            "global",
            "Impossible de créer des codes d'activation sur une offre non-numérique",
        )
        raise errors


def check_activation_codes_expiration_datetime(
    activation_codes_expiration_datetime: datetime.datetime | None,
    booking_limit_datetime: datetime.datetime | None,
) -> None:
    if activation_codes_expiration_datetime is None:
        return

    if booking_limit_datetime is None and activation_codes_expiration_datetime is not None:
        errors = api_errors.ApiErrors()
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
        and activation_codes_expiration_datetime < booking_limit_datetime + datetime.timedelta(days=7)
    ):
        errors = api_errors.ApiErrors()
        errors.add_error(
            "activationCodesExpirationDatetime",
            (
                "La date limite de validité des codes d'activation doit être ultérieure"
                " d'au moins 7 jours à la date limite de réservation"
            ),
        )
        raise errors


def check_activation_codes_expiration_datetime_on_stock_edition(
    activation_codes: list[models.ActivationCode] | None,
    booking_limit_datetime: datetime.datetime | None,
) -> None:
    if activation_codes is None or len(activation_codes) == 0:
        return

    activation_codes_expiration_datetime = activation_codes[0].expirationDate
    check_activation_codes_expiration_datetime(activation_codes_expiration_datetime, booking_limit_datetime)


def check_offer_is_eligible_for_educational(subcategory_id: str | None) -> None:
    if not subcategory_id:
        return

    subcategory = subcategories.ALL_SUBCATEGORIES_DICT.get(subcategory_id)
    if not subcategory or not subcategory.can_be_educational:
        raise exceptions.SubcategoryNotEligibleForEducationalOffer()


def check_offer_withdrawal(
    withdrawal_type: models.WithdrawalTypeEnum | None,
    withdrawal_delay: int | None,
    subcategory_id: str,
    booking_contact: str | None,
    provider: providers_models.Provider | None,
) -> None:
    is_offer_withdrawable = subcategory_id in subcategories.WITHDRAWABLE_SUBCATEGORIES
    if is_offer_withdrawable and withdrawal_type is None:
        raise exceptions.WithdrawableEventOfferMustHaveWithdrawal()

    if FeatureToggle.WIP_MANDATORY_BOOKING_CONTACT.is_active() and is_offer_withdrawable and not booking_contact:
        raise exceptions.WithdrawableEventOfferMustHaveBookingContact()

    if withdrawal_type == models.WithdrawalTypeEnum.NO_TICKET and withdrawal_delay is not None:
        raise exceptions.NoDelayWhenEventWithdrawalTypeHasNoTicket()

    if (
        withdrawal_type in (models.WithdrawalTypeEnum.ON_SITE, models.WithdrawalTypeEnum.BY_EMAIL)
        and withdrawal_delay is None
    ):
        raise exceptions.EventWithTicketMustHaveDelay()

    # Only providers that activated the charlie api can create offer with IN_APP withdrawal type
    if withdrawal_type == models.WithdrawalTypeEnum.IN_APP:
        if not provider or not provider.hasProviderEnableCharlie:
            raise exceptions.NonLinkedProviderCannotHaveInAppTicket()


def check_offer_subcategory_is_valid(offer_subcategory_id: str | None) -> None:
    if not offer_subcategory_id:
        return
    if offer_subcategory_id not in subcategories.ALL_SUBCATEGORIES_DICT:
        raise exceptions.UnknownOfferSubCategory()
    if not subcategories.ALL_SUBCATEGORIES_DICT[offer_subcategory_id].is_selectable:
        raise exceptions.SubCategoryIsInactive()


def check_booking_limit_datetime(
    stock: educational_models.CollectiveStock | models.Stock | None,
    beginning: datetime.datetime | None,
    booking_limit_datetime: datetime.datetime | None,
) -> None:
    if stock:
        if isinstance(stock, educational_models.CollectiveStock):
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


def check_offer_extra_data(
    subcategory_id: str,
    extra_data: models.OfferExtraData | None,
    venue: offerers_models.Venue,
    is_from_private_api: bool,
    offer: models.Offer | None = None,
) -> None:
    errors = api_errors.ApiErrors()

    if extra_data is None:
        extra_data = {}

    subcategory = subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id]
    mandatory_fields = [
        name
        for name, conditional_field in subcategory.conditional_fields.items()
        if (is_from_private_api and conditional_field.is_required_in_internal_form)
        or (not is_from_private_api and conditional_field.is_required_in_external_form)
    ]
    for field in mandatory_fields:
        if not extra_data.get(field):
            errors.add_error(field, "Ce champ est obligatoire")

    try:
        ean = extra_data.get(ExtraDataFieldEnum.EAN.value)
        if ean and (not offer or (offer.extraData and ean != offer.extraData.get(ExtraDataFieldEnum.EAN.value))):
            _check_ean_field(extra_data, ExtraDataFieldEnum.EAN.value)
            check_ean_does_not_exist(ean, venue)
    except (exceptions.EanFormatException, exceptions.OfferAlreadyExists) as e:
        errors.add_client_error(e)

    try:
        _check_value_is_allowed(extra_data, ExtraDataFieldEnum.MUSIC_TYPE, music_types.MUSIC_TYPES_LABEL_BY_CODE)
        _check_value_is_allowed(extra_data, ExtraDataFieldEnum.MUSIC_SUB_TYPE, music_types.MUSIC_SUB_TYPES_BY_CODE)
        _check_value_is_allowed(extra_data, ExtraDataFieldEnum.SHOW_TYPE, show_types.SHOW_TYPES_LABEL_BY_CODE)
        _check_value_is_allowed(extra_data, ExtraDataFieldEnum.SHOW_SUB_TYPE, show_types.SHOW_SUB_TYPES_BY_CODE)
    except exceptions.ExtraDataValueNotAllowed as e:
        errors.add_client_error(e)

    if errors.errors:
        raise errors


def check_ean_does_not_exist(ean: str | None, venue: offerers_models.Venue) -> None:
    if repository.has_active_offer_with_ean(ean, venue):
        if ean:
            raise exceptions.OfferAlreadyExists("ean")


def _check_value_is_allowed(
    extra_data: models.OfferExtraData, extra_data_field: ExtraDataFieldEnum, allowed_values: dict
) -> None:
    field_value = extra_data.get(extra_data_field.value)
    if field_value is None:
        return
    if not isinstance(field_value, (str, int)):
        raise exceptions.ExtraDataValueNotAllowed(extra_data_field.value, "should be an int or a string")
    try:
        music_type_code = int(field_value)
    except ValueError:
        raise exceptions.ExtraDataValueNotAllowed(extra_data_field.value, "should be an int or an int string")
    if music_type_code not in allowed_values:
        raise exceptions.ExtraDataValueNotAllowed(extra_data_field.value, "should be in allowed values")


def _check_ean_field(extra_data: models.OfferExtraData, field: str) -> None:
    value = extra_data.get(field)
    if not value:
        return

    if not isinstance(value, str):
        raise exceptions.EanFormatException(field, f"L'{field.upper()} doit être une chaîne de caractères")

    if not value.isdigit() or not len(value) == 13:
        raise exceptions.EanFormatException(field, f"L'{field.upper()} doit être composé de 13 chiffres")


def check_offer_is_from_current_cinema_provider(offer: models.Offer) -> None:
    venue_cinema_pivot = providers_models.CinemaProviderPivot.query.filter(
        providers_models.CinemaProviderPivot.venueId == offer.venueId
    ).one_or_none()
    if not venue_cinema_pivot or offer.lastProviderId != venue_cinema_pivot.providerId:
        raise exceptions.UnexpectedCinemaProvider()


def check_is_duo_compliance(is_duo: bool | None, subcategory: subcategories.Subcategory) -> None:
    if is_duo and not subcategory.can_be_duo:
        raise exceptions.OfferCannotBeDuo()


def check_price_categories_deletable(offer: models.Offer) -> None:
    if offer.validation != models.OfferValidationStatus.DRAFT:
        raise api_errors.ApiErrors(
            {"global": "Les catégories de prix ne sont pas supprimables sur les offres qui ne sont pas en brouillon"}
        )


def check_stock_has_price_or_price_category(
    offer: models.Offer,
    stock: serialization.StockCreationBodyModel | serialization.StockEditionBodyModel,
    existing_price_categories: dict,
) -> None:
    if offer.isThing:
        if stock.price is None:
            raise api_errors.ApiErrors(
                {"price": ["Le prix est obligatoire pour les offres produit"]},
                status_code=400,
            )
        return
    if not stock.price_category_id:
        raise api_errors.ApiErrors(
            {"price_category_id": ["Le tarif est obligatoire pour les offres évènement"]},
            status_code=400,
        )
    if stock.price_category_id not in existing_price_categories:
        raise api_errors.ApiErrors(
            {"price_category_id": ["Le tarif avec l'id %s n'existe pas" % stock.price_category_id]},
            status_code=400,
        )


def check_for_duplicated_price_categories(
    new_labels_and_prices: set[tuple[str, decimal.Decimal]], offer_id: int
) -> None:
    existing_price_category = (
        models.PriceCategory.query.filter_by(offerId=offer_id)
        .join(models.PriceCategoryLabel)
        .filter(sqla.func.ROW(models.PriceCategoryLabel.label, models.PriceCategory.price).in_(new_labels_and_prices))
        .first()
    )

    if existing_price_category:
        raise api_errors.ApiErrors(
            {"priceCategories": [f"The price category {existing_price_category.label} already exists"]},
            status_code=400,
        )


class OfferValidationError(Exception):
    field = "all"
    msg = "Invalid"


class UnknownNationalProgram(OfferValidationError):
    field = "national_program"
    msg = "National program unknown"


class IllegalNationalProgram(OfferValidationError):
    field = "national_program"
    msg = "National program known, but can't be used in this context"


class MissingDomains(OfferValidationError):
    field = "domains"
    msg = "Domains can't be null if national program is set"


def validate_national_program(
    nationalProgramId: int | None, domains: typing.Sequence[educational_models.EducationalDomain] | None
) -> None:
    if not nationalProgramId:
        return

    if not domains:
        raise MissingDomains()

    nps = {np.id for domain in domains for np in domain.nationalPrograms}
    if nationalProgramId not in nps:
        if not np_api.get_national_program(nationalProgramId):
            raise UnknownNationalProgram()
        raise IllegalNationalProgram()
