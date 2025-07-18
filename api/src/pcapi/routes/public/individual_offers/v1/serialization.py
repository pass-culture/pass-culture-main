import copy
import datetime
import decimal
import enum
import logging
import typing

import pydantic.v1 as pydantic_v1
from flask import request
from pydantic.v1 import validator
from pydantic.v1.utils import GetterDict
from spectree import BaseFile

import pcapi.routes.public.serialization.accessibility as accessibility_serialization
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.categories.genres import show
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import constants
from pcapi.core.providers.constants import TITELIVE_MUSIC_TYPES
from pcapi.models import offer_mixin
from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants import descriptions
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.public.individual_offers.v1.base_serialization import IndexPaginationQueryParams
from pcapi.routes.public.serialization.utils import StrEnum
from pcapi.routes.serialization import BaseModel
from pcapi.serialization import utils as serialization_utils


logger = logging.getLogger(__name__)


ALLOWED_PRODUCT_SUBCATEGORIES = [
    subcategories.ABO_BIBLIOTHEQUE,
    subcategories.ABO_CONCERT,
    subcategories.ABO_LIVRE_NUMERIQUE,
    subcategories.ABO_MEDIATHEQUE,
    subcategories.ABO_PLATEFORME_MUSIQUE,
    subcategories.ABO_PLATEFORME_VIDEO,
    subcategories.ABO_PRATIQUE_ART,
    subcategories.ABO_PRESSE_EN_LIGNE,
    subcategories.ABO_SPECTACLE,
    subcategories.ACHAT_INSTRUMENT,
    subcategories.APP_CULTURELLE,
    subcategories.AUTRE_SUPPORT_NUMERIQUE,
    subcategories.CAPTATION_MUSIQUE,
    subcategories.CARTE_JEUNES,
    subcategories.CARTE_MUSEE,
    subcategories.LIVRE_AUDIO_PHYSIQUE,
    subcategories.LIVRE_NUMERIQUE,
    subcategories.LOCATION_INSTRUMENT,
    subcategories.PARTITION,
    subcategories.PLATEFORME_PRATIQUE_ARTISTIQUE,
    subcategories.PODCAST,
    subcategories.PRATIQUE_ART_VENTE_DISTANCE,
    subcategories.SPECTACLE_ENREGISTRE,
    subcategories.SUPPORT_PHYSIQUE_FILM,
    subcategories.TELECHARGEMENT_LIVRE_AUDIO,
    subcategories.TELECHARGEMENT_MUSIQUE,
    subcategories.VISITE_VIRTUELLE,
    subcategories.VOD,
]


MusicTypeEnum = StrEnum(  # type: ignore[call-overload]
    "MusicTypeEnum (deprecated)",
    {music_sub_type_slug: music_sub_type_slug for music_sub_type_slug in music.MUSIC_SUB_TYPES_BY_SLUG},
)

TiteliveMusicTypeEnum = StrEnum(  # type: ignore[call-overload]
    "TiteliveMusicTypeEnum", {music_type: music_type for music_type in constants.GTL_ID_BY_TITELIVE_MUSIC_GENRE}
)

TiteliveEventMusicTypeEnum = StrEnum(  # type: ignore[call-overload]
    "TiteliveEventMusicTypeEnum",
    {
        constants.TITELIVE_MUSIC_GENRES_BY_GTL_ID[music_type.gtl_id]: constants.TITELIVE_MUSIC_GENRES_BY_GTL_ID[
            music_type.gtl_id
        ]
        for music_type in TITELIVE_MUSIC_TYPES
        if music_type.can_be_event
    },
)

ShowTypeEnum = StrEnum(  # type: ignore[call-overload]
    "ShowTypeEnum",
    {show_sub_type_slug: show_sub_type_slug for show_sub_type_slug in show.SHOW_SUB_TYPES_BY_SLUG},
)

EventCategoryEnum = StrEnum(  # type: ignore[call-overload]
    "CategoryEnum", {subcategory_id: subcategory_id for subcategory_id in subcategories.EVENT_SUBCATEGORIES}
)

ProductCategoryEnum = StrEnum(  # type: ignore[call-overload]
    "CategoryEnum", {subcategory.id: subcategory.id for subcategory in ALLOWED_PRODUCT_SUBCATEGORIES}
)

