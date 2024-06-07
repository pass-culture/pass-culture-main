import copy
import datetime
import decimal
import enum
import logging
import typing

from dateutil import relativedelta
from flask import request
import pydantic.v1 as pydantic_v1
from pydantic.v1 import validator
from pydantic.v1.utils import GetterDict
from spectree import BaseFile

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import constants
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.models import offer_mixin
from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants import descriptions
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.public.individual_offers.v1.base_serialization import IndexPaginationQueryParams
import pcapi.routes.public.serialization.accessibility as accessibility_serialization
from pcapi.routes.public.serialization.utils import StrEnum
from pcapi.routes.serialization import BaseModel
from pcapi.serialization import utils as serialization_utils
from pcapi.utils import date as date_utils
from pcapi.utils.feature import FeatureToggle


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
    "MusicTypeEnum",
    {music_sub_type_slug: music_sub_type_slug for music_sub_type_slug in music_types.MUSIC_SUB_TYPES_BY_SLUG},
)

TiteliveMusicTypeEnum = StrEnum(  # type: ignore[call-overload]
    "TiteliveMusicTypeEnum", {music_type: music_type for music_type in constants.GTL_ID_BY_TITELIVE_MUSIC_GENRE}
)

ShowTypeEnum = StrEnum(  # type: ignore[call-overload]
    "ShowTypeEnum",
    {show_sub_type_slug: show_sub_type_slug for show_sub_type_slug in show_types.SHOW_SUB_TYPES_BY_SLUG},
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

    audio_disability_compliant: bool | None
    mental_disability_compliant: bool | None
    motor_disability_compliant: bool | None
    visual_disability_compliant: bool | None


class PhysicalLocation(serialization.ConfiguredBaseModel):
    type: typing.Literal["physical"] = "physical"
    venue_id: int = pydantic_v1.Field(..., example=1, description="List of venues is available at GET /offerer_venues")


class DigitalLocation(serialization.ConfiguredBaseModel):
    type: typing.Literal["digital"] = "digital"
    venue_id: int = pydantic_v1.Field(..., example=1, description="List of venues is available at GET /offerer_venues")
    url: pydantic_v1.HttpUrl = pydantic_v1.Field(
        ...,
        description="Link users will be redirected to after booking this offer. You may include '{token}', '{email}' and/or '{offerId}' in the URL, which will be replaced respectively by the booking token (use this token to confirm the offer - see API Contremarque), the email of the user who booked the offer and the created offer id",
        example="https://example.com?token={token}&email={email}&offerId={offerId}",
    )


EAN_FIELD = pydantic_v1.Field(example="1234567890123", description="European Article Number (EAN-13)")


class ExtraDataModel(serialization.ConfiguredBaseModel):
    author: str | None = pydantic_v1.Field(example="Jane Doe")
    ean: str | None = EAN_FIELD
    musicType: TiteliveMusicTypeEnum | MusicTypeEnum | None  # type: ignore[valid-type]
    performer: str | None = pydantic_v1.Field(example="Jane Doe")
    stageDirector: str | None = pydantic_v1.Field(example="Jane Doe")
    showType: ShowTypeEnum | None  # type: ignore[valid-type]
    speaker: str | None = pydantic_v1.Field(example="Jane Doe")
    visa: str | None = pydantic_v1.Field(example="140843")


class CategoryRelatedFields(ExtraDataModel):
    subcategory_id: str = pydantic_v1.Field(alias="category")


IS_DUO_BOOKINGS_FIELD = pydantic_v1.Field(
    False,
    description="If set to true, users may book the offer for two persons. Second item will be delivered at the same price as the first one. Category must be compatible with this feature.",
    alias="enableDoubleBookings",
)
BOOKING_EMAIL_FIELD = pydantic_v1.Field(
    None, description="Recipient email for notifications about bookings, cancellations, etc."
)
CATEGORY_RELATED_FIELD_DESCRIPTION = (
    "Cultural category the offer belongs to. According to the category, some fields may or must be specified."
)
CATEGORY_RELATED_FIELD = pydantic_v1.Field(..., description=CATEGORY_RELATED_FIELD_DESCRIPTION)
DESCRIPTION_FIELD_MODEL = pydantic_v1.Field(
    None, description="Offer description", example="A great book for kids and old kids.", max_length=1000
)
DESCRIPTION_FIELD_RESPONSE = pydantic_v1.Field(
    None, description="Offer description", example="A great book for kids and old kids."
)
EXTERNAL_TICKET_OFFICE_URL_FIELD = pydantic_v1.Field(
    None,
    description="Link displayed to users wishing to book the offer but who do not have (anymore) credit.",
    example="https://example.com",
)
IMAGE_CREDIT_FIELD = pydantic_v1.Field(None, description="Image owner or author.", example="Jane Doe")
WITHDRAWAL_DETAILS_FIELD = pydantic_v1.Field(
    None,
    description="Further information that will be provided to attendees to ease the offer collection.",
    example="Opening hours, specific office, collection period, access code, email annoucement...",
    alias="itemCollectionDetails",
)
BOOKING_CONTACT_FIELD = pydantic_v1.Field(
    None,
    description="Recipient email to contact if there is an issue with booking the offer. Mandatory if the offer has withdrawable tickets.",
)
LOCATION_FIELD = pydantic_v1.Field(
    ...,
    discriminator="type",
    description="Location where the offer will be available or will take place. The location type must be compatible with the category",
)
NAME_FIELD = pydantic_v1.Field(description="Offer title", example="Le Petit Prince", max_length=90)
DURATION_MINUTES_FIELD = pydantic_v1.Field(description="Event duration in minutes", example=60, alias="eventDuration")

HAS_TICKET_FIELD = pydantic_v1.Field(
    description="Indicates whether the offer has an associated ticket. True if a ticket is available, False otherwise. To create an offer with tickets you must have developed the pass culture ticketing interface.",
    example=False,
)
PRICE_CATEGORY_LABEL_FIELD = pydantic_v1.Field(description="Price category label", example="Carré or")
PRICE_CATEGORIES_FIELD = pydantic_v1.Field(description="Available price categories for dates of this offer")
EVENT_DATES_FIELD = pydantic_v1.Field(
    description="Dates of the event. If there are different prices for the same date, several date objects are needed",
)


class ImageBody(serialization.ConfiguredBaseModel):
    """Image illustrating the offer. Offers with images are more likely to be booked."""

    credit: str | None = IMAGE_CREDIT_FIELD
    file: str = pydantic_v1.Field(
        ...,
        description="Image file encoded in base64 string. Image format must be PNG or JPEG. Size must be between 400x600 and 800x1200 pixels. Aspect ratio must be 2:3 (portrait format).",
        example="iVBORw0KGgoAAAANSUhEUgAAAhUAAAMgCAAAAACxT88IAAABImlDQ1BJQ0MgcHJvZmlsZQAAKJGdkLFKw1AUhr+0oiKKg6IgDhlcO5pFB6tCKCjEWMHqlCYpFpMYkpTiG/gm+jAdBMFXcFdw9r/RwcEs3nD4Pw7n/P+9gZadhGk5dwBpVhWu3x1cDq7shTfa+lbZZC8Iy7zreSc0ns9XLKMvHePVPPfnmY/iMpTOVFmYFxVY+2JnWuWGVazf9v0j8YPYjtIsEj+Jd6I0Mmx2/TSZhD+e5jbLcXZxbvqqbVx6nOJhM2TCmISKjjRT5xiHXalLQcA9JaE0IVZvqpmKG1EpJ5dDUV+k2zTkbdV5nlKG8hjLyyTckcrT5GH+7/fax1m9aW3M8qAI6lZb1RqN4P0RVgaw9gxL1w1Zi7/f1jDj1DP/fOMXG7hQfuNVil0AAAAJcEhZcwAALiMAAC4jAXilP3YAAAAHdElNRQfnAwMPGDrdy1JyAAABtElEQVR42u3BAQ0AAADCoPdPbQ8HFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8GaFGgABH6N7kwAAAABJRU5ErkJggg==",
    )


class ImageResponse(serialization.ConfiguredBaseModel):
    """Image illustrating the offer. Offers with images are more likely to be booked."""

    credit: str | None = IMAGE_CREDIT_FIELD
    url: str = pydantic_v1.Field(
        ..., description="Url where the image is accessible", example="https://example.com/image.png"
    )


class OfferCreationBase(serialization.ConfiguredBaseModel):
    accessibility: Accessibility
    booking_contact: pydantic_v1.EmailStr | None = BOOKING_CONTACT_FIELD
    booking_email: pydantic_v1.EmailStr | None = BOOKING_EMAIL_FIELD
    category_related_fields: CategoryRelatedFields = CATEGORY_RELATED_FIELD
    description: str | None = DESCRIPTION_FIELD_MODEL
    external_ticket_office_url: pydantic_v1.HttpUrl | None = EXTERNAL_TICKET_OFFICE_URL_FIELD
    image: ImageBody | None
    is_duo: bool | None = IS_DUO_BOOKINGS_FIELD
    name: str = fields.OFFER_NAME_WITH_MAX_LENGTH
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD


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

    # Convert musicSubType (resp showSubType) code to musicType slug (resp showType slug)
    music_sub_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.MUSIC_SUB_TYPE.value, None)

    # FIXME (mageoffray, 2023-12-14): some historical offers have no musicSubType and only musicType.
    # We should migrate our musicType|musicSubType to titelive music types. This migration will include
    # offers without musicSubType
    music_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value, None)
    if music_type and not music_sub_type:
        music_sub_type = "-1"  # Use 'Other' when not filled

    gtl_id = serialized_data.pop(subcategories.ExtraDataFieldEnum.GTL_ID.value, None)

    # FIXME (mageoffray, 2023-12-14): some historical offers have no showSubType and only showType.
    show_sub_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.SHOW_SUB_TYPE.value, None)
    show_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.SHOW_TYPE.value, None)
    if show_type and not show_sub_type:
        show_sub_type = "-1"  # Use 'Other' when not filled

    if music_sub_type:
        serialized_data["musicType"] = MusicTypeEnum(music_types.MUSIC_SUB_TYPES_BY_CODE[int(music_sub_type)].slug)
    if show_sub_type:
        serialized_data["showType"] = ShowTypeEnum(show_types.SHOW_SUB_TYPES_BY_CODE[int(show_sub_type)].slug)

    if (
        gtl_id
        and offer.subcategoryId in subcategories.MUSIC_SUBCATEGORIES
        and FeatureToggle.ENABLE_TITELIVE_MUSIC_TYPES_IN_API_OUTPUT.is_active()
    ):
        serialized_data["musicType"] = TiteliveMusicTypeEnum(
            constants.TITELIVE_MUSIC_GENRES_BY_GTL_ID[gtl_id[:2] + "0" * 6]
        )  # Only take the first level of the GTL ID

    return category_fields_model(**serialized_data, subcategory_id=offer.subcategory.id)  # type: ignore[misc, call-arg]


