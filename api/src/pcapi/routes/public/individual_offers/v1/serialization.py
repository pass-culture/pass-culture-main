import datetime
import enum
import typing

import pydantic
from pydantic import utils as pydantic_utils
import typing_extensions

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.models import offer_mixin
from pcapi.routes import serialization
from pcapi.serialization import utils as serialization_utils
from pcapi.utils import date as date_utils


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


class DisabilityCompliance(serialization.ConfiguredBaseModel):
    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool


class PhysicalLocation(serialization.ConfiguredBaseModel):
    type: typing.Literal["physical"] = "physical"
    venue_id: int = pydantic.Field(
        ..., example=1, description="You can get the list of your venues with the route GET /venues"
    )


class DigitalLocation(serialization.ConfiguredBaseModel):
    type: typing.Literal["digital"] = "digital"
    url: pydantic.HttpUrl = pydantic.Field(
        ...,
        description="The link users will be redirected to after booking this offer. You may include '{token}', '{email}' and/or '{offerId}' in the URL, which will be replaced respectively by the booking token (use this token to confirm the offer - see API Contremarque), the email of the user who booked the offer and the created offer id",
        example="https://example.com?token={token}&email={email}&offerId={offerId}",
    )


class ImageBody(serialization.ConfiguredBaseModel):
    credit: str | None = pydantic.Field(None, description="The image owner or author.")
    file: str = pydantic.Field(
        ...,
        description="The image file encoded in base64 string. The image format must be PNG or JPEG. The size must be between 400x600 and 800x1200 pixels. The aspect ratio must be 2:3 (portrait format).",
        example="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEUAAACnej3aAAAAAXRSTlMAQObYZgAAAApJREFUCNdjYAAAAAIAAeIhvDMAAAAASUVORK5CYII=",
    )


class ImageResponse(serialization.ConfiguredBaseModel):
    credit: str | None = pydantic.Field(None, description="The image owner or author.")
    url: str = pydantic.Field(
        ..., description="The url where the image is accessible", example="https://example.com/image.png"
    )


class ExtraDataModel(serialization.ConfiguredBaseModel):
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


IS_DUO_BOOKINGS_FIELD = pydantic.Field(
    False,
    description="If set to true, the user may book the offer for two persons. The second item will be delivered at the same price as the first one. The category must be compatible with this feature.",
    alias="enableDoubleBookings",
)
BOOKING_EMAIL_FIELD = pydantic.Field(
    None, description="The recipient email for notifications about bookings, cancellations, etc."
)
CATEGORY_RELATED_FIELD_DESCRIPTION = (
    "The cultural category the offer belongs to. According to the category, some fields may or must be specified."
)
CATEGORY_RELATED_FIELD = pydantic.Field(..., description=CATEGORY_RELATED_FIELD_DESCRIPTION)
DESCRIPTION_FIELD = pydantic.Field(
    None, description="The offer description", example="A great book for kids and old kids.", max_length=1000
)
DISABILITY_COMPLIANCE_FIELD = pydantic.Field(..., description="Specify if the offer is accessible to disabled people.")
EXTERNAL_TICKET_OFFICE_URL_FIELD = pydantic.Field(
    None,
    description="This link is displayed to users wishing to book the offer but who do not have (anymore) credit.",
)
IMAGE_FIELD = pydantic.Field(
    None, description="The image illustrating the offer. Offers with images are more likely to be booked."
)
WITHDRAWAL_DETAILS_FIELD = pydantic.Field(
    None,
    description="Further information that will be provided to the beneficiary to ease the offer collection.",
    example="Opening hours, specific office, collection period, access code, email annoucement...",
    alias="itemCollectionDetails",
)
LOCATION_FIELD = pydantic.Field(
    ..., discriminator="type", description="The location where the offer will be available or will take place."
)
NAME_FIELD = pydantic.Field(description="The offer title", example="Le Petit Prince", max_length=90)


class OfferCreationBase(serialization.ConfiguredBaseModel):
    booking_email: pydantic.EmailStr | None = BOOKING_EMAIL_FIELD
    category_related_fields: CategoryRelatedFields = CATEGORY_RELATED_FIELD
    description: str | None = DESCRIPTION_FIELD
    disability_compliance: DisabilityCompliance = DISABILITY_COMPLIANCE_FIELD
    external_ticket_office_url: pydantic.HttpUrl | None = EXTERNAL_TICKET_OFFICE_URL_FIELD
    image: ImageBody | None = IMAGE_FIELD
    is_duo: bool | None = IS_DUO_BOOKINGS_FIELD
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD
    name: str = NAME_FIELD
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD


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


