import copy
import datetime
import decimal
import enum
import logging
import typing

from dateutil import relativedelta
import pydantic
from pydantic.utils import GetterDict
import typing_extensions

from pcapi import settings
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.models import offer_mixin
from pcapi.routes import serialization
from pcapi.serialization import utils as serialization_utils
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


class StrEnum(str, enum.Enum):
    # StrEnum is needed so that swagger ui displays the enum values
    # see https://github.com/swagger-api/swagger-ui/issues/6906
    pass


MusicTypeEnum = StrEnum(  # type: ignore [call-overload]
    "MusicTypeEnum",
    {
        music_sub_type.slug: music_sub_type.slug
        for music_type in music_types.music_types
        for music_sub_type in music_type.children
    },
)


ShowTypeEnum = StrEnum(  # type: ignore [call-overload]
    "ShowTypeEnum",
    {
        show_sub_type.slug: show_sub_type.slug
        for show_type in show_types.show_types
        for show_sub_type in show_type.children
    },
)

VenueTypeEnum = StrEnum(  # type: ignore [call-overload]
    "VenueTypeEnum", {venue_type.name: venue_type.name for venue_type in offerers_models.VenueTypeCode}
)


class Accessibility(serialization.ConfiguredBaseModel):
    """Accessibility for people with disabilities."""

    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool


class PartialAccessibility(serialization.ConfiguredBaseModel):
    """Accessibility for people with disabilities. Fields are null for digital venues."""

    audio_disability_compliant: bool | None
    mental_disability_compliant: bool | None
    motor_disability_compliant: bool | None
    visual_disability_compliant: bool | None


class PhysicalLocation(serialization.ConfiguredBaseModel):
    type: typing.Literal["physical"] = "physical"
    venue_id: int = pydantic.Field(..., example=1, description="List of venues is available at GET /offerer_venues")


class DigitalLocation(serialization.ConfiguredBaseModel):
    type: typing.Literal["digital"] = "digital"
    venue_id: int = pydantic.Field(..., example=1, description="List of venues is available at GET /offerer_venues")
    url: pydantic.HttpUrl = pydantic.Field(
        ...,
        description="Link users will be redirected to after booking this offer. You may include '{token}', '{email}' and/or '{offerId}' in the URL, which will be replaced respectively by the booking token (use this token to confirm the offer - see API Contremarque), the email of the user who booked the offer and the created offer id",
        example="https://example.com?token={token}&email={email}&offerId={offerId}",
    )


EAN_FIELD = pydantic.Field(example="1234567890123", description="European Article Number (EAN-13)")


class ExtraDataModel(serialization.ConfiguredBaseModel):
    author: str | None = pydantic.Field(example="Jane Doe")
    ean: str | None = EAN_FIELD
    isbn: str | None = pydantic.Field(None, example="9783140464079")
    musicType: MusicTypeEnum | None  # type: ignore [valid-type]
    performer: str | None = pydantic.Field(example="Jane Doe")
    stageDirector: str | None = pydantic.Field(example="Jane Doe")
    showType: ShowTypeEnum | None  # type: ignore [valid-type]
    speaker: str | None = pydantic.Field(example="Jane Doe")
    visa: str | None = pydantic.Field(example="140843")


class CategoryRelatedFields(ExtraDataModel):
    subcategory_id: str = pydantic.Field(alias="category")