def deserialize_extra_data(
    category_related_fields: CategoryRelatedFields, initial_extra_data: offers_models.OfferExtraData | None = None
) -> dict[str, str]:
    extra_data: dict = initial_extra_data or {}  # type: ignore[assignment]
    for field_name, field_value in category_related_fields.dict(exclude_unset=True).items():
        if field_name == "subcategory_id":
            continue
        if field_name == subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value:
            # Convert musicType slug to musicType and musicSubType codes
            if field_value in TiteliveMusicTypeEnum.__members__:
                extra_data["gtl_id"] = constants.GTL_ID_BY_TITELIVE_MUSIC_GENRE[field_value]
                music_slug = constants.MUSIC_SLUG_BY_GTL_ID[extra_data["gtl_id"]]
                extra_data["musicType"] = str(music_types.MUSIC_TYPES_BY_SLUG[music_slug].code)
                extra_data["musicSubType"] = str(music_types.MUSIC_SUB_TYPES_BY_SLUG[music_slug].code)
            else:
                extra_data["musicSubType"] = str(music_types.MUSIC_SUB_TYPES_BY_SLUG[field_value].code)
                extra_data["musicType"] = str(music_types.MUSIC_TYPES_BY_SLUG[field_value].code)
                extra_data["gtl_id"] = constants.MUSIC_SLUG_TO_GTL_ID[field_value]
        elif field_name == subcategories.ExtraDataFieldEnum.SHOW_TYPE.value:
            # Convert showType slug to showType and showSubType codes
            extra_data["showSubType"] = str(show_types.SHOW_SUB_TYPES_BY_SLUG[field_value].code)
            extra_data["showType"] = str(show_types.SHOW_TYPES_BY_SLUG[field_value].code)
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

