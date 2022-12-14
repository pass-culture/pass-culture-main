import datetime
import enum
import typing

import pydantic
import typing_extensions

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import validation as offers_validation
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.routes import serialization
from pcapi.serialization import utils as serialization_utils
from pcapi.serialization.utils import to_camel


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


class DisabilityCompliance(serialization.BaseModel):
    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool

    class Config:
        alias_generator = to_camel


class PhysicalLocation(serialization.BaseModel):
    type: typing.Literal["physical"]
    venue_id: int = pydantic.Field(
        ..., example=1, description="You can get the list of your venues with the route GET /venues"
    )

    class Config:
        alias_generator = to_camel


class DigitalLocation(serialization.BaseModel):
    type: typing.Literal["digital"]
    url: pydantic.HttpUrl = pydantic.Field(
        ...,
        description="The link users will be redirected to after booking this offer. You may include '{token}', '{email}' and/or '{offerId}' in the URL, which will be replaced respectively by the booking token (use this token to confirm the offer - see API Contremarque), the email of the user who booked the offer and the created offer id",
        example="https://example.com?token={token}&email={email}&offerId={offerId}",
    )


class ImageBody(serialization.BaseModel):
    credit: str | None = pydantic.Field(None, description="The image owner or author.")
    file: str = pydantic.Field(
        ...,
        description="The image file encoded in base64 string. The image format must be PNG or JPEG. The size must be between 400x600 and 800x1200 pixels. The aspect ratio must be 2:3 (portrait format).",
        example="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEUAAACnej3aAAAAAXRSTlMAQObYZgAAAApJREFUCNdjYAAAAAIAAeIhvDMAAAAASUVORK5CYII=",
    )


class ExtraDataModel(pydantic.BaseModel):
    author: str | None
    isbn: str | None = pydantic.Field(None, regex=r"^(\d){13}$", example="9783140464079")
    musicType: MusicTypeEnum | None  # type: ignore [valid-type]
    performer: str | None
    stageDirector: str | None
    showType: ShowTypeEnum | None  # type: ignore [valid-type]
    speaker: str | None
    visa: str | None


class CategoryRelatedFields(ExtraDataModel):
    subcategory_id: str = pydantic.Field(alias="category")


class OfferCreationBase(serialization.BaseModel):
    accept_double_bookings: bool | None = pydantic.Field(
        None,
        description="If set to true, the user may book the offer for two persons. The second item will be delivered at the same price as the first one. The category must be compatible with this feature.",
    )
    booking_email: pydantic.EmailStr | None = pydantic.Field(
        None, description="The recipient email for notifications about bookings, cancellations, etc."
    )
    category_related_fields: CategoryRelatedFields
    description: str | None = pydantic.Field(
        None, description="The offer description", example="A great book for kids and old kids.", max_length=1000
    )
    disability_compliance: DisabilityCompliance
    external_ticket_office_url: pydantic.HttpUrl | None = pydantic.Field(
        None,
        description="This link is displayed to users wishing to book the offer but who do not have (anymore) credit.",
    )
    image: ImageBody | None
    item_collection_details: str | None = pydantic.Field(
        None,
        description="Further information that will be provided to the beneficiary to ease the offer collection.",
        example="Opening hours, specific office, collection period, access code, email annoucement...",
    )
    location: PhysicalLocation | DigitalLocation = pydantic.Field(
        ..., discriminator="type", description="The location where the offer will be available or will take place."
    )
    name: str = pydantic.Field(description="The offer title", example="Le Petit Prince", max_length=90)

    class Config:
        alias_generator = to_camel


PRODUCT_SELECTABLE_SUBCATEGORIES = [
    subcategory
    for subcategory in subcategories.ALL_SUBCATEGORIES
    if subcategory.is_selectable and not subcategory.is_event
]
EVENT_SELECTABLE_SUBCATEGORIES = [
    subcategory for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.is_selectable and subcategory.is_event
]