def compute_category_related_fields(offer: offers_models.Offer) -> CategoryRelatedFields:
    category_fields_model = (PRODUCT_CATEGORY_MODELS_BY_SUBCATEGORY | EVENT_CATEGORY_MODELS_BY_SUBCATEGORY)[
        offer.subcategoryId
    ]
    fields = offer.extraData or {}
    if offer.extraData and "musicSubType" in offer.extraData:
        fields["musicType"] = MusicTypeEnum(
            music_types.MUSIC_SUB_TYPES_BY_CODE[int(offer.extraData["musicSubType"])].slug
        )
    if offer.extraData and "showSubType" in offer.extraData:
        fields["showType"] = ShowTypeEnum(show_types.SHOW_SUB_TYPES_BY_CODE[int(offer.extraData["showSubType"])].slug)
    return category_fields_model(**fields, category=offer.subcategory.id)  # type: ignore [operator]


def compute_extra_data(category_related_fields: CategoryRelatedFields) -> dict[str, str]:
    extra_data = {}
    for extra_data_field in ExtraDataModel.__fields__:
        field_value = getattr(category_related_fields, extra_data_field, None)
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


PRODUCT_CATEGORY_MODELS_BY_SUBCATEGORY = {
    subcategory.id: get_category_fields_model(subcategory)
    for subcategory in subcategories.ALL_SUBCATEGORIES
    if subcategory.is_selectable and not subcategory.is_event
}
EVENT_CATEGORY_MODELS_BY_SUBCATEGORY = {
    subcategory.id: get_category_fields_model(subcategory)
    for subcategory in subcategories.ALL_SUBCATEGORIES
    if subcategory.is_selectable and subcategory.is_event
}


if typing.TYPE_CHECKING:
    product_category_fields = CategoryRelatedFields
    event_category_fields = CategoryRelatedFields
else:
    product_category_fields = typing_extensions.Annotated[
        typing.Union[tuple(PRODUCT_CATEGORY_MODELS_BY_SUBCATEGORY.values())],
        pydantic.Field(discriminator="subcategory_id", description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]
    event_category_fields = typing_extensions.Annotated[
        typing.Union[tuple(EVENT_CATEGORY_MODELS_BY_SUBCATEGORY.values())],
        pydantic.Field(discriminator="subcategory_id", description=CATEGORY_RELATED_FIELD_DESCRIPTION),
    ]

BEGINNING_DATETIME_FIELD = pydantic.Field(
    ...,
    description="The timezone aware datetime of the event.",
    example="2023-01-02T00:00:00+01:00",
)
BOOKING_LIMIT_DATETIME_FIELD = pydantic.Field(
    description="The timezone aware datetime after which the offer can no longer be booked.",
    example="2023-01-01T00:00:00+01:00",
)
PRICE_FIELD = pydantic.Field(..., description="The offer price in euro cents.", example=1000)
QUANTITY_FIELD = pydantic.Field(
    ...,
    description="The quantity of items allocated to pass Culture. Value 'unlimited' is used for infinite items.",
    example=10,
)


class BaseStockCreation(serialization.ConfiguredBaseModel):
    price: pydantic.StrictInt = PRICE_FIELD
    quantity: pydantic.StrictInt | typing.Literal["unlimited"] = QUANTITY_FIELD

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


class StockCreation(BaseStockCreation):
    booking_limit_datetime: datetime.datetime | None = BOOKING_LIMIT_DATETIME_FIELD

    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")


class DateCreation(BaseStockCreation):
    beginning_datetime: datetime.datetime = BEGINNING_DATETIME_FIELD
    booking_limit_datetime: datetime.datetime = BOOKING_LIMIT_DATETIME_FIELD

    _validate_beginning_datetime = serialization_utils.validate_datetime("beginning_datetime")
    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")


ON_SITE_MINUTES_BEFORE_EVENT = typing.Literal[0, 15, 30, 60, 120, 240, 1440, 2880]
BY_EMAIL_DAYS_BEFORE_EVENT = typing.Literal[1, 2, 3, 4, 5, 6, 7]


class OnSiteCollectionDetails(serialization.ConfiguredBaseModel):
    minutesBeforeEvent: ON_SITE_MINUTES_BEFORE_EVENT = pydantic.Field(
        ...,
        description="The number of minutes before the event when the ticket may be collected. Only some values are accepted (between 0 minutes and 48 hours).",
        example=0,
    )
    way: typing.Literal["on_site"]


class SentByEmailDetails(serialization.ConfiguredBaseModel):
    daysBeforeEvent: BY_EMAIL_DAYS_BEFORE_EVENT = pydantic.Field(
        ...,
        description="The number of days before the event when the ticket will be sent. Only some values are accepted (1 to 7).",
        example=1,
    )
    way: typing.Literal["by_email"]


class ProductOfferCreation(OfferCreationBase):
    category_related_fields: product_category_fields
    stock: StockCreation | None


class EventOfferCreation(OfferCreationBase):
    category_related_fields: event_category_fields
    dates: typing.List[DateCreation] | None = pydantic.Field(
        None,
        description="The dates of your event. If there are different prices and quantity for the same date, you must add several date objects",
    )
    event_duration: int | None = pydantic.Field(description="The event duration in minutes", example=60)
    ticket_collection: SentByEmailDetails | OnSiteCollectionDetails | None = pydantic.Field(
        None,
        description="The way the ticket will be collected. Leave empty if there is no ticket. Only some categories are compatible with tickets.",
        discriminator="way",
    )


class AdditionalDatesCreation(serialization.ConfiguredBaseModel):
    additional_dates: typing.List[DateCreation] | None = pydantic.Field(
        None,
        description="The dates of your event. If there are different prices and quantity for the same date, you must add several date objects",
    )


class BaseStockResponseGetter(pydantic_utils.GetterDict):
    def get(self, key: typing.Any, default: typing.Any = None) -> typing.Any:
        stock: offers_models.Stock = self._obj
        if key == "price":
            return finance_utils.to_eurocents(stock.price)
        if key == "quantity":
            return stock.quantity if stock.quantity is not None else "unlimited"

        return super().get(key, default)


class BaseStockResponse(serialization.ConfiguredBaseModel):
    booking_limit_datetime: datetime.datetime | None = BOOKING_LIMIT_DATETIME_FIELD
    price: pydantic.StrictInt = PRICE_FIELD
    quantity: pydantic.StrictInt | typing.Literal["unlimited"] = QUANTITY_FIELD

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}
        getter_dict = BaseStockResponseGetter