next_month = datetime.datetime.utcnow().replace(hour=12, minute=0, second=0) + relativedelta.relativedelta(months=1)
paris_tz_next_month = date_utils.utc_datetime_to_department_timezone(next_month, "75")

BEGINNING_DATETIME_FIELD = pydantic_v1.Field(
    description=descriptions.BEGINNING_DATETIME_FIELD_DESCRIPTION,
    example=paris_tz_next_month.isoformat(timespec="seconds"),
)
BOOKING_LIMIT_DATETIME_FIELD = pydantic_v1.Field(
    description=descriptions.BOOKING_LIMIT_DATETIME_FIELD_DESCRIPTION,
    example=paris_tz_next_month.isoformat(timespec="seconds"),
)
PRICE_FIELD = pydantic_v1.Field(description="Offer price in euro cents.", example=1000)
QUANTITY_FIELD = pydantic_v1.Field(
    description="Quantity of items currently available to pass Culture. Value 'unlimited' is used for infinite quantity of items.",
    example=10,
)

UNLIMITED_LITERAL = typing.Literal["unlimited"]


class BaseStockCreation(serialization.ConfiguredBaseModel):
    quantity: pydantic_v1.StrictInt | UNLIMITED_LITERAL = QUANTITY_FIELD

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


class StockCreation(BaseStockCreation):
    price: offer_price_model = PRICE_FIELD
    booking_limit_datetime: datetime.datetime | None = BOOKING_LIMIT_DATETIME_FIELD

    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")

    @pydantic_v1.validator("price")
    def price_must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Value must be positive")
        return value