IS_DUO_BOOKINGS_FIELD = pydantic.Field(
    False,
    description="If set to true, users may book the offer for two persons. Second item will be delivered at the same price as the first one. Category must be compatible with this feature.",
    alias="enableDoubleBookings",
)
BOOKING_EMAIL_FIELD = pydantic.Field(
    None, description="Recipient email for notifications about bookings, cancellations, etc."
)
CATEGORY_RELATED_FIELD_DESCRIPTION = (
    "Cultural category the offer belongs to. According to the category, some fields may or must be specified."
)
CATEGORY_RELATED_FIELD = pydantic.Field(..., description=CATEGORY_RELATED_FIELD_DESCRIPTION)
DESCRIPTION_FIELD = pydantic.Field(
    None, description="Offer description", example="A great book for kids and old kids.", max_length=1000
)
EXTERNAL_TICKET_OFFICE_URL_FIELD = pydantic.Field(
    None,
    description="Link displayed to users wishing to book the offer but who do not have (anymore) credit.",
    example="https://example.com",
)
ID_AT_PROVIDER_FIELD = pydantic.Field(
    description="The ID of the offer in your database. May be used to assert proper synchronization."
)
IMAGE_CREDIT_FIELD = pydantic.Field(None, description="Image owner or author.", example="Jane Doe")
WITHDRAWAL_DETAILS_FIELD = pydantic.Field(
    None,
    description="Further information that will be provided to attendees to ease the offer collection.",
    example="Opening hours, specific office, collection period, access code, email annoucement...",
    alias="itemCollectionDetails",
)
LOCATION_FIELD = pydantic.Field(
    ...,
    discriminator="type",
    description="Location where the offer will be available or will take place. The location type must be compatible with the category",
)
NAME_FIELD = pydantic.Field(description="Offer title", example="Le Petit Prince", max_length=90)
DURATION_MINUTES_FIELD = pydantic.Field(description="Event duration in minutes", example=60, alias="eventDuration")
TICKET_COLLECTION_FIELD = pydantic.Field(
    None,
    description="How the ticket will be collected. Leave empty if there is no ticket. Only some categories are compatible with tickets.",
    discriminator="way",
    example=None,
)
PRICE_CATEGORY_LABEL_FIELD = pydantic.Field(description="Price category label", example="Carré or")
PRICE_CATEGORIES_FIELD = pydantic.Field(description="Available price categories for dates of this offer")
EVENT_DATES_FIELD = pydantic.Field(
    description="Dates of the event. If there are different prices for the same date, several date objects are needed",
)
ON_SITE_MINUTES_BEFORE_EVENT_FIELD = pydantic.Field(
    ...,
    description="Number of minutes before the event when the ticket may be collected. Only some values are accepted (between 0 minutes and 48 hours).",
    example=0,
)
BY_EMAIL_DAYS_BEFORE_EVENT_FIELD = pydantic.Field(
    ...,
    description="Number of days before the event when the ticket will be sent. Only some values are accepted (1 to 7).",
    example=1,
)


class ImageBody(serialization.ConfiguredBaseModel):
    """Image illustrating the offer. Offers with images are more likely to be booked."""

    credit: str | None = IMAGE_CREDIT_FIELD
    file: str = pydantic.Field(
        ...,
        description="Image file encoded in base64 string. Image format must be PNG or JPEG. Size must be between 400x600 and 800x1200 pixels. Aspect ratio must be 2:3 (portrait format).",
        example="iVBORw0KGgoAAAANSUhEUgAAAhUAAAMgCAAAAACxT88IAAABImlDQ1BJQ0MgcHJvZmlsZQAAKJGdkLFKw1AUhr+0oiKKg6IgDhlcO5pFB6tCKCjEWMHqlCYpFpMYkpTiG/gm+jAdBMFXcFdw9r/RwcEs3nD4Pw7n/P+9gZadhGk5dwBpVhWu3x1cDq7shTfa+lbZZC8Iy7zreSc0ns9XLKMvHePVPPfnmY/iMpTOVFmYFxVY+2JnWuWGVazf9v0j8YPYjtIsEj+Jd6I0Mmx2/TSZhD+e5jbLcXZxbvqqbVx6nOJhM2TCmISKjjRT5xiHXalLQcA9JaE0IVZvqpmKG1EpJ5dDUV+k2zTkbdV5nlKG8hjLyyTckcrT5GH+7/fax1m9aW3M8qAI6lZb1RqN4P0RVgaw9gxL1w1Zi7/f1jDj1DP/fOMXG7hQfuNVil0AAAAJcEhZcwAALiMAAC4jAXilP3YAAAAHdElNRQfnAwMPGDrdy1JyAAABtElEQVR42u3BAQ0AAADCoPdPbQ8HFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8GaFGgABH6N7kwAAAABJRU5ErkJggg==",
    )


class ImageResponse(serialization.ConfiguredBaseModel):
    """Image illustrating the offer. Offers with images are more likely to be booked."""

    credit: str | None = IMAGE_CREDIT_FIELD
    url: str = pydantic.Field(
        ..., description="Url where the image is accessible", example="https://example.com/image.png"
    )


class OfferCreationBase(serialization.ConfiguredBaseModel):
    accessibility: Accessibility
    booking_email: pydantic.EmailStr | None = BOOKING_EMAIL_FIELD
    category_related_fields: CategoryRelatedFields = CATEGORY_RELATED_FIELD
    description: str | None = DESCRIPTION_FIELD
    external_ticket_office_url: pydantic.HttpUrl | None = EXTERNAL_TICKET_OFFICE_URL_FIELD
    image: ImageBody | None
    is_duo: bool | None = IS_DUO_BOOKINGS_FIELD
    name: str = NAME_FIELD
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD


class Method(enum.Enum):
    create = "create"
    read = "read"
    edit = "edit"


