import datetime
import decimal
from io import BytesIO
import logging
import re
import warnings

from PIL import Image
from PIL import UnidentifiedImageError
from dateutil.relativedelta import relativedelta
import flask
from pydantic.v1 import HttpUrl
import sqlalchemy as sa

from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.categories.genres import show
from pcapi.core.categories.subcategories import ExtraDataFieldEnum
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import repository as finance_repository
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.core.offers import exceptions
from pcapi.core.offers import models
from pcapi.core.offers import repository
from pcapi.core.offers import schemas
from pcapi.core.providers import models as providers_models
from pcapi.models import api_errors
from pcapi.models.feature import FeatureToggle
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.serialization import stock_serialize as serialization
from pcapi.utils import date


logger = logging.getLogger(__name__)

EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER = {
    "name",
    "audioDisabilityCompliant",
    "externalTicketOfficeUrl",
    "mentalDisabilityCompliant",
    "motorDisabilityCompliant",
    "visualDisabilityCompliant",
    "description",
    "offererAddress",
    "venue",
    "url",
}
EDITABLE_FIELDS_FOR_ALLOCINE_OFFER = {"isDuo"} | EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER
EDITABLE_FIELDS_FOR_ALLOCINE_STOCK = {"bookingLimitDatetime", "price", "priceCategory", "quantity"}
EDITABLE_FIELDS_FOR_INDIVIDUAL_OFFERS_API_PROVIDER = {
    "name",
    "description",
    "isActive",
    "isDuo",
    "bookingContact",
    "bookingEmail",
    "ean",
    "extraData",
    "withdrawalDetails",
    "durationMinutes",
    "withdrawalDelay",
    "withdrawalType",
    "idAtProvider",
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
            assert (
                stock.price is not None
            )  # helps mypy, not sure but it would crash in check_stock_price if None - TODO: check
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
    if (
        offer_price_limitation_rule
        and offer.validation is not OfferValidationStatus.DRAFT
        and not offer.ean
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


def _get_number_of_existing_stocks(offer_id: int) -> int:
    return models.Stock.query.filter_by(offerId=offer_id).filter(models.Stock.isSoftDeleted == False).count()


def check_stocks_quantity(quantity: int) -> None:
    if quantity > models.Offer.MAX_STOCKS_PER_OFFER:
        raise api_errors.ApiErrors(
            {"stocks": [f"Le nombre maximum de stocks par offre est de {models.Offer.MAX_STOCKS_PER_OFFER}"]},
            status_code=400,
        )


def check_stocks_quantity_with_previous_offer_stock(
    stocks_to_create: list[serialization.StockCreationBodyModel] | list[serialization.StockEditionBodyModel],
    offer: models.Offer,
) -> None:
    if stocks_to_create:
        number_of_existing_stocks = _get_number_of_existing_stocks(offer.id)
        quantity = number_of_existing_stocks + len(stocks_to_create)
        check_stocks_quantity(quantity)


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


def check_can_input_id_at_provider_for_this_venue(
    venue_id: int,
    id_at_provider: str | None,
    offer_id: int | None = None,
) -> None:
    """
    Raise a validation error if `id_at_provider` is already used to identify another venue offer.
    """
    if not id_at_provider:
        return

    id_at_provider_is_taken = repository.is_id_at_provider_taken_by_another_venue_offer(
        venue_id=venue_id,
        id_at_provider=id_at_provider,
        offer_id=offer_id,
    )

    if id_at_provider_is_taken:
        raise exceptions.IdAtProviderAlreadyTakenByAnotherVenueOffer(id_at_provider)


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
    *,
    accepted_types: tuple = ACCEPTED_THUMBNAIL_FORMATS,
    min_width: int | None = MIN_THUMBNAIL_WIDTH,
    min_height: int | None = MIN_THUMBNAIL_HEIGHT,
    max_width: int | None = None,
    max_height: int | None = None,
    max_size: int = MAX_THUMBNAIL_SIZE,
) -> None:
    check_image_size(image_as_bytes, max_size)
    try:
        # to raise an error when PIL warns for a possible decompression bomb
        # as this warning always lead to the pod being out of memory
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        image = Image.open(BytesIO(image_as_bytes))
    except UnidentifiedImageError:
        raise exceptions.UnidentifiedImage()
    except Exception:
        raise exceptions.ImageValidationError()
    assert image.format is not None  # helps mypy

    if image.format.lower() not in accepted_types:
        raise exceptions.UnacceptedFileType(accepted_types, image.format)

    if min_width is not None and image.width < min_width or min_height is not None and image.height < min_height:
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

    set_email = in_data.get("contactEmail", offer.contactEmail)
    set_phone = in_data.get("contactPhone", offer.contactPhone)
    set_url = in_data.get("contactUrl", offer.contactUrl)
    set_form = in_data.get("contactForm", offer.contactForm)

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


def check_url_is_coherent_with_subcategory(subcategory: subcategories.Subcategory, url: HttpUrl | str | None) -> None:
    if url and subcategory.is_offline_only:
        raise api_errors.ApiErrors(
            {"url": [f'Une offre de sous-catégorie "{subcategory.pro_label}" ne peut contenir un champ `url`']}
        )

    if not url and subcategory.is_online_only:
        raise api_errors.ApiErrors(
            {"url": [f'Une offre de catégorie "{subcategory.pro_label}" doit contenir un champ `url`']}
        )


def check_url_and_offererAddress_are_not_both_set(
    url: HttpUrl | str | None, offererAddress: offerers_models.OffererAddress | None
) -> None:
    """
    An offer is either:
        - digital -> `url` is not null or empty & `offererAddress=None`
        - physicial -> `offererAddress` is not null and `url=None`
    """
    if url and offererAddress is not None:
        raise api_errors.ApiErrors({"offererAddress": ["Une offre numérique ne peut pas avoir d'adresse"]})

    if not url and offererAddress is None:
        raise api_errors.ApiErrors({"offererAddress": ["Une offre physique doit avoir une adresse"]})


def check_can_input_id_at_provider_for_this_price_category(
    offer_id: int,
    id_at_provider: str,
    price_category_id: int | None = None,
) -> None:
    id_at_provider_is_taken = repository.is_id_at_provider_taken_by_another_offer_price_category(
        offer_id,
        id_at_provider,
        price_category_id,
    )

    if id_at_provider_is_taken:
        raise exceptions.IdAtProviderAlreadyTakenByAnotherOfferPriceCategory(id_at_provider)


def check_can_input_id_at_provider_for_this_stock(
    offer_id: int,
    id_at_provider: str,
    stock_id: int | None = None,
) -> None:
    id_at_provider_is_taken = repository.is_id_at_provider_taken_by_another_offer_stock(
        offer_id,
        id_at_provider,
        stock_id,
    )

    if id_at_provider_is_taken:
        raise exceptions.IdAtProviderAlreadyTakenByAnotherOfferStock(id_at_provider)


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


def check_offer_withdrawal(
    *,
    withdrawal_type: models.WithdrawalTypeEnum | None,
    withdrawal_delay: int | None,
    subcategory_id: str,
    booking_contact: str | None,
    provider: providers_models.Provider | None,
    venue_provider: providers_models.VenueProvider | None = None,
) -> None:
    is_offer_withdrawable = subcategory_id in subcategories.WITHDRAWABLE_SUBCATEGORIES
    if is_offer_withdrawable and withdrawal_type is None:
        raise exceptions.WithdrawableEventOfferMustHaveWithdrawal()

    if is_offer_withdrawable and not booking_contact:
        raise exceptions.WithdrawableEventOfferMustHaveBookingContact()

    if withdrawal_type == models.WithdrawalTypeEnum.NO_TICKET and withdrawal_delay is not None:
        raise exceptions.NoDelayWhenEventWithdrawalTypeHasNoTicket()

    if (
        withdrawal_type in (models.WithdrawalTypeEnum.ON_SITE, models.WithdrawalTypeEnum.BY_EMAIL)
        and withdrawal_delay is None
    ):
        raise exceptions.EventWithTicketMustHaveDelay()

    # Only providers that have set a ticketing system at provider level or at venue level
    # can create offers with in app Withdrawal
    if withdrawal_type == models.WithdrawalTypeEnum.IN_APP:
        has_ticketing_system_at_provider_level = provider and provider.hasTicketingService
        has_ticketing_system_at_venue_level = venue_provider and venue_provider.hasTicketingService
        if not (has_ticketing_system_at_provider_level or has_ticketing_system_at_venue_level):
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
) -> list[datetime.datetime]:
    if not (beginning and booking_limit_datetime):  # nothing to check
        return []

    if stock:
        if isinstance(stock, educational_models.CollectiveStock):
            offer = stock.collectiveOffer
        else:
            offer = stock.offer

        reference_tz = offer.venue.timezone
        if offer.offererAddress and not isinstance(stock, educational_models.CollectiveStock):
            reference_tz = offer.offererAddress.address.timezone
        elif offer.venue.offererAddress:
            reference_tz = offer.venue.offererAddress.address.timezone

        if reference_tz is not None:  # update to timezone
            beginning = date.default_timezone_to_local_datetime(beginning, reference_tz)
            booking_limit_datetime = date.default_timezone_to_local_datetime(booking_limit_datetime, reference_tz)
    if booking_limit_datetime > beginning:
        raise exceptions.BookingLimitDatetimeTooLate()
    return [beginning, booking_limit_datetime]