if typing.TYPE_CHECKING:
    offer_price_model = pydantic_v1.StrictInt
else:
    offer_price_model = pydantic_v1.conint(strict=True, ge=0, le=30000)  # 300 euros


class Accessibility(serialization.ConfiguredBaseModel):
    """Accessibility for people with disabilities."""

    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool


class AccessibilityResponse(serialization.ConfiguredBaseModel):
    """Accessibility for people with disabilities."""

    audio_disability_compliant: bool | None = fields.AUDIO_DISABILITY_COMPLIANT
    mental_disability_compliant: bool | None = fields.MENTAL_DISABILITY_COMPLIANT
    motor_disability_compliant: bool | None = fields.MOTOR_DISABILITY_COMPLIANT
    visual_disability_compliant: bool | None = fields.VISUAL_DISABILITY_COMPLIANT


class AddressLabel(pydantic_v1.ConstrainedStr):
    min_length = 1
    max_length = 200


class AddressLocation(serialization.ConfiguredBaseModel):
    """
    If your offer location is different from the venue location
    """

    type: typing.Literal["address"] = "address"
    venue_id: int = fields.VENUE_ID
    address_id: int = fields.ADDRESS_ID
    address_label: AddressLabel | None = fields.ADDRESS_LABEL

    @classmethod
    def build_from_offer(cls, offer: offers_models.Offer) -> "AddressLocation":
        if not offer.offererAddress:
            raise ValueError("offer.offererAddress is `None`")

        if offer.offererAddress.addressId is None:
            raise ValueError("offer.offererAddress.addressId is `None`")

        return cls(
            type="address",
            venue_id=offer.venueId,
            address_id=offer.offererAddress.addressId,
            address_label=offer.offererAddress.label,  # type: ignore[arg-type]
        )


class PhysicalLocation(serialization.ConfiguredBaseModel):
    """
    If your offer location is your venue
    """

    type: typing.Literal["physical"] = "physical"
    venue_id: int = fields.VENUE_ID


class DigitalLocation(serialization.ConfiguredBaseModel):
    """
    If your offer has no physical location as it is a digital product
    """

    type: typing.Literal["digital"] = "digital"
    venue_id: int = fields.VENUE_ID
    url: pydantic_v1.HttpUrl = pydantic_v1.Field(
        ...,
        description="Link users will be redirected to after booking this offer. You may include '{token}', '{email}' and/or '{offerId}' in the URL, which will be replaced respectively by the booking token (use this token to confirm the offer - see API Contremarque), the email of the user who booked the offer and the created offer id",
        example="https://example.com?token={token}&email={email}&offerId={offerId}",
    )


class ExtraDataModel(serialization.ConfiguredBaseModel):
    author: str | None = pydantic_v1.Field(example="Jane Doe")
    ean: str | None = fields.EAN
    musicType: TiteliveMusicTypeEnum | MusicTypeEnum | None  # type: ignore[valid-type]
    performer: str | None = pydantic_v1.Field(example="Jane Doe")
    stageDirector: str | None = pydantic_v1.Field(example="Jane Doe")
    showType: ShowTypeEnum | None  # type: ignore[valid-type]
    speaker: str | None = pydantic_v1.Field(example="Jane Doe")
    visa: str | None = pydantic_v1.Field(example="140843")


class CategoryRelatedFields(ExtraDataModel):
    subcategory_id: str = pydantic_v1.Field(alias="category")


CATEGORY_RELATED_FIELD_DESCRIPTION = (
    "Cultural category the offer belongs to. According to the category, some fields may or must be specified."
)
CATEGORY_RELATED_FIELD = pydantic_v1.Field(..., description=CATEGORY_RELATED_FIELD_DESCRIPTION)
EXTERNAL_TICKET_OFFICE_URL_FIELD = pydantic_v1.Field(
    None,
    description="Link displayed to users wishing to book the offer but who do not have credit.",
    example="https://example.com",
)
WITHDRAWAL_DETAILS_FIELD = pydantic_v1.Field(
    None,
    description="Further information that will be provided to attendees to ease the offer collection.",
    example="Opening hours, specific office, collection period, access code, email announcement...",
    alias="itemCollectionDetails",
)