class BaseStockEdition(serialization.ConfiguredBaseModel):
    booking_limit_datetime: datetime.datetime | None = BOOKING_LIMIT_DATETIME_FIELD
    quantity: pydantic_v1.StrictInt | UNLIMITED_LITERAL | None = QUANTITY_FIELD

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


class StockEdition(BaseStockEdition):
    price: offer_price_model | None = PRICE_FIELD


class ProductOfferCreation(OfferCreationBase):
    category_related_fields: product_category_creation_fields
    stock: StockCreation | None
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD

    class Config:
        extra = "forbid"


class ProductOfferByEanCreation(serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        ean: str = EAN_FIELD
    else:
        ean: pydantic_v1.constr(min_length=13, max_length=13) = EAN_FIELD
    stock: StockCreation

    class Config:
        extra = "forbid"


class ProductsOfferByEanCreation(serialization.ConfiguredBaseModel):
    products: list[ProductOfferByEanCreation] = pydantic_v1.Field(
        description="List of product to create or update", max_items=500
    )
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD

    class Config:
        extra = "forbid"


class DecimalPriceGetterDict(GetterDict):
    def get(self, key: str, default: typing.Any | None = None) -> typing.Any:
        if key == "price" and isinstance(self._obj.price, decimal.Decimal):
            return finance_utils.to_eurocents(self._obj.price)
        return super().get(key, default)


class PriceCategoryCreation(serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        label: str = PRICE_CATEGORY_LABEL_FIELD
    else:
        label: pydantic_v1.constr(min_length=1, max_length=50) = PRICE_CATEGORY_LABEL_FIELD
    price: offer_price_model = PRICE_FIELD

    class Config:
        getter_dict = DecimalPriceGetterDict


class PriceCategoriesCreation(serialization.ConfiguredBaseModel):
    price_categories: list[PriceCategoryCreation] = PRICE_CATEGORIES_FIELD

    @pydantic_v1.validator("price_categories")
    def get_unique_price_categories(
        cls,
        price_categories: list[PriceCategoryCreation],
    ) -> list[PriceCategoryCreation]:
        unique_price_categories = []
        for price_category in price_categories:
            if (price_category.label, price_category.price) in unique_price_categories:
                raise ValueError("Price categories must be unique")
            unique_price_categories.append((price_category.label, price_category.price))
        return price_categories

    class Config:
        extra = "forbid"


class EventOfferCreation(OfferCreationBase):
    category_related_fields: event_category_creation_fields
    duration_minutes: int | None = DURATION_MINUTES_FIELD
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD
    has_ticket: bool = HAS_TICKET_FIELD
    price_categories: list[PriceCategoryCreation] | None = PRICE_CATEGORIES_FIELD

    @pydantic_v1.validator("price_categories")
    def get_unique_price_categories(
        cls,
        price_categories: list[PriceCategoryCreation],
    ) -> list[PriceCategoryCreation]:
        unique_price_categories = []
        for price_category in price_categories:
            if (price_category.label, price_category.price) in unique_price_categories:
                raise ValueError("Price categories must be unique")
            unique_price_categories.append((price_category.label, price_category.price))
        return price_categories

    class Config:
        extra = "forbid"


class OfferEditionBase(serialization.ConfiguredBaseModel):
    accessibility: accessibility_serialization.PartialAccessibility | None = pydantic_v1.Field(
        description="Accessibility to disabled people. Leave fields undefined to keep current value"
    )
    booking_contact: pydantic_v1.EmailStr | None = BOOKING_CONTACT_FIELD
    booking_email: pydantic_v1.EmailStr | None = BOOKING_EMAIL_FIELD
    is_active: bool | None = pydantic_v1.Field(
        description="Whether the offer is activated. An inactive offer cannot be booked."
    )
    is_duo: bool | None = IS_DUO_BOOKINGS_FIELD
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD
    image: ImageBody | None
    description: str | None = DESCRIPTION_FIELD_MODEL

    class Config:
        extra = "forbid"


STOCK_EDITION_FIELD = pydantic_v1.Field(
    description="If stock is set to null, all cancellable bookings (i.e not used) will be cancelled. To prevent from further bookings, you may alternatively set stock.quantity to the bookedQuantity (but not below).",
)


class ProductOfferEdition(OfferEditionBase):
    offer_id: int
    category_related_fields: product_category_edition_fields | None = pydantic_v1.Field(
        None,
        description="To override category related fields, the category must be specified, even if it cannot be changed. Other category related fields may be left undefined to keep their current value.",
    )
    stock: StockEdition | None = STOCK_EDITION_FIELD

    class Config:
        extra = "forbid"


class PriceCategoryEdition(serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        label: str = PRICE_CATEGORY_LABEL_FIELD
    else:
        label: pydantic_v1.constr(min_length=1, max_length=50) | None = PRICE_CATEGORY_LABEL_FIELD
    price: offer_price_model | None = PRICE_FIELD

    @pydantic_v1.validator("price")
    def price_must_be_positive(cls, value: int | None) -> int | None:
        if value and value < 0:
            raise ValueError("Value must be positive")
        return value

    class Config:
        extra = "forbid"


class DateEdition(BaseStockEdition):
    beginning_datetime: datetime.datetime | None = BEGINNING_DATETIME_FIELD
    price_category_id: int | None


class EventOfferEdition(OfferEditionBase):
    category_related_fields: event_category_edition_fields | None = pydantic_v1.Field(
        None,
        description="To override category related fields, the category must be specified, even if it cannot be changed. Other category related fields may be left undefined to keep their current value.",
    )
    duration_minutes: int | None = DURATION_MINUTES_FIELD


class DateCreation(BaseStockCreation):
    beginning_datetime: datetime.datetime = BEGINNING_DATETIME_FIELD
    booking_limit_datetime: datetime.datetime = BOOKING_LIMIT_DATETIME_FIELD
    price_category_id: int

    _validate_beginning_datetime = serialization_utils.validate_datetime("beginning_datetime")
    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")


class DatesCreation(serialization.ConfiguredBaseModel):
    dates: list[DateCreation] = pydantic_v1.Field(
        description="Dates to add to the event. If there are different prices and quantity for the same date, you must add several date objects",
    )

    class Config:
        extra = "forbid"


class PriceCategoryResponse(serialization.ConfiguredBaseModel):
    id: int
    label: str = PRICE_CATEGORY_LABEL_FIELD
    price: pydantic_v1.StrictInt = PRICE_FIELD

    class Config:
        getter_dict = DecimalPriceGetterDict


class PriceCategoriesResponse(serialization.ConfiguredBaseModel):
    price_categories: list[PriceCategoryResponse] = PRICE_CATEGORIES_FIELD

    @classmethod
    def build_price_categories(cls, price_categories: list[offers_models.PriceCategory]) -> "PriceCategoriesResponse":
        return cls(price_categories=[PriceCategoryResponse.from_orm(category) for category in price_categories])


class BaseStockResponse(serialization.ConfiguredBaseModel):
    booking_limit_datetime: datetime.datetime | None = BOOKING_LIMIT_DATETIME_FIELD
    dnBookedQuantity: int = pydantic_v1.Field(..., description="Number of bookings.", example=0, alias="bookedQuantity")
    quantity: pydantic_v1.StrictInt | UNLIMITED_LITERAL = QUANTITY_FIELD

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}

    @classmethod
    def build_stock(cls, stock: offers_models.Stock) -> "BaseStockResponse":
        return cls(  # type: ignore[call-arg]
            booking_limit_datetime=stock.bookingLimitDatetime,
            dnBookedQuantity=stock.dnBookedQuantity,
            quantity=stock.quantity if stock.quantity is not None else "unlimited",
        )


class DateResponse(BaseStockResponse):
    id: int
    beginning_datetime: datetime.datetime = BEGINNING_DATETIME_FIELD
    booking_limit_datetime: datetime.datetime = BOOKING_LIMIT_DATETIME_FIELD
    price_category: PriceCategoryResponse

    @classmethod
    def build_date(cls, stock: offers_models.Stock) -> "DateResponse":
        stock_response = BaseStockResponse.build_stock(stock)
        return cls(
            id=stock.id,
            beginning_datetime=stock.beginningDatetime,  # type: ignore[arg-type]
            price_category=PriceCategoryResponse.from_orm(stock.priceCategory),
            **stock_response.dict(),
        )


class PostDatesResponse(serialization.ConfiguredBaseModel):
    dates: list[DateResponse] = pydantic_v1.Field(description="Dates of the event.")


class OfferResponse(serialization.ConfiguredBaseModel):
    id: int
    accessibility: AccessibilityResponse
    booking_contact: str | None = BOOKING_CONTACT_FIELD
    booking_email: str | None = BOOKING_EMAIL_FIELD
    description: str | None = DESCRIPTION_FIELD_RESPONSE
    external_ticket_office_url: str | None = EXTERNAL_TICKET_OFFICE_URL_FIELD
    image: ImageResponse | None
    is_duo: bool | None = IS_DUO_BOOKINGS_FIELD
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD
    name: str = fields.OFFER_NAME
    status: offer_mixin.OfferStatus = pydantic_v1.Field(
        ...,
        description=descriptions.OFFER_STATUS_FIELD_DESCRIPTION,
        example=offer_mixin.OfferStatus.ACTIVE.name,
    )
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}

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
            is_duo=offer.isDuo,
            location=DigitalLocation.from_orm(offer) if offer.isDigital else PhysicalLocation.from_orm(offer),
            name=offer.name,
            status=offer.status,
            withdrawal_details=offer.withdrawalDetails,
        )