def check_offer_extra_data(
    subcategory_id: str,
    extra_data: models.OfferExtraData | None,
    venue: offerers_models.Venue,
    is_from_private_api: bool,
    offer: models.Offer | None = None,
    ean: str | None = None,
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

        if field == "ean":
            if not ean:
                errors.add_error(field, "Ce champ est obligatoire")
            continue

        if not extra_data.get(field):
            errors.add_error(field, "Ce champ est obligatoire")

    try:
        _check_offer_has_product(offer)
    except exceptions.OfferWithProductShouldNotUpdateExtraData as e:
        errors.add_client_error(e)

    try:
        if ean:
            _check_ean_field(ean)

            offer_id = offer.id if offer else None
            check_other_offer_with_ean_does_not_exist(ean, venue, offer_id)
    except (exceptions.EanFormatException, exceptions.OfferAlreadyExists) as e:
        errors.add_client_error(e)

    try:
        _check_value_is_allowed(extra_data, ExtraDataFieldEnum.MUSIC_TYPE, music.MUSIC_TYPES_LABEL_BY_CODE)
        _check_value_is_allowed(extra_data, ExtraDataFieldEnum.MUSIC_SUB_TYPE, music.MUSIC_SUB_TYPES_BY_CODE)
        _check_value_is_allowed(extra_data, ExtraDataFieldEnum.SHOW_TYPE, show.SHOW_TYPES_LABEL_BY_CODE)
        _check_value_is_allowed(extra_data, ExtraDataFieldEnum.SHOW_SUB_TYPE, show.SHOW_SUB_TYPES_BY_CODE)
    except exceptions.ExtraDataValueNotAllowed as e:
        errors.add_client_error(e)

    if errors.errors:
        raise errors


def check_product_for_venue_and_subcategory(
    product: models.Product | None,
    subcategory_id: str | None,
    venue_type_code: VenueTypeCode,
) -> None:
    if venue_type_code != VenueTypeCode.RECORD_STORE:
        return

    if subcategory_id not in [
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    ]:
        return
    if product is not None:
        return
    raise exceptions.ProductNotFoundForOfferCreation(
        ExtraDataFieldEnum.EAN.value, "EAN non reconnu. Assurez-vous qu'il n'y ait pas d'erreur de saisie."
    )


def check_other_offer_with_ean_does_not_exist(
    ean: str | None, venue: offerers_models.Venue, offer_id: int | None = None
) -> None:
    if repository.has_active_offer_with_ean(ean, venue, offer_id):
        if ean:
            raise exceptions.OfferAlreadyExists("ean")


def check_offer_name_does_not_contain_ean(offer_name: str) -> None:
    if re.search(r"\d{13}", offer_name):
        raise exceptions.EanInOfferNameException()


def _check_offer_has_product(offer: models.Offer | None) -> None:
    if FeatureToggle.WIP_EAN_CREATION.is_active() and offer and offer.product is not None:
        raise exceptions.OfferWithProductShouldNotUpdateExtraData()


def check_product_cgu_and_offerer(
    product: models.Product | None, ean: str, offerer: offerers_models.Offerer | None
) -> None:
    if product is None:
        raise api_errors.ApiErrors(
            errors={
                "ean": ["EAN non reconnu. Assurez-vous qu'il n'y ait pas d'erreur de saisie."],
            },
            status_code=422,
        )
    if offerer is None:
        raise api_errors.ApiErrors(
            errors={
                "ean": ["Structure non reconnue."],
            },
            status_code=422,
        )
    not_virtual_venues = [venue for venue in offerer.managedVenues if venue.isVirtual is False]
    # Context give only the offerer, not the specific venue on wich the offer is created.
    # We can only check the existence of an offer with this EAN if the offerer has one venue.
    if len(not_virtual_venues) == 1:
        try:
            check_other_offer_with_ean_does_not_exist(ean, not_virtual_venues[0])
        except exceptions.OfferAlreadyExists:
            raise api_errors.ApiErrors(
                errors={"ean": ["Une offre avec cet EAN existe déjà. Vous pouvez la retrouver dans l'onglet Offres."]},
                status_code=422,
            )
    if not product.isGcuCompatible:
        raise api_errors.ApiErrors(
            errors={
                "ean": ["EAN invalide. Ce produit n'est pas conforme à nos CGU."],
            },
            status_code=422,
        )


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


def _check_ean_field(ean: str) -> None:
    if not ean:
        return

    if not isinstance(ean, str):
        raise exceptions.EanFormatException("ean", "L'EAN doit être une chaîne de caractères")

    if not ean.isdigit() or not len(ean) == 13:
        raise exceptions.EanFormatException("ean", "L'EAN doit être composé de 13 chiffres")


def check_offer_is_from_current_cinema_provider(offer: models.Offer) -> None:
    venue_cinema_pivot = providers_models.CinemaProviderPivot.query.filter(
        providers_models.CinemaProviderPivot.venueId == offer.venueId
    ).one_or_none()
    if not venue_cinema_pivot or offer.lastProviderId != venue_cinema_pivot.providerId:
        raise exceptions.UnexpectedCinemaProvider()


def check_is_duo_compliance(is_duo: bool | None, subcategory: subcategories.Subcategory) -> None:
    if is_duo and not subcategory.can_be_duo:
        raise exceptions.OfferCannotBeDuo()


def check_accessibility_compliance(
    audio_disability_compliant: bool | None,
    mental_disability_compliant: bool | None,
    motor_disability_compliant: bool | None,
    visual_disability_compliant: bool | None,
) -> None:
    fields = (
        audio_disability_compliant,
        mental_disability_compliant,
        motor_disability_compliant,
        visual_disability_compliant,
    )
    if None in fields:
        raise exceptions.OfferMustHaveAccessibility()


def check_publication_date(offer: models.Offer, publication_date: datetime.datetime | None) -> None:
    if publication_date is None:
        return

    if offer.publicationDate is not None:
        msg = "Cette offre est déjà programmée pour être publiée dans le futur"
        raise exceptions.FutureOfferException("publication_date", msg)

    if not offer.subcategory.is_event:
        msg = "Seules les offres d’événements peuvent avoir une date de publication"
        raise exceptions.FutureOfferException("publication_date", msg)

    if publication_date.minute not in [0, 15, 30, 45]:
        msg = "L’heure de publication ne peut avoir une précision supérieure au quart d'heure"
        raise exceptions.FutureOfferException("publication_date", msg)

    now = datetime.datetime.utcnow()
    if publication_date < now:
        msg = "Impossible de sélectionner une date de publication dans le passé"
        raise exceptions.FutureOfferException("publication_date", msg)

    years = 2
    if publication_date > now + relativedelta(years=years):
        msg = f"Impossible sélectionner une date de publication plus de {years} ans en avance"
        raise exceptions.FutureOfferException("publication_date", msg)


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
        .filter(sa.func.ROW(models.PriceCategoryLabel.label, models.PriceCategory.price).in_(new_labels_and_prices))
        .first()
    )

    if existing_price_category:
        raise api_errors.ApiErrors(
            {"priceCategories": [f"The price category {existing_price_category.label} already exists"]}
        )