class ImageBody(serialization.ConfiguredBaseModel):
    """Image illustrating the offer. Offers with images are more likely to be booked."""

    credit: str | None = fields.IMAGE_CREDIT
    file: str = fields.IMAGE_FILE


class ImageResponse(serialization.ConfiguredBaseModel):
    """Image illustrating the offer. Offers with images are more likely to be booked."""

    credit: str | None = fields.IMAGE_CREDIT
    url: str = fields.IMAGE_URL


class OfferCreationBase(serialization.ConfiguredBaseModel):
    accessibility: Accessibility
    booking_contact: pydantic_v1.EmailStr | None = fields.OFFER_BOOKING_CONTACT
    booking_email: pydantic_v1.EmailStr | None = fields.OFFER_BOOKING_EMAIL
    category_related_fields: CategoryRelatedFields = CATEGORY_RELATED_FIELD
    description: str | None = fields.OFFER_DESCRIPTION_WITH_MAX_LENGTH
    external_ticket_office_url: pydantic_v1.HttpUrl | None = EXTERNAL_TICKET_OFFICE_URL_FIELD
    image: ImageBody | None
    enable_double_bookings: bool | None = fields.OFFER_ENABLE_DOUBLE_BOOKINGS_WITH_DEFAULT
    name: str = fields.OFFER_NAME_WITH_MAX_LENGTH
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD
    id_at_provider: str | None = fields.ID_AT_PROVIDER_WITH_MAX_LENGTH
    publication_datetime: datetime.datetime | serialization_utils.NOW_LITERAL | None = (
        fields.OFFER_PUBLICATION_DATETIME_WITH_DEFAULT
    )
    booking_allowed_datetime: datetime.datetime | None = fields.OFFER_BOOKING_ALLOWED_DATETIME

    _validate_publicationDatetime = serialization_utils.validate_datetime(
        "publication_datetime",
        always=True,  # to convert default literal `"now"` into an actual datetime
    )
    _validate_bookingAllowedDatetime = serialization_utils.validate_datetime("booking_allowed_datetime")

    class Config:
        extra = "forbid"


class Method(enum.Enum):
    create = "create"
    read = "read"
    edit = "edit"


def compute_category_fields_model(
    subcategory: subcategories.Subcategory, method: Method
) -> type[CategoryRelatedFields]:
    """
    Create dynamic pydantic_v1 models to indicate which fields are available for the chosen subcategory,
    without duplicating categories declaration.
    If musicType (resp showType) field is applicable, we expose only the musicSubType (resp showSubType) information
    because it also contains musicType (resp showType) information. And we use the simpler musicType (resp showType) alias.
    """
    specific_fields: dict[typing.Any, typing.Any] = {}
    for field_name, conditional_field in subcategory.conditional_fields.items():
        if field_name not in ExtraDataModel.__fields__:
            continue
        is_required = conditional_field.is_required_in_external_form and method == Method.create
        model_field = ExtraDataModel.__fields__[field_name]
        specific_fields[field_name] = (model_field.type_, ... if is_required else model_field.default)

    specific_fields["subcategory_id"] = (
        typing.Literal[subcategory.id],
        pydantic_v1.Field(alias="category"),
    )

    model = pydantic_v1.create_model(f"{subcategory.id}_{method.value}", **specific_fields)
    model.__doc__ = subcategory.pro_label
    model.__config__.allow_population_by_field_name = True
    return model