class ProductStockResponse(BaseStockResponse):
    price: pydantic_v1.StrictInt = PRICE_FIELD

    @classmethod
    def build_product_stock(cls, stock: offers_models.Stock) -> "ProductStockResponse":
        stock_response = BaseStockResponse.build_stock(stock)
        return cls(price=finance_utils.to_eurocents(stock.price), **stock_response.dict())


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


def _serialize_has_ticket(offer: offers_models.Offer) -> bool:
    # hasTicket is True only if the bookings are linked to an externalBooking
    # This is the case for offers with withdrawalType IN_APP.
    return offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP


class EventOfferResponse(OfferResponse, PriceCategoriesResponse):
    category_related_fields: event_category_reading_fields
    duration_minutes: int | None = DURATION_MINUTES_FIELD
    has_ticket: bool = HAS_TICKET_FIELD

    @classmethod
    def build_event_offer(cls, offer: offers_models.Offer) -> "EventOfferResponse":
        base_offer_response = OfferResponse.build_offer(offer)
        return cls(
            category_related_fields=serialize_extra_data(offer),
            duration_minutes=offer.durationMinutes,
            has_ticket=_serialize_has_ticket(offer),
            price_categories=[
                PriceCategoryResponse.from_orm(price_category) for price_category in offer.priceCategories
            ],
            **base_offer_response.dict(),
        )