class OfferValidationError(Exception):
    field = "all"
    msg = "Invalid"


def check_offerer_is_eligible_for_headline_offers(offerer_id: int) -> None:
    # FIXME: ogeber 03.01.2025 - when venue regularisation is done, we can change this validation by
    # raising the OffererCanNotHaveHeadlineOffer only if
    # offerers_models.Venue.query.filter(
    #     offerers_models.Venue.managingOffererId == offerer_id
    #     offerers_models.Venue.isPermanent.is_(True)
    # ).count()
    # is superior to 1 (as permanent & virtual venues won't exist anymore)

    venues = offerers_models.Venue.query.filter(offerers_models.Venue.managingOffererId == offerer_id).all()

    permanent_venues = [v for v in venues if v.isPermanent and not v.isVirtual]
    non_permanent_venues = [v for v in venues if not v.isPermanent and not v.isVirtual]

    if len(permanent_venues) != 1 or len(non_permanent_venues) > 0:
        raise exceptions.OffererCanNotHaveHeadlineOffer()


def check_offer_is_eligible_to_be_headline(offer: models.Offer) -> None:
    if offer.status != OfferStatus.ACTIVE:
        raise exceptions.InactiveOfferCanNotBeHeadline()
    if not offer.images:
        raise exceptions.OfferWithoutImageCanNotBeHeadline()
    # FIXME: ogeber 03.01.2025 - when venue regularisation is done, this
    # validation can be removed and virtual offers can be made headline
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT[offer.subcategoryId]
    if subcategory.is_online_only:
        raise exceptions.VirtualOfferCanNotBeHeadline()