def compute_category_fields_model(
    subcategory: subcategories.Subcategory, method: Method
) -> typing.Type[CategoryRelatedFields]:
    """
    Create dynamic pydantic models to indicate which fields are available for the chosen subcategory,
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
        typing.Literal[subcategory.id],  # pyright: ignore (pylance error message)
        pydantic.Field(alias="category"),
    )

    model = pydantic.create_model(f"{subcategory.id}_{method.value}", **specific_fields)
    model.__doc__ = subcategory.pro_label
    model.__config__.allow_population_by_field_name = True
    return model


def serialize_extra_data(offer: offers_models.Offer) -> CategoryRelatedFields:
    category_fields_model = (product_category_reading_models | event_category_reading_models)[offer.subcategoryId]
    serialized_data = copy.deepcopy(offer.extraData or {})

    # Convert musicSubType (resp showSubType) code to musicType slug (resp showType slug)
    music_sub_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.MUSIC_SUB_TYPE.value, None)
    show_sub_type = serialized_data.pop(subcategories.ExtraDataFieldEnum.SHOW_SUB_TYPE.value, None)
    if music_sub_type:
        serialized_data["musicType"] = MusicTypeEnum(music_types.MUSIC_SUB_TYPES_BY_CODE[int(music_sub_type)].slug)
    if show_sub_type:
        serialized_data["showType"] = ShowTypeEnum(show_types.SHOW_SUB_TYPES_BY_CODE[int(show_sub_type)].slug)

    return category_fields_model(**serialized_data, subcategory_id=offer.subcategory.id)  # type: ignore [misc]


def deserialize_extra_data(
    category_related_fields: CategoryRelatedFields, initial_extra_data: offers_models.OfferExtraData | None = None
) -> dict[str, str]:
    extra_data: dict = initial_extra_data or {}  # type: ignore[assignment]
    for field_name, field_value in category_related_fields.dict(exclude_unset=True).items():
        if field_name == "subcategory_id":
            continue
        if field_name == subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value:
            # Convert musicType slug to musicType and musicSubType codes
            extra_data["musicSubType"] = str(music_types.MUSIC_SUB_TYPES_BY_SLUG[field_value].code)
            extra_data["musicType"] = str(music_types.MUSIC_TYPES_BY_SLUG[field_value].code)
        elif field_name == subcategories.ExtraDataFieldEnum.SHOW_TYPE.value:
            # Convert showType slug to showType and showSubType codes
            extra_data["showSubType"] = str(show_types.SHOW_SUB_TYPES_BY_SLUG[field_value].code)
            extra_data["showType"] = str(show_types.SHOW_TYPES_BY_SLUG[field_value].code)
        else:
            extra_data[field_name] = field_value

    return extra_data


ALLOWED_PRODUCT_SUBCATEGORIES = [subcategories.SUPPORT_PHYSIQUE_MUSIQUE]
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
    product_category_creation_fields = typing_extensions.Annotated[
        product_category_creation_models[subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id],
        pydantic.Field(description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]
    product_category_reading_fields = typing_extensions.Annotated[
        typing.Union[tuple(product_category_reading_models.values())],
        pydantic.Field(discriminator="subcategory_id", description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]
    product_category_edition_fields = typing_extensions.Annotated[
        typing.Union[tuple(product_category_edition_models.values())],
        pydantic.Field(discriminator="subcategory_id"),
    ]
    event_category_creation_fields = typing_extensions.Annotated[
        typing.Union[tuple(event_category_creation_models.values())],
        pydantic.Field(discriminator="subcategory_id", description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]
    event_category_edition_fields = typing_extensions.Annotated[
        typing.Union[tuple(event_category_edition_models.values())],
        pydantic.Field(discriminator="subcategory_id"),
    ]
    event_category_reading_fields = typing_extensions.Annotated[
        typing.Union[tuple(event_category_reading_models.values())],
        pydantic.Field(discriminator="subcategory_id", description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]

next_month = datetime.datetime.utcnow().replace(hour=12, minute=0, second=0) + relativedelta.relativedelta(months=1)
paris_tz_next_month = date_utils.utc_datetime_to_department_timezone(next_month, "75")

BEGINNING_DATETIME_FIELD = pydantic.Field(
    description="Timezone aware datetime of the event.",
    example=paris_tz_next_month.isoformat(timespec="seconds"),
)
BOOKING_LIMIT_DATETIME_FIELD = pydantic.Field(
    description="Timezone aware datetime after which the offer can no longer be booked.",
    example=paris_tz_next_month.isoformat(timespec="seconds"),
)
PRICE_FIELD = pydantic.Field(description="Offer price in euro cents.", example=1000)
QUANTITY_FIELD = pydantic.Field(
    description="Quantity of items allocated to pass Culture. Value 'unlimited' is used for infinite quantity of items.",
    example=10,
)

UNLIMITED_LITERAL = typing.Literal["unlimited"]


class BaseStockCreation(serialization.ConfiguredBaseModel):
    quantity: pydantic.StrictInt | UNLIMITED_LITERAL = QUANTITY_FIELD

    @pydantic.validator("quantity")
    def quantity_must_be_positive(cls, quantity: int | str) -> int | str:
        if isinstance(quantity, int) and quantity < 0:
            raise ValueError("Value must be positive")
        return quantity


def deserialize_quantity(quantity: int | UNLIMITED_LITERAL | None) -> int | None:
    if quantity == "unlimited":
        return None
    return quantity


class StockCreation(BaseStockCreation):
    price: pydantic.StrictInt = PRICE_FIELD
    booking_limit_datetime: datetime.datetime | None = BOOKING_LIMIT_DATETIME_FIELD

    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")

    @pydantic.validator("price")
    def price_must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Value must be positive")
        return value


class BaseStockEdition(serialization.ConfiguredBaseModel):
    booking_limit_datetime: datetime.datetime | None = BOOKING_LIMIT_DATETIME_FIELD
    quantity: pydantic.StrictInt | UNLIMITED_LITERAL | None = QUANTITY_FIELD

    @pydantic.validator("quantity")
    def quantity_must_be_positive(cls, quantity: int | str | None) -> int | str | None:
        if isinstance(quantity, int) and quantity < 0:
            raise ValueError("Value must be positive")
        return quantity

    class Config:
        extra = "forbid"


class StockEdition(BaseStockEdition):
    price: pydantic.StrictInt | None = PRICE_FIELD

    @pydantic.validator("price")
    def price_must_be_positive(cls, value: int | None) -> int | None:
        if value and value < 0:
            raise ValueError("Value must be positive")
        return value


ON_SITE_MINUTES_BEFORE_EVENT = typing.Literal[0, 15, 30, 60, 120, 240, 1440, 2880]
BY_EMAIL_DAYS_BEFORE_EVENT = typing.Literal[1, 2, 3, 4, 5, 6, 7]


class OnSiteCollectionDetails(serialization.ConfiguredBaseModel):
    minutesBeforeEvent: ON_SITE_MINUTES_BEFORE_EVENT = ON_SITE_MINUTES_BEFORE_EVENT_FIELD
    way: typing.Literal["on_site"] = "on_site"


class OnSiteCollectionDetailsResponse(serialization.ConfiguredBaseModel):
    # different model in case the database minutesBeforeEvent value is not in the enum
    minutesBeforeEvent: int = ON_SITE_MINUTES_BEFORE_EVENT_FIELD
    way: typing.Literal["on_site"] = "on_site"


class SentByEmailDetails(serialization.ConfiguredBaseModel):
    daysBeforeEvent: BY_EMAIL_DAYS_BEFORE_EVENT = BY_EMAIL_DAYS_BEFORE_EVENT_FIELD
    way: typing.Literal["by_email"] = "by_email"


class SentByEmailDetailsResponse(serialization.ConfiguredBaseModel):
    # different model in case the database daysBeforeEvent value is not in the enum
    daysBeforeEvent: int = BY_EMAIL_DAYS_BEFORE_EVENT_FIELD
    way: typing.Literal["by_email"] = "by_email"


class ProductOfferCreation(OfferCreationBase):
    category_related_fields: product_category_creation_fields
    stock: StockCreation | None

    class Config:
        extra = "forbid"


class BatchProductOfferCreation(serialization.ConfiguredBaseModel):
    product_offers: list[ProductOfferCreation]
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD

    @pydantic.validator("product_offers")
    def validate_product_offer_list(cls, product_offers: list[ProductOfferCreation]) -> list[ProductOfferCreation]:
        if len(product_offers) > 50:
            raise ValueError("Maximum number of product offers is 50")
        return product_offers


class ProductOfferByEanCreation(serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        ean: str = EAN_FIELD
    else:
        ean: pydantic.constr(min_length=13, max_length=13) = EAN_FIELD
    id_at_provider: str | None = ID_AT_PROVIDER_FIELD
    stock: StockCreation

    class Config:
        extra = "forbid"


class ProductsOfferByEanCreation(serialization.ConfiguredBaseModel):
    products: list[ProductOfferByEanCreation] = pydantic.Field(
        description="List of product to create or update", max_items=500
    )
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD

    class Config:
        extra = "forbid"


class DecimalPriceGetterDict(GetterDict):
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        if key == "price" and isinstance(self._obj.price, decimal.Decimal):
            return finance_utils.to_eurocents(self._obj.price)
        return super().get(key, default)


class PriceCategoryCreation(serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        label: str = PRICE_CATEGORY_LABEL_FIELD
    else:
        label: pydantic.constr(min_length=1, max_length=50) = PRICE_CATEGORY_LABEL_FIELD
    price: pydantic.StrictInt = PRICE_FIELD

    @pydantic.validator("price")
    def price_must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Value must be positive")
        return value

    class Config:
        getter_dict = DecimalPriceGetterDict


class PriceCategoriesCreation(serialization.ConfiguredBaseModel):
    price_categories: typing.List[PriceCategoryCreation] = PRICE_CATEGORIES_FIELD

    class Config:
        extra = "forbid"


class EventOfferCreation(OfferCreationBase):
    category_related_fields: event_category_creation_fields
    duration_minutes: int | None = DURATION_MINUTES_FIELD
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD
    ticket_collection: SentByEmailDetails | OnSiteCollectionDetails | None = TICKET_COLLECTION_FIELD
    price_categories: typing.List[PriceCategoryCreation] | None = PRICE_CATEGORIES_FIELD

    class Config:
        extra = "forbid"


class OfferEditionBase(serialization.ConfiguredBaseModel):
    accessibility: PartialAccessibility | None = pydantic.Field(
        description="Accessibility to disabled people. Leave fields undefined to keep current value"
    )
    booking_email: pydantic.EmailStr | None = BOOKING_EMAIL_FIELD
    is_active: bool | None = pydantic.Field(
        description="Whether the offer is activated. An inactive offer cannot be booked."
    )
    is_duo: bool | None = IS_DUO_BOOKINGS_FIELD
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD

    class Config:
        extra = "forbid"


STOCK_EDITION_FIELD = pydantic.Field(
    description="If stock is set to null, all cancellable bookings (i.e not used) will be cancelled. To prevent from further bookings, you may alternatively set stock.quantity to the bookedQuantity (but not below).",
)


class ProductOfferEdition(OfferEditionBase):
    offer_id: int
    category_related_fields: product_category_edition_fields | None = pydantic.Field(
        None,
        description="To override category related fields, the category must be specified, even if it cannot be changed. Other category related fields may be left undefined to keep their current value.",
    )
    stock: StockEdition | None = STOCK_EDITION_FIELD

    class Config:
        extra = "forbid"


class BatchProductOfferEdition(serialization.ConfiguredBaseModel):
    product_offers: list[ProductOfferEdition]

    @pydantic.validator("product_offers")
    def validate_product_offer_list(cls, product_offers: list[ProductOfferEdition]) -> list[ProductOfferEdition]:
        if len(product_offers) > 50:
            raise ValueError("Maximum number of product offers is 50")
        return product_offers


class ProductOfferByEanEdition(serialization.ConfiguredBaseModel):
    stock: StockEdition | None = STOCK_EDITION_FIELD

    class Config:
        extra = "forbid"


class PriceCategoryEdition(serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        label: str = PRICE_CATEGORY_LABEL_FIELD
    else:
        label: pydantic.constr(min_length=1, max_length=50) | None = PRICE_CATEGORY_LABEL_FIELD
    price: pydantic.StrictInt | None = PRICE_FIELD

    @pydantic.validator("price")
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
    category_related_fields: event_category_edition_fields | None = pydantic.Field(
        None,
        description="To override category related fields, the category must be specified, even if it cannot be changed. Other category related fields may be left undefined to keep their current value.",
    )
    duration_minutes: int | None = DURATION_MINUTES_FIELD
    ticket_collection: SentByEmailDetails | OnSiteCollectionDetails | None = TICKET_COLLECTION_FIELD


class DateCreation(BaseStockCreation):
    beginning_datetime: datetime.datetime = BEGINNING_DATETIME_FIELD
    booking_limit_datetime: datetime.datetime = BOOKING_LIMIT_DATETIME_FIELD
    price_category_id: int

    _validate_beginning_datetime = serialization_utils.validate_datetime("beginning_datetime")
    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")


class DatesCreation(serialization.ConfiguredBaseModel):
    dates: typing.List[DateCreation] = pydantic.Field(
        description="Dates to add to the event. If there are different prices and quantity for the same date, you must add several date objects",
    )

    class Config:
        extra = "forbid"


class PriceCategoryResponse(PriceCategoryCreation):
    id: int


class PriceCategoriesResponse(serialization.ConfiguredBaseModel):
    price_categories: typing.List[PriceCategoryResponse] = PRICE_CATEGORIES_FIELD

    @classmethod
    def build_price_categories(cls, price_categories: list[offers_models.PriceCategory]) -> "PriceCategoriesResponse":
        return cls(price_categories=[PriceCategoryResponse.from_orm(category) for category in price_categories])


class BaseStockResponse(serialization.ConfiguredBaseModel):
    booking_limit_datetime: datetime.datetime | None = BOOKING_LIMIT_DATETIME_FIELD
    dnBookedQuantity: int = pydantic.Field(..., description="Number of bookings.", example=0, alias="bookedQuantity")
    quantity: pydantic.StrictInt | UNLIMITED_LITERAL = QUANTITY_FIELD

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}

    @classmethod
    def build_stock(cls, stock: offers_models.Stock) -> "BaseStockResponse":
        return cls(
            booking_limit_datetime=stock.bookingLimitDatetime,
            dnBookedQuantity=stock.dnBookedQuantity,
            quantity=stock.quantity if stock.quantity is not None else "unlimited",
        )


# FIXME (cepehang, 2023-02-02): remove after price category generation script
class PartialPriceCategoryResponse(serialization.ConfiguredBaseModel):
    id: None = None
    label: None = None
    price: pydantic.StrictInt = PRICE_FIELD

    @classmethod
    def build_partial_price_category(cls, price: decimal.Decimal) -> "PartialPriceCategoryResponse":
        return cls(price=finance_utils.to_eurocents(price))


class DateResponse(BaseStockResponse):
    id: int
    beginning_datetime: datetime.datetime = BEGINNING_DATETIME_FIELD
    booking_limit_datetime: datetime.datetime = BOOKING_LIMIT_DATETIME_FIELD
    price_category: PriceCategoryResponse | PartialPriceCategoryResponse

    @classmethod
    def build_date(cls, stock: offers_models.Stock) -> "DateResponse":
        stock_response = BaseStockResponse.build_stock(stock)
        return cls(
            id=stock.id,
            beginning_datetime=stock.beginningDatetime,  # type: ignore [arg-type]
            price_category=PriceCategoryResponse.from_orm(stock.priceCategory)
            if stock.priceCategory
            else PartialPriceCategoryResponse.build_partial_price_category(stock.price),
            **stock_response.dict(),
        )


class PostDatesResponse(serialization.ConfiguredBaseModel):
    dates: typing.List[DateResponse] = pydantic.Field(description="Dates of the event.")


class OfferResponse(serialization.ConfiguredBaseModel):
    id: int
    accessibility: Accessibility
    booking_email: pydantic.EmailStr | None = BOOKING_EMAIL_FIELD
    description: str | None = DESCRIPTION_FIELD
    external_ticket_office_url: pydantic.HttpUrl | None = EXTERNAL_TICKET_OFFICE_URL_FIELD
    image: ImageResponse | None
    is_duo: bool | None = IS_DUO_BOOKINGS_FIELD
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD
    name: str = NAME_FIELD
    status: offer_mixin.OfferStatus = pydantic.Field(
        ...,
        description="ACTIVE: offer is validated and active.\n\n"
        "DRAFT: offer is still draft and not yet submitted for validation - this status is not applicable to offers created via this API.\n\n"
        "EXPIRED: offer is validated but the booking limit datetime has passed.\n\n"
        "INACTIVE: offer is not active and cannot be booked.\n\n"
        "PENDING: offer is pending for pass Culture rules compliance validation. This step may last 72 hours.\n\n"
        "REJECTED: offer validation has been rejected because it is not compliant with pass Culture rules.\n\n"
        "SOLD_OUT: offer is validated but there is no (more) stock available for booking.",
        example=offer_mixin.OfferStatus.ACTIVE.name,
    )
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}

    @classmethod
    def build_offer(cls, offer: offers_models.Offer) -> "OfferResponse":
        return cls(
            id=offer.id,
            booking_email=offer.bookingEmail,  # type: ignore [arg-type]
            description=offer.description,
            accessibility=Accessibility.from_orm(offer),
            external_ticket_office_url=offer.externalTicketOfficeUrl,  # type: ignore [arg-type]
            image=offer.image,  # type: ignore [arg-type]
            is_duo=offer.isDuo,
            location=DigitalLocation.from_orm(offer) if offer.isDigital else PhysicalLocation.from_orm(offer),
            name=offer.name,
            status=offer.status,  # type: ignore [arg-type]
            withdrawal_details=offer.withdrawalDetails,
        )


class ProductStockResponse(BaseStockResponse):
    price: pydantic.StrictInt = PRICE_FIELD

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


class BatchProductOfferResponse(serialization.ConfiguredBaseModel):
    product_offers: list[ProductOfferResponse]

    @classmethod
    def build_product_offers(cls, offers: list[offers_models.Offer]) -> "BatchProductOfferResponse":
        return cls(product_offers=[ProductOfferResponse.build_product_offer(offer) for offer in offers])


def _serialize_ticket_collection(
    offer: offers_models.Offer,
) -> SentByEmailDetailsResponse | OnSiteCollectionDetailsResponse | None:
    if offer.withdrawalType is None or offer.withdrawalType == offers_models.WithdrawalTypeEnum.NO_TICKET:
        return None
    if offer.withdrawalDelay is None:
        logger.error("Missing withdrawal delay for offer %s", offer.id)
        return None
    if offer.withdrawalType == offers_models.WithdrawalTypeEnum.ON_SITE:
        return OnSiteCollectionDetailsResponse(minutesBeforeEvent=offer.withdrawalDelay / 60)  # type: ignore [arg-type]
    if offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL:
        return SentByEmailDetailsResponse(daysBeforeEvent=offer.withdrawalDelay / (24 * 3600))  # type: ignore [arg-type]
    logger.error("Unknown withdrawal type %s for offer %s", offer.withdrawalType, offer.id)
    return None


class EventOfferResponse(OfferResponse, PriceCategoriesResponse):
    category_related_fields: event_category_reading_fields
    duration_minutes: int | None = DURATION_MINUTES_FIELD
    ticket_collection: SentByEmailDetailsResponse | OnSiteCollectionDetailsResponse | None = TICKET_COLLECTION_FIELD

    @classmethod
    def build_event_offer(cls, offer: offers_models.Offer) -> "EventOfferResponse":
        base_offer_response = OfferResponse.build_offer(offer)

        return cls(
            category_related_fields=serialize_extra_data(offer),
            duration_minutes=offer.durationMinutes,
            ticket_collection=_serialize_ticket_collection(offer),
            price_categories=[
                PriceCategoryResponse.from_orm(price_category) for price_category in offer.priceCategories
            ],
            **base_offer_response.dict(),
        )


class PaginationQueryParams(serialization.ConfiguredBaseModel):
    limit: int = pydantic.Field(50, le=50, gt=0, description="Maximum number of items per page.")
    page: int = pydantic.Field(1, ge=1, description="Page number of the items to return.")


class GetOffersQueryParams(PaginationQueryParams):
    venue_id: int = pydantic.Field(..., description="Venue id to filter offers on. Optional.")


class GetDatesQueryParams(PaginationQueryParams):
    pass


class PaginationLinks(serialization.ConfiguredBaseModel):
    current: str = pydantic.Field(
        ...,
        description="URL of the current page.",
        example=f"{settings.API_URL}/public/offers/v1/products?page=1&limit=50",
    )
    first: str = pydantic.Field(
        ...,
        description="URL of the first page.",
        example=f"{settings.API_URL}/public/offers/v1/products?page=1&limit=50",
    )
    last: str = pydantic.Field(
        ...,
        description="URL of the last page.",
        example=f"{settings.API_URL}/public/offers/v1/products?page=3&limit=50",
    )
    next: str | None = pydantic.Field(
        None,
        description="URL of the next page.",
        example=f"{settings.API_URL}/public/offers/v1/products?page=2&limit=50",
    )
    previous: str | None = pydantic.Field(None, description="URL of the previous page.", example=None)

    @classmethod
    def build_pagination_links(
        cls,
        base_url: str,
        current: int,
        limit: int,
        items_total: int,
        venue_id: int | None = None,
    ) -> "PaginationLinks":
        url_start = f"{base_url}?venueId={venue_id}&" if venue_id is not None else f"{base_url}?"
        return cls(
            first=f"{url_start}page=1&limit={limit}",
            current=f"{url_start}page={current}&limit={limit}",
            last=f"{url_start}page={items_total // limit+1}&limit={limit}",
            next=f"{url_start}page={current + 1}&limit={limit}" if current * limit < items_total else None,
            previous=f"{url_start}page={current - 1}&limit={limit}" if current > 1 else None,
        )


class Pagination(serialization.ConfiguredBaseModel):
    current_page: int = pydantic.Field(..., description="Page number of the returned items.", example=1)
    items_count: int = pydantic.Field(..., description="Number of items returned.", example=50)
    items_total: int = pydantic.Field(..., description="Total number of items.", example=120)
    last_page: int = pydantic.Field(..., description="Last page number.", example=3)
    limit_per_page: int = pydantic.Field(..., description="Maximum number of items per page.", example=50)
    pages_links: PaginationLinks

    @classmethod
    def build_pagination(
        cls,
        base_url: str,
        current_page: int,
        items_count: int,
        items_total: int,
        limit: int,
        venue_id: int | None = None,
    ) -> "Pagination":
        return cls(
            current_page=current_page,
            items_count=items_count,
            items_total=items_total,
            last_page=items_total // limit + 1,
            limit_per_page=limit,
            pages_links=PaginationLinks.build_pagination_links(
                base_url,
                current_page,
                limit,
                items_total,
                venue_id=venue_id,
            ),
        )


class ProductOffersResponse(serialization.ConfiguredBaseModel):
    products: typing.List[ProductOfferResponse]
    pagination: Pagination


class ProductOffersByEanResponse(serialization.ConfiguredBaseModel):
    products: typing.List[ProductOfferResponse]


class EventOffersResponse(serialization.ConfiguredBaseModel):
    events: typing.List[EventOfferResponse]
    pagination: Pagination


class GetDatesResponse(serialization.ConfiguredBaseModel):
    dates: typing.List[DateResponse]
    pagination: Pagination

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}


class OffererResponse(serialization.ConfiguredBaseModel):
    id: int
    dateCreated: datetime.datetime = pydantic.Field(..., alias="createdDatetime")
    name: str = pydantic.Field(example="Structure A")
    siren: str | None = pydantic.Field(example="123456789")


class VenuePhysicalLocation(serialization.ConfiguredBaseModel):
    address: str | None = pydantic.Field(example="55 rue du Faubourg-Saint-Honoré")
    city: str | None = pydantic.Field(example="Paris")
    postalCode: str | None = pydantic.Field(example="75008")
    type: typing.Literal["physical"] = "physical"


class VenueDigitalLocation(serialization.ConfiguredBaseModel):
    type: typing.Literal["digital"] = "digital"


class VenueResponse(serialization.ConfiguredBaseModel):
    comment: str | None = pydantic.Field(
        None, description="Applicable if siret is null and venue is physical.", alias="siretComment", example=None
    )
    dateCreated: datetime.datetime = pydantic.Field(..., alias="createdDatetime")
    id: int
    location: VenuePhysicalLocation | VenueDigitalLocation = pydantic.Field(
        ...,
        description="Location where the offers will be available or will take place. There is exactly one digital venue per offerer, which is listed although its id is not required to create a digital offer (see DigitalLocation model).",
        discriminator="type",
    )
    name: str = pydantic.Field(alias="legalName", example="Palais de l'Élysée")
    publicName: str | None = pydantic.Field(..., description="If null, legalName is used.", example="Élysée")
    siret: str | None = pydantic.Field(
        description="Null when venue is digital or when siretComment field is not null.", example="12345678901234"
    )
    venueTypeCode: VenueTypeEnum = pydantic.Field(alias="activityDomain")  # type: ignore [valid-type]
    accessibility: PartialAccessibility

    @classmethod
    def build_model(cls, venue: offerers_models.Venue) -> "VenueResponse":
        return cls(
            comment=venue.comment,
            dateCreated=venue.dateCreated,
            id=venue.id,
            location=VenuePhysicalLocation(address=venue.address, city=venue.city, postalCode=venue.postalCode)
            if not venue.isVirtual
            else VenueDigitalLocation(),
            name=venue.name,
            publicName=venue.publicName,
            siret=venue.siret,
            venueTypeCode=venue.venueTypeCode.name,
            accessibility=PartialAccessibility.from_orm(venue),
        )

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}


class GetOffererVenuesResponse(serialization.ConfiguredBaseModel):
    offerer: OffererResponse = pydantic.Field(
        ..., description="Offerer to which the venues belong. Entity linked to the api key used."
    )
    venues: typing.List[VenueResponse]


class GetOfferersVenuesResponse(serialization.BaseModel):
    __root__: typing.List[GetOffererVenuesResponse]

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}


class GetOfferersVenuesQuery(serialization.ConfiguredBaseModel):
    siren: str | None = pydantic.Field(example="123456789")


class GetProductsListByEansQuery(serialization.ConfiguredBaseModel):
    eans: str | None = pydantic.Field(example="0123456789123,0123456789124")

    @pydantic.validator("eans")
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
