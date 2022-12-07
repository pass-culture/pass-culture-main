import datetime
import typing

import pydantic
import pytz
import typing_extensions

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.routes import serialization
from pcapi.serialization.utils import to_camel


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
    credit: str | None
    file: str = pydantic.Field(
        ...,
        description="The image file encoded in base64 string. The image format must be PNG or JPEG. The size must be between 400x600 and 800x1200 pixels. The aspect ratio must be 2:3 (portrait format).",
        example="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEUAAACnej3aAAAAAXRSTlMAQObYZgAAAApJREFUCNdjYAAAAAIAAeIhvDMAAAAASUVORK5CYII=",
    )


class OfferCreationBase(serialization.BaseModel):
    accept_double_bookings: bool | None = pydantic.Field(
        None,
        description="If set to true, the user may book the offer for two persons. The second item will be delivered at the same price as the first one. The category must be compatible with this feature.",
    )
    booking_email: pydantic.EmailStr | None = pydantic.Field(
        None, description="The recipient email for notifications about bookings, cancellations, etc."
    )
    description: str | None = pydantic.Field(
        None, description="The offer description", example="A great book for kids and old kids.", max_length=1000
    )
    disability_compliance: DisabilityCompliance
    external_ticket_office_url: pydantic.HttpUrl | None = pydantic.Field(
        None,
        description="This link is displayed to users wishing to book the offer but who do not have (anymore) credit.",
    )
    image: ImageBody | None
    location: PhysicalLocation | DigitalLocation = pydantic.Field(
        ..., discriminator="type", description="The location where the offer will be available or will take place."
    )
    name: str = pydantic.Field(description="The offer title", example="Le Petit Prince", max_length=90)

    class Config:
        alias_generator = to_camel


class ExtraDataModel(pydantic.BaseModel):
    author: str | None
    isbn: str | None = pydantic.Field(None, regex=r"^(\d){13}$", example="9783140464079")
    musicType: str | None
    performer: str | None
    stageDirector: str | None
    showType: str | None
    speaker: str | None
    visa: str | None


class CategoryRelatedFields(ExtraDataModel):
    subcategory_id: str = pydantic.Field(alias="category")  # pyright: ignore (pylance error message)


PRODUCT_SELECTABLE_SUBCATEGORIES = [
    subcategory
    for subcategory in subcategories.ALL_SUBCATEGORIES
    if subcategory.is_selectable and not subcategory.is_event
]


def get_category_fields_model(subcategory: subcategories.Subcategory) -> pydantic.BaseModel:
    """
    Create dynamic pydantic models to indicate which fields are available for the chosen subcategory,
    without duplicating categories declaration
    """
    specific_fields: dict[typing.Any, typing.Any] = {}
    for field_name, model_field in ExtraDataModel.__fields__.items():
        if field_name in subcategory.conditional_fields:
            specific_fields[field_name] = (model_field.type_, model_field.default)

    specific_fields["subcategory_id"] = (
        typing.Literal[subcategory.id],  # pyright: ignore (pylance error message)
        pydantic.Field(alias="category"),
    )

    model = pydantic.create_model(subcategory.id, **specific_fields)
    model.__doc__ = subcategory.pro_label
    return model


if typing.TYPE_CHECKING:
    category_related_fields = CategoryRelatedFields
else:
    category_related_fields = typing_extensions.Annotated[
        typing.Union[tuple(get_category_fields_model(subcategory) for subcategory in PRODUCT_SELECTABLE_SUBCATEGORIES)],
        pydantic.Field(discriminator="subcategory_id"),
    ]


class StockBody(serialization.BaseModel):
    booking_limit_datetime: datetime.datetime | None = pydantic.Field(
        None,
        description="The timezone aware datetime after which the offer can no longer be booked",
        example="2023-01-01T00:00:00+01:00",
    )
    price: pydantic.StrictInt = pydantic.Field(..., description="The offer price in euro cents", example=1000)
    quantity: pydantic.PositiveInt | typing.Literal["unlimited"]

    @pydantic.validator("booking_limit_datetime")
    def check_booking_limit_timezone(cls, value: datetime.datetime) -> datetime.datetime | None:
        if not value:
            return None
        if value.tzinfo is None:
            raise ValueError("The value must be a timezone-aware datetime or null")
        return value.astimezone(pytz.utc).replace(tzinfo=None)

    @pydantic.validator("price")
    def price_must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("The value must be positive")
        return value

    class Config:
        alias_generator = to_camel


class ProductOfferCreationBody(OfferCreationBase):
    category_related_fields: category_related_fields
    stock: StockBody | None


class OfferResponse(serialization.BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