def _opening_hours_base_checks(offer: models.Offer) -> None:
    if not offer.subcategory.can_have_opening_hours:
        raise exceptions.OfferEditionBaseException(
            "offer.subcategory", f"`{offer.subcategory.id}` subcategory does not allow opening hours"
        )

    if repository.offer_has_timestamped_stocks(offer.id):
        raise exceptions.OfferEditionBaseException("offer", f"Offer #{offer.id} already has timestamped stocks")


def check_offer_can_have_opening_hours(
    offer: models.Offer,
) -> None:
    _opening_hours_base_checks(offer)

    if offer.hasOpeningHours:
        raise exceptions.OfferEditionBaseException("offer", f"Offer #{offer.id} already has opening hours")


def check_event_opening_hours_can_be_updated(
    offer: models.Offer, opening_hours: models.EventOpeningHours, body: schemas.UpdateEventOpeningHoursModel
) -> None:
    """Check that an event opening hours can be updated, meaning:
    * the opening hours to be updated is not (soft) deleted
    * nothing can be changed if the event has already ended
    * the new start date can't be after the end date (current or old)
    * the new start date can't be too close (less than 48 hours - because
      users must still be able to cancel)
    * the new end date can't less than 48 hours from now (same as above)
    """

    def _ensure_datetime_has_tz(dt: datetime.datetime | None) -> datetime.datetime | None:
        return dt.replace(tzinfo=datetime.timezone.utc) if dt and not dt.tzinfo else dt

    now = datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
    two_days_from_now = now + datetime.timedelta(hours=48)

    current_end = _ensure_datetime_has_tz(opening_hours.endDatetime)
    new_end = _ensure_datetime_has_tz(body.endDatetime)
    new_start = _ensure_datetime_has_tz(body.startDatetime)

    _opening_hours_base_checks(offer)

    if opening_hours.isSoftDeleted:
        raise exceptions.EventOpeningHoursException(field="event", msg="event opening hours has been deleted")

    if current_end and current_end <= now:
        raise exceptions.EventOpeningHoursException(
            field="event.endDatetime",
            msg="event opening hours cannot be updated: end date has already passed (end date update)",
        )

    if new_start:
        assert new_start

        if new_start <= two_days_from_now:
            raise exceptions.EventOpeningHoursException(
                field="event.startDatetime",
                msg="event opening hours cannot be updated: new start is too soon (too close to current end)",
            )

        new_start_date_after_current_end = current_end and new_start >= current_end
        if not new_end and new_start_date_after_current_end:
            raise exceptions.EventOpeningHoursException(
                field="event.startDatetime",
                msg="event opening hours cannot be updated: cannot start after ending (start date update)",
            )

    if new_end and new_end <= two_days_from_now:
        raise exceptions.EventOpeningHoursException(
            field="event.endDatetime", msg="event opening hours cannot be updated: new end is too soon"
        )