def get_category_fields_model(subcategory: subcategories.Subcategory) -> pydantic.BaseModel:
    """
    Create dynamic pydantic models to indicate which fields are available for the chosen subcategory,
    without duplicating categories declaration
    """
    specific_fields: dict[typing.Any, typing.Any] = {}
    for field_name, model_field in ExtraDataModel.__fields__.items():
        if field_name in subcategory.conditional_fields:
            is_required = field_name in offers_validation.OFFER_EXTRA_DATA_MANDATORY_FIELDS
            specific_fields[field_name] = (model_field.type_, ... if is_required else model_field.default)

    specific_fields["subcategory_id"] = (
        typing.Literal[subcategory.id],  # pyright: ignore (pylance error message)
        pydantic.Field(alias="category"),
    )

    model = pydantic.create_model(subcategory.id, **specific_fields)
    model.__doc__ = subcategory.pro_label
    return model


if typing.TYPE_CHECKING:
    product_category_fields = CategoryRelatedFields
    event_category_fields = CategoryRelatedFields
else:
    product_category_fields = typing_extensions.Annotated[
        typing.Union[tuple(get_category_fields_model(subcategory) for subcategory in PRODUCT_SELECTABLE_SUBCATEGORIES)],
        pydantic.Field(discriminator="subcategory_id"),
    ]
    event_category_fields = typing_extensions.Annotated[
        typing.Union[tuple(get_category_fields_model(subcategory) for subcategory in EVENT_SELECTABLE_SUBCATEGORIES)],
        pydantic.Field(discriminator="subcategory_id"),
    ]


class BaseStockBody(serialization.BaseModel):
    price: pydantic.StrictInt = pydantic.Field(..., description="The offer price in euro cents.", example=1000)
    quantity: pydantic.StrictInt | typing.Literal["unlimited"]

    @pydantic.validator("price")
    def price_must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("The value must be positive")
        return value

    @pydantic.validator("quantity")
    def quantity_must_be_positive(cls, quantity: int | str) -> int | str:
        if isinstance(quantity, int) and quantity < 0:
            raise ValueError("The value must be positive")
        return quantity

    class Config:
        alias_generator = to_camel


class StockBody(BaseStockBody):
    booking_limit_datetime: datetime.datetime | None = pydantic.Field(
        None,
        description="The timezone aware datetime after which the offer can no longer be booked.",
        example="2023-01-01T00:00:00+01:00",
    )

    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")


class DateBody(BaseStockBody):
    beginning_datetime: datetime.datetime = pydantic.Field(
        ...,
        description="The timezone aware datetime of the event.",
        example="2023-01-02T00:00:00+01:00",
    )
    booking_limit_datetime: datetime.datetime = pydantic.Field(
        ...,
        description="The timezone aware datetime after which the offer can no longer be booked. If no value is provided, the beginning datetime is used.",
        example="2023-01-01T00:00:00+01:00",
    )

    _validate_beginning_datetime = serialization_utils.validate_datetime("beginning_datetime")
    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")


ON_SITE_MINUTES_BEFORE_EVENT = typing.Literal[0, 15, 30, 60, 120, 240, 1440, 2880]
BY_EMAIL_DAYS_BEFORE_EVENT = typing.Literal[1, 2, 3, 4, 5, 6, 7]


class OnSiteCollectionDetails(serialization.BaseModel):
    minutesBeforeEvent: ON_SITE_MINUTES_BEFORE_EVENT = pydantic.Field(
        ...,
        description="The number of minutes before the event when the ticket may be collected. Only some values are accepted (between 0 minutes and 48 hours).",
        example=0,
    )
    way: typing.Literal["on_site"]


class SentByEmailDetails(serialization.BaseModel):
    daysBeforeEvent: BY_EMAIL_DAYS_BEFORE_EVENT = pydantic.Field(
        ...,
        description="The number of days before the event when the ticket will be sent. Only some values are accepted (1 to 7).",
        example=1,
    )
    way: typing.Literal["by_email"]


class ProductOfferCreationBody(OfferCreationBase):
    category_related_fields: product_category_fields
    stock: StockBody | None


class EventOfferCreationBody(OfferCreationBase):
    category_related_fields: event_category_fields
    dates: typing.List[DateBody] | None = pydantic.Field(
        None,
        description="The dates of your event. If there are different prices and quantity for the same date, you should add several date objects",
    )
    event_duration: int | None = pydantic.Field(description="The event duration in minutes", example=60)
    ticket_collection: SentByEmailDetails | OnSiteCollectionDetails | None = pydantic.Field(
        None,
        description="The way the ticket will be collected. Leave empty if there is no ticket. Only some categories are compatible with tickets.",
        discriminator="way",
    )


class OfferResponse(serialization.BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