class GetOffersQueryParams(IndexPaginationQueryParams):
    venue_id: int = pydantic_v1.Field(..., description="Venue id to filter offers on.")


class GetDatesQueryParams(IndexPaginationQueryParams):
    pass


class ProductOffersResponse(serialization.ConfiguredBaseModel):
    products: list[ProductOfferResponse]


class ProductOffersByEanResponse(serialization.ConfiguredBaseModel):
    products: list[ProductOfferResponse]


class EventOffersResponse(serialization.ConfiguredBaseModel):
    events: list[EventOfferResponse]


class GetDatesResponse(serialization.ConfiguredBaseModel):
    dates: list[DateResponse]

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}


class GetProductsListByEansQuery(serialization.ConfiguredBaseModel):
    eans: str = pydantic_v1.Field(example="0123456789123,0123456789124")
    venueId: int = pydantic_v1.Field(example=1)

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


class EventCategoryResponse(serialization.ConfiguredBaseModel):
    id: EventCategoryEnum  # type: ignore[valid-type]
    conditional_fields: dict[str, bool] = pydantic_v1.Field(
        description="The keys are fields that should be set in the category_related_fields of an event. The values indicate whether their associated field is mandatory during event creation."
    )

    @classmethod
    def build_category(cls, subcategory: subcategories.Subcategory) -> "EventCategoryResponse":
        return cls(
            id=subcategory.id,
            conditional_fields={
                field: condition.is_required_in_external_form
                for field, condition in subcategory.conditional_fields.items()
            },
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

        if subcategory.is_online_only:
            locationType = LocationTypeEnum.DIGITAL
        elif subcategory.is_offline_only:
            locationType = LocationTypeEnum.PHYSICAL

        return cls(
            id=subcategory.id,
            conditional_fields=conditional_fields,
            locationType=locationType,
        )


class GetEventCategoriesResponse(serialization.ConfiguredBaseModel):
    __root__: list[EventCategoryResponse]


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


class GetMusicTypesResponse(serialization.ConfiguredBaseModel):
    __root__: list[MusicTypeResponse | TiteliveMusicTypeResponse]


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