def serialize_extra_data(offer: offers_models.Offer) -> CategoryRelatedFields:
    category_fields_model = (product_category_reading_models | event_category_reading_models)[offer.subcategoryId]
    serialized_data = copy.deepcopy(offer.extraData or {})

    if offer.ean:
        serialized_data["ean"] = offer.ean

    # Convert musicSubType (resp showSubType) code to musicType slug (resp showType slug)

    OTHER_TYPE_CODE = "-1"
    music_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value, None)
    music_sub_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.MUSIC_SUB_TYPE.value, None)
    gtl_id = serialized_data.pop(subcategories.ExtraDataFieldEnum.GTL_ID.value, None)

    # FIXME (mageoffray, 2023-12-14): some historical offers have no musicSubType and only musicType.
    # We should migrate our musicType|musicSubType to titelive music types. This migration will include
    # offers without musicSubType
    if music_type and not music_sub_type:
        music_sub_type = OTHER_TYPE_CODE

    if music_sub_type == OTHER_TYPE_CODE and gtl_id is not None:
        # Infer more precise music type from gtl_id
        serialized_data["musicType"] = TiteliveMusicTypeEnum(
            constants.TITELIVE_MUSIC_GENRES_BY_GTL_ID[gtl_id[:2] + "0" * 6]
        )
    elif music_sub_type:
        serialized_data["musicType"] = MusicTypeEnum(music.MUSIC_SUB_TYPES_BY_CODE[int(music_sub_type)].slug)

    # FIXME (mageoffray, 2023-12-14): some historical offers have no showSubType and only showType.
    show_sub_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.SHOW_SUB_TYPE.value, None)
    show_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.SHOW_TYPE.value, None)
    if show_type and not show_sub_type:
        show_sub_type = OTHER_TYPE_CODE
    if show_sub_type:
        serialized_data["showType"] = ShowTypeEnum(show.SHOW_SUB_TYPES_BY_CODE[int(show_sub_type)].slug)

    return category_fields_model(**serialized_data, subcategory_id=offer.subcategory.id)  # type: ignore[misc, call-arg]


def deserialize_extra_data(
    category_related_fields: CategoryRelatedFields | None,
    initial_extra_data: offers_models.OfferExtraData | None = None,
    venue_id: int | None = None,
) -> dict[str, str]:
    extra_data: dict = initial_extra_data or {}  # type: ignore[assignment]
    if not category_related_fields:
        return extra_data
    for field_name, field_value in category_related_fields.dict(exclude_unset=True).items():
        if field_name in ("subcategory_id", "ean"):
            continue
        if field_name == subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value:
            # Convert musicType slug to musicType and musicSubType codes
            if field_value in TiteliveMusicTypeEnum.__members__:
                extra_data["gtl_id"] = constants.GTL_ID_BY_TITELIVE_MUSIC_GENRE[field_value]
                music_slug = constants.MUSIC_SLUG_BY_GTL_ID[extra_data["gtl_id"]]
                extra_data["musicType"] = str(music.MUSIC_TYPES_BY_SLUG[music_slug].code)
                extra_data["musicSubType"] = str(music.MUSIC_SUB_TYPES_BY_SLUG[music_slug].code)
            else:
                extra = {
                    "venue": venue_id if venue_id else "",
                    "field_name": field_name,
                    "field_value": field_value.value,
                    "enum_used": type(field_value).__name__,
                }

                logger.info("offer: using old music type", extra=extra)

                extra_data["musicSubType"] = str(music.MUSIC_SUB_TYPES_BY_SLUG[field_value].code)
                extra_data["musicType"] = str(music.MUSIC_TYPES_BY_SLUG[field_value].code)
                extra_data["gtl_id"] = constants.MUSIC_SLUG_TO_GTL_ID[field_value]
        elif field_name == subcategories.ExtraDataFieldEnum.SHOW_TYPE.value:
            # Convert showType slug to showType and showSubType codes
            extra_data["showSubType"] = str(show.SHOW_SUB_TYPES_BY_SLUG[field_value].code)
            extra_data["showType"] = str(show.SHOW_TYPES_BY_SLUG[field_value].code)
        else:
            extra_data[field_name] = field_value
    return extra_data


product_category_creation_models = {
    subcategory.id: compute_category_fields_model(subcategory, Method.create)
    for subcategory in ALLOWED_PRODUCT_SUBCATEGORIES
    if not subcategory.is_event and subcategory.is_selectable
}
product_category_edition_models = {
    subcategory.id: compute_category_fields_model(subcategory, Method.edit)
    for subcategory in ALLOWED_PRODUCT_SUBCATEGORIES
    if not subcategory.is_event and subcategory.is_selectable
}
product_category_reading_models = {
    subcategory.id: compute_category_fields_model(subcategory, Method.read)
    for subcategory in subcategories.ALL_SUBCATEGORIES
    if not subcategory.is_event
}