class DateResponse(BaseStockResponse):
    id: int
    beginning_datetime: datetime.datetime = BEGINNING_DATETIME_FIELD
    booking_limit_datetime: datetime.datetime = BOOKING_LIMIT_DATETIME_FIELD


class AdditionalDatesResponse(serialization.ConfiguredBaseModel):
    additional_dates: typing.List[DateResponse] | None = pydantic.Field(None, description="The new dates created.")


class OfferResponseGetter(pydantic_utils.GetterDict):
    def get(self, key: typing.Any, default: typing.Any = None) -> typing.Any:
        offer: offers_models.Offer = self._obj
        if key == "disability_compliance":
            return DisabilityCompliance.from_orm(self)
        if key == "location":
            return DigitalLocation.from_orm(offer) if offer.isDigital else PhysicalLocation.from_orm(offer)

        return super().get(key, default)


class OfferResponse(serialization.ConfiguredBaseModel):
    id: int
    booking_email: pydantic.EmailStr | None = BOOKING_EMAIL_FIELD
    description: str | None = DESCRIPTION_FIELD
    disability_compliance: DisabilityCompliance = DISABILITY_COMPLIANCE_FIELD
    external_ticket_office_url: pydantic.HttpUrl | None = EXTERNAL_TICKET_OFFICE_URL_FIELD
    image: ImageResponse | None = IMAGE_FIELD
    is_duo: bool | None = IS_DUO_BOOKINGS_FIELD
    location: PhysicalLocation | DigitalLocation = LOCATION_FIELD
    name: str = NAME_FIELD
    status: offer_mixin.OfferStatus = pydantic.Field(
        ...,
        description="ACTIVE: the offer is validated and active.\n\n"
        "DRAFT: the offer is still draft and not yet submitted for validation - this status is not applicable to offers created via this API.\n\n"
        "EXPIRED: the offer is validated but the booking limit datetime has passed.\n\n"
        "INACTIVE: the offer is not active and cannot be booked.\n\n"
        "PENDING: the offer is pending for pass Culture rules compliance validation. This step may last 72 hours.\n\n"
        "REJECTED: the offer validation has been rejected because it is not compliant with pass Culture rules.\n\n"
        "SOLD_OUT: the offer is validated but there is no (more) stock available for booking.",
    )
    withdrawal_details: str | None = WITHDRAWAL_DETAILS_FIELD

    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}
        getter_dict = OfferResponseGetter


class ProductResponseGetter(OfferResponseGetter):
    def get(self, key: typing.Any, default: typing.Any = None) -> typing.Any:
        product: offers_models.Offer = self._obj
        if key == "category_related_fields":
            return compute_category_related_fields(product)
        if key == "stock":
            return BaseStockResponse.from_orm(product.stock) if product.stock else None

        return super().get(key, default)


class ProductOfferResponse(OfferResponse):
    category_related_fields: product_category_fields
    stock: BaseStockResponse | None

    class Config:
        getter_dict = ProductResponseGetter