event_category_creation_models = {
    subcategory.id: compute_category_fields_model(subcategory, Method.create)
    for subcategory in subcategories.ALL_SUBCATEGORIES
    if subcategory.is_event and subcategory.is_selectable
}
event_category_edition_models = {
    subcategory.id: compute_category_fields_model(subcategory, Method.edit)
    for subcategory in subcategories.ALL_SUBCATEGORIES
    if subcategory.is_event and subcategory.is_selectable
}
event_category_reading_models = {
    subcategory.id: compute_category_fields_model(subcategory, Method.read)
    for subcategory in subcategories.ALL_SUBCATEGORIES
    if subcategory.is_event
}


if typing.TYPE_CHECKING:
    product_category_creation_fields = CategoryRelatedFields
    product_category_reading_fields = CategoryRelatedFields
    event_category_creation_fields = CategoryRelatedFields
    event_category_edition_fields = CategoryRelatedFields
    event_category_reading_fields = CategoryRelatedFields
    product_category_edition_fields = CategoryRelatedFields
else:
    product_category_creation_fields = typing.Annotated[
        typing.Union[tuple(product_category_creation_models.values())],
        pydantic_v1.Field(description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]
    product_category_reading_fields = typing.Annotated[
        typing.Union[tuple(product_category_reading_models.values())],
        pydantic_v1.Field(discriminator="subcategory_id", description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]
    product_category_edition_fields = typing.Annotated[
        typing.Union[tuple(product_category_edition_models.values())],
        pydantic_v1.Field(discriminator="subcategory_id"),
    ]
    event_category_creation_fields = typing.Annotated[
        typing.Union[tuple(event_category_creation_models.values())],
        pydantic_v1.Field(discriminator="subcategory_id", description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]
    event_category_edition_fields = typing.Annotated[
        typing.Union[tuple(event_category_edition_models.values())],
        pydantic_v1.Field(discriminator="subcategory_id"),
    ]
    event_category_reading_fields = typing.Annotated[
        typing.Union[tuple(event_category_reading_models.values())],
        pydantic_v1.Field(discriminator="subcategory_id", description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]

UNLIMITED_LITERAL = typing.Literal["unlimited"]


class BaseStockCreation(serialization.ConfiguredBaseModel):
    quantity: pydantic_v1.StrictInt | UNLIMITED_LITERAL = fields.QUANTITY

    @pydantic_v1.validator("quantity")
    def quantity_must_be_in_range(cls, quantity: int | str) -> int | str:
        if isinstance(quantity, int):
            if quantity < 0:
                raise ValueError("Value must be positive")
            if quantity > offers_models.Stock.MAX_STOCK_QUANTITY:
                raise ValueError(f"Value must be less than {offers_models.Stock.MAX_STOCK_QUANTITY}")

        return quantity


def deserialize_quantity(quantity: int | UNLIMITED_LITERAL | None) -> int | None:
    if quantity == "unlimited":
        return None
    return quantity


class BaseStockEdition(serialization.ConfiguredBaseModel):
    booking_limit_datetime: datetime.datetime | None = fields.BOOKING_LIMIT_DATETIME
    quantity: pydantic_v1.NonNegativeInt | UNLIMITED_LITERAL | None = fields.QUANTITY

    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")

    @pydantic_v1.validator("quantity")
    def quantity_must_be_in_range(cls, quantity: int | str | None) -> int | str | None:
        if isinstance(quantity, int):
            if quantity < 0:
                raise ValueError("Value must be positive")
            if quantity > offers_models.Stock.MAX_STOCK_QUANTITY:
                raise ValueError(f"Value must be less than {offers_models.Stock.MAX_STOCK_QUANTITY}")

        return quantity

    class Config:
        extra = "forbid"


class DecimalPriceGetterDict(GetterDict):
    def get(self, key: str, default: typing.Any | None = None) -> typing.Any:
        if key == "price" and isinstance(self._obj.price, decimal.Decimal):
            return finance_utils.to_cents(self._obj.price)
        return super().get(key, default)


class OfferName(pydantic_v1.ConstrainedStr):
    min_length = 1
    max_length = 140


class OfferEditionBase(serialization.ConfiguredBaseModel):
    accessibility: accessibility_serialization.PartialAccessibility | None = pydantic_v1.Field(
        description="Accessibility to disabled people. Leave fields undefined to keep current value"
    )
    booking_email: pydantic_v1.EmailStr | None = fields.OFFER_BOOKING_EMAIL
    booking_contact: pydantic_v1.EmailStr | None = fields.OFFER_BOOKING_CONTACT
    # TODO(jbaudet): deprecated, use publicationDatetime instead
    is_active: bool | None = pydantic_v1.Field(
        description="Set to `false` if you want to deactivate the offer. This will not cancel former bookings. "
    )
    enable_double_bookings: bool | None = fields.OFFER_ENABLE_DOUBLE_BOOKINGS_WITH_DEFAULT
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD
    image: ImageBody | None
    description: str | None = fields.OFFER_DESCRIPTION_WITH_MAX_LENGTH
    id_at_provider: str | None = fields.ID_AT_PROVIDER_WITH_MAX_LENGTH
    name: OfferName | None = fields.OFFER_NAME
    location: PhysicalLocation | DigitalLocation | AddressLocation | None = fields.OFFER_LOCATION
    publication_datetime: datetime.datetime | serialization_utils.NOW_LITERAL | None = fields.OFFER_PUBLICATION_DATETIME
    booking_allowed_datetime: datetime.datetime | None = fields.OFFER_BOOKING_ALLOWED_DATETIME

    _validate_publicationDatetime = serialization_utils.validate_datetime("publication_datetime")
    _validate_bookingAllowedDatetime = serialization_utils.validate_datetime("booking_allowed_datetime")

    class Config:
        extra = "forbid"


class BaseStockResponse(serialization.ConfiguredBaseModel):
    booking_limit_datetime: datetime.datetime | None = fields.BOOKING_LIMIT_DATETIME
    dnBookedQuantity: int = pydantic_v1.Field(..., description="Number of bookings.", example=0, alias="bookedQuantity")
    quantity: pydantic_v1.StrictInt | UNLIMITED_LITERAL = fields.QUANTITY

    @classmethod
    def build_stock(cls, stock: offers_models.Stock) -> "BaseStockResponse":
        return cls(  # type: ignore[call-arg]
            booking_limit_datetime=stock.bookingLimitDatetime,
            dnBookedQuantity=stock.dnBookedQuantity,
            quantity=stock.quantity if stock.quantity is not None else "unlimited",
        )


class OfferResponse(serialization.ConfiguredBaseModel):
    id: int
    accessibility: AccessibilityResponse
    booking_contact: str | None = fields.OFFER_BOOKING_CONTACT
    booking_email: str | None = fields.OFFER_BOOKING_EMAIL
    description: str | None = fields.OFFER_DESCRIPTION
    external_ticket_office_url: str | None = EXTERNAL_TICKET_OFFICE_URL_FIELD
    image: ImageResponse | None
    enable_double_bookings: bool | None = fields.OFFER_ENABLE_DOUBLE_BOOKINGS_WITH_DEFAULT
    location: PhysicalLocation | DigitalLocation | AddressLocation = fields.OFFER_LOCATION
    name: str = fields.OFFER_NAME
    status: offer_mixin.OfferStatus = pydantic_v1.Field(
        ...,
        description=descriptions.OFFER_STATUS_FIELD_DESCRIPTION,
        example=offer_mixin.OfferStatus.ACTIVE.name,
    )
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD
    id_at_provider: str | None = fields.ID_AT_PROVIDER
    publication_datetime: datetime.datetime | None = fields.OFFER_PUBLICATION_DATETIME
    booking_allowed_datetime: datetime.datetime | None = fields.OFFER_BOOKING_ALLOWED_DATETIME

    @classmethod
    def get_location(cls, offer: offers_models.Offer) -> PhysicalLocation | DigitalLocation | AddressLocation:
        if offer.isDigital:
            return DigitalLocation.from_orm(offer)
        if offer.offererAddressId is not None and offer.offererAddressId != offer.venue.offererAddressId:
            return AddressLocation.build_from_offer(offer)

        return PhysicalLocation.from_orm(offer)

    @classmethod
    def build_offer(cls, offer: offers_models.Offer) -> "OfferResponse":
        return cls(
            id=offer.id,
            booking_contact=offer.bookingContact,
            booking_email=offer.bookingEmail,
            description=offer.description,
            accessibility=AccessibilityResponse.from_orm(offer),
            external_ticket_office_url=offer.externalTicketOfficeUrl,
            image=offer.image,  # type: ignore[arg-type]
            enable_double_bookings=offer.isDuo,
            location=cls.get_location(offer),
            name=offer.name,
            status=offer.status,
            withdrawal_details=offer.withdrawalDetails,
            id_at_provider=offer.idAtProvider,
            publication_datetime=offer.publicationDatetime,
            booking_allowed_datetime=offer.bookingAllowedDatetime,
        )


class ProductStockResponse(BaseStockResponse):
    price: pydantic_v1.StrictInt = fields.PRICE

    @classmethod
    def build_product_stock(cls, stock: offers_models.Stock) -> "ProductStockResponse":
        stock_response = BaseStockResponse.build_stock(stock)
        return cls(price=finance_utils.to_cents(stock.price), **stock_response.dict())


class ProductOfferResponse(OfferResponse):
    category_related_fields: product_category_reading_fields
    stock: ProductStockResponse | None

    @classmethod
    def build_product_offer(cls, offer: offers_models.Offer) -> "ProductOfferResponse":
        base_offer_response = OfferResponse.build_offer(offer)
        active_stock = next((stock for stock in offer.activeStocks), None)
        return cls(
            category_related_fields=serialize_extra_data(offer),
            stock=ProductStockResponse.build_product_stock(active_stock) if active_stock else None,
            **base_offer_response.dict(),
        )


class GetOffersQueryParams(IndexPaginationQueryParams):
    venue_id: int | None = fields.VENUE_ID
    ids_at_provider: str | None = fields.IDS_AT_PROVIDER_FILTER
    address_id: int | None = fields.ADDRESS_ID

    @pydantic_v1.validator("ids_at_provider")
    def validate_ids_at_provider(cls, ids_at_provider: str) -> list[str] | None:
        if ids_at_provider:
            return ids_at_provider.split(",")
        return None


class ProductOffersResponse(serialization.ConfiguredBaseModel):
    products: list[ProductOfferResponse]


class ProductOffersByEanResponse(serialization.ConfiguredBaseModel):
    products: list[ProductOfferResponse]


class GetProductsListByEansQuery(serialization.ConfiguredBaseModel):
    eans: str = fields.EANS_FILTER
    venueId: int = fields.VENUE_ID

    @pydantic_v1.validator("eans")
    def validate_ean_list(cls, eans: str) -> list[str]:
        """The ean list must contain at least one element, at most 100
        An ean must be a 13 digit integer"""
        ean_list = eans.split(",")
        if len(ean_list) > 100:
            raise ValueError("Too many EANs")
        if len(ean_list) == 0:
            raise ValueError("EAN list must not be empty")
        for ean in ean_list:
            if not ean.isdigit():
                raise ValueError("EAN must be an integer")
            if int(ean) < 0:
                raise ValueError("EAN must be positive")
            if len(ean) != 13:
                raise ValueError("Only 13 characters EAN are accepted")
        return ean_list


class GetAvailableEANsListQuery(serialization.ConfiguredBaseModel):
    eans: str = fields.EANS_FILTER

    @pydantic_v1.validator("eans")
    def validate_ean_list(cls, eans: str) -> list[str]:
        """The ean list must contain at least one element, at most 100
        An ean must be a 13 digit integer"""
        if not eans:
            raise ValueError("EAN list must not be empty")

        ean_list = eans.split(",")

        if len(ean_list) > 100:
            raise ValueError("Too many EANs")
        for ean in ean_list:
            if not ean.isdigit():
                raise ValueError("EAN must be an integer")
            if len(ean) != 13:
                raise ValueError("Only 13 characters EAN are accepted")
        return ean_list


class RejectedEANsPartialResponse(serialization.ConfiguredBaseModel):
    not_found: list[str] = fields.EANS_REJECTED_BECAUSE_NOT_FOUND
    subcategory_not_allowed: list[str] = fields.EANS_REJECTED_BECAUSE_CATEGORY_NOT_ALLOWED
    not_compliant_with_cgu: list[str] = fields.EANS_REJECTED_BECAUSE_NOT_COMPLIANT


class AvailableEANsResponse(serialization.ConfiguredBaseModel):
    available: list[str] = fields.EANS_AVAILABLE
    rejected: RejectedEANsPartialResponse = fields.EANS_REJECTED

    @classmethod
    def build_response(
        cls,
        *,
        available: list[str],
        not_compliant_with_cgu: list[str],
        not_found: list[str],
        subcategory_not_allowed: list[str],
    ) -> "AvailableEANsResponse":
        return cls(
            available=available,
            rejected=RejectedEANsPartialResponse(
                not_found=not_found,
                subcategory_not_allowed=subcategory_not_allowed,
                not_compliant_with_cgu=not_compliant_with_cgu,
            ),
        )


class LocationTypeEnum(str, enum.Enum):
    DIGITAL = "DIGITAL"
    PHYSICAL = "PHYSICAL"


class ProductCategoryResponse(serialization.ConfiguredBaseModel):
    id: ProductCategoryEnum  # type: ignore[valid-type]
    conditional_fields: dict[str, bool] = pydantic_v1.Field(
        description="The keys are fields that should be set in the category_related_fields of a product. The values indicate whether their associated field is mandatory during product creation."
    )
    locationType: LocationTypeEnum | None

    @classmethod
    def build_category(cls, subcategory: subcategories.Subcategory) -> "ProductCategoryResponse":
        conditional_fields = {}
        for field_name, condition in subcategory.conditional_fields.items():
            if field_name in ExtraDataModel.__fields__:
                conditional_fields[field_name] = condition.is_required_in_external_form

        locationType: LocationTypeEnum | None = None
        if subcategory.is_online_only:
            locationType = LocationTypeEnum.DIGITAL
        elif subcategory.is_offline_only:
            locationType = LocationTypeEnum.PHYSICAL

        return cls(
            id=subcategory.id,
            conditional_fields=conditional_fields,
            locationType=locationType,
        )


class GetProductCategoriesResponse(serialization.ConfiguredBaseModel):
    __root__: list[ProductCategoryResponse]


class ShowTypeResponse(serialization.ConfiguredBaseModel):
    id: ShowTypeEnum  # type: ignore[valid-type]
    label: str


class GetShowTypesResponse(serialization.ConfiguredBaseModel):
    __root__: list[ShowTypeResponse]


class MusicTypeResponse(serialization.ConfiguredBaseModel):
    id: MusicTypeEnum  # type: ignore[valid-type]
    label: str


class TiteliveMusicTypeResponse(serialization.ConfiguredBaseModel):
    id: TiteliveMusicTypeEnum  # type: ignore[valid-type]
    label: str


class TiteliveEventMusicTypeResponse(serialization.ConfiguredBaseModel):
    id: TiteliveEventMusicTypeEnum  # type: ignore[valid-type]
    label: str


class GetMusicTypesResponse(serialization.ConfiguredBaseModel):
    __root__: list[MusicTypeResponse]


class GetTiteliveMusicTypesResponse(serialization.ConfiguredBaseModel):
    __root__: list[TiteliveMusicTypeResponse]


class GetTiteliveEventMusicTypesResponse(serialization.ConfiguredBaseModel):
    __root__: list[TiteliveEventMusicTypeResponse]


class ImageUploadFile(BaseModel):
    # This field is required but cannot be handled by pydantic.
    # We validate it manually in the validator below.
    # This is used by spectree to generate a correct swagger documentation.
    file: BaseFile | None = pydantic_v1.Field(
        description="[required] Image format must be PNG, JPEG or JPG. Size must be between 400x600 and 800x1200 pixels. Aspect ratio must be 2:3 (portrait format).",
    )
    credit: str | None

    @validator("file", pre=True, always=True)
    def validate_file(cls, value: BaseFile | None) -> BaseFile | None:
        if request.files and "file" in request.files:
            return value
        raise ValueError("A file must be provided in the request")
