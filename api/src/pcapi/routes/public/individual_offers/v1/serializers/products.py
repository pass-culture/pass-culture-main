import datetime
import typing

import pydantic as pydantic_v2
import pydantic.v1 as pydantic_v1
from typing_extensions import Annotated

from pcapi.core.offers import models as offers_models
from pcapi.routes import serialization as routes_serialization
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.public.documentation_constants.fields_v2 import fields_v2
from pcapi.routes.public.individual_offers.v1 import serialization as v1_serialization
from pcapi.routes.serialization import HttpBodyModel
from pcapi.serialization import utils as serialization_utils


UNLIMITED_LITERAL = typing.Literal["unlimited"]


def _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates(cls: typing.Any, values: dict) -> dict:
    stock: StockCreation | StockEdition | None = values.get("stock")
    publication_datetime: datetime.datetime | None = values.get("publication_datetime")
    booking_allowed_datetime: datetime.datetime | None = values.get("booking_allowed_datetime")

    if not stock or not stock.booking_limit_datetime:
        return values

    if publication_datetime and stock.booking_limit_datetime < publication_datetime.replace(tzinfo=None):
        raise ValueError("`stock.bookingLimitDatetime` must be after `publicationDatetime`")

    if booking_allowed_datetime and stock.booking_limit_datetime < booking_allowed_datetime.replace(tzinfo=None):
        raise ValueError("`stock.bookingLimitDatetime` must be after `bookingAllowedDatetime`")

    return values


OfferPrice = Annotated[int, pydantic_v2.Field(ge=0, le=30000)]  # 300€ in cents
OfferQuantity = Annotated[int, pydantic_v2.Field(ge=0, le=offers_models.Stock.MAX_STOCK_QUANTITY)]


class ThingStockEdition(HttpBodyModel):
    booking_limit_datetime: datetime.datetime | None = fields_v2.BOOKING_LIMIT_DATETIME_NOT_REQUIRED
    quantity: OfferQuantity | UNLIMITED_LITERAL | None = fields_v2.QUANTITY_NOT_REQUIRED
    price: OfferPrice | None = fields_v2.PRICE_NOT_REQUIRED

    @pydantic_v2.field_validator("booking_limit_datetime")
    @classmethod
    def validate_booking_limit_datetime(cls, value: datetime.datetime | None) -> datetime.datetime | None:
        return serialization_utils.check_date_in_future_and_remove_timezone(value, pydantic_version="v2")


class ThingStockCreation(HttpBodyModel):
    price: OfferPrice = fields_v2.PRICE
    quantity: OfferQuantity | UNLIMITED_LITERAL | None = fields_v2.QUANTITY_NOT_REQUIRED
    booking_limit_datetime: datetime.datetime | None = fields_v2.BOOKING_LIMIT_DATETIME_NOT_REQUIRED

    @pydantic_v2.field_validator("booking_limit_datetime")
    @classmethod
    def validate_booking_limit_datetime(cls, value: datetime.datetime | None) -> datetime.datetime | None:
        return serialization_utils.check_date_in_future_and_remove_timezone(value, pydantic_version="v2")


class Accessibility(HttpBodyModel):
    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool


class ImageBody(HttpBodyModel):
    credit: str | None = fields_v2.IMAGE_CREDIT_NOT_REQUIRED
    file: str = fields_v2.IMAGE_FILE


class OfferCreationBase(HttpBodyModel):
    accessibility: Accessibility
    booking_contact: pydantic_v2.EmailStr | None = fields_v2.OFFER_BOOKING_CONTACT
    booking_email: pydantic_v2.EmailStr | None = fields_v2.OFFER_BOOKING_EMAIL
    # category_related_fields: CategoryRelatedFields = fields_v2.CATEGORY_RELATED_FIELD
    description: str | None = fields_v2.OFFER_DESCRIPTION_WITH_MAX_LENGTH
    external_ticket_office_url: pydantic_v2.HttpUrl | None = fields_v2.OFFER_EXTERNAL_TICKET_OFFICE_URL_NOT_REQUIRED
    image: ImageBody | None = None
    enable_double_bookings: bool | None = fields_v2.OFFER_ENABLE_DOUBLE_BOOKINGS_WITH_DEFAULT
    name: str = fields_v2.OFFER_NAME_WITH_MAX_LENGTH
    withdrawal_details: str | None = fields_v2.OFFER_WITHDRAWAL_DETAILS_FIELD_REQUIRED
    id_at_provider: str | None = fields_v2.ID_AT_PROVIDER_WITH_MAX_LENGTH
    publication_datetime: datetime.datetime | serialization_utils.NOW_LITERAL | None = (
        fields_v2.OFFER_PUBLICATION_DATETIME_WITH_DEFAULT
    )
    booking_allowed_datetime: datetime.datetime | None = fields_v2.OFFER_BOOKING_ALLOWED_DATETIME

    @pydantic_v2.field_validator("booking_allowed_datetime", "publication_datetime")
    @classmethod
    def validate_booking_limit_datetime(
        cls, value: datetime.datetime | serialization_utils.NOW_LITERAL | None
    ) -> datetime.datetime | None:
        return serialization_utils.check_date_in_future_and_remove_timezone(value, pydantic_version="v2")


class StockEdition(v1_serialization.BaseStockEdition):
    price: v1_serialization.offer_price_model | None = fields.PRICE


class StockCreation(v1_serialization.BaseStockCreation):
    price: v1_serialization.offer_price_model = fields.PRICE
    booking_limit_datetime: datetime.datetime | None = fields.BOOKING_LIMIT_DATETIME
    quantity: pydantic_v1.PositiveInt | v1_serialization.UNLIMITED_LITERAL | None = fields.QUANTITY  # type: ignore[assignment]

    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")

    @pydantic_v1.validator("price")
    def price_must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Value must be positive")
        return value


class StockUpsert(StockCreation):
    quantity: pydantic_v1.StrictInt | v1_serialization.UNLIMITED_LITERAL | None = fields.QUANTITY


class ProductOfferEdition(v1_serialization.OfferEditionBase):
    offer_id: int
    category_related_fields: v1_serialization.product_category_edition_fields | None = pydantic_v1.Field(
        None,
        description="To override category related fields, the category must be specified, even if it cannot be changed. Other category related fields may be left undefined to keep their current value.",
    )
    stock: StockEdition | None = fields.STOCK_EDITION
    name: v1_serialization.OfferName | None = fields.OFFER_NAME
    description: str | None = fields.OFFER_DESCRIPTION_WITH_MAX_LENGTH
    enable_double_bookings: bool | None = fields.OFFER_ENABLE_DOUBLE_BOOKINGS_ENABLED

    _validate_stock_booking_limit_datetime = pydantic_v1.root_validator(skip_on_failure=True, allow_reuse=True)(
        _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates
    )


class ProductOfferCreation(v1_serialization.OfferCreationBase):
    category_related_fields: v1_serialization.product_category_creation_fields
    stock: StockCreation | None
    location: (
        v1_serialization.PhysicalLocation | v1_serialization.DigitalLocation | v1_serialization.AddressLocation
    ) = fields.OFFER_LOCATION

    _validate_stock_booking_limit_datetime = pydantic_v1.root_validator(skip_on_failure=True, allow_reuse=True)(
        _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates
    )


class ProductOfferByEanCreation(routes_serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        ean: str = fields.EAN
    else:
        ean: pydantic_v1.constr(min_length=13, max_length=13) = fields.EAN
    stock: StockUpsert
    publication_datetime: datetime.datetime | serialization_utils.NOW_LITERAL | None = (
        fields.OFFER_PUBLICATION_DATETIME_WITH_DEFAULT
    )
    booking_allowed_datetime: datetime.datetime | None = fields.OFFER_BOOKING_ALLOWED_DATETIME

    _validate_publicationDatetime = serialization_utils.validate_timezoned_datetime(
        "publication_datetime",
        always=True,  # to convert default literal `"now"` into an actual datetime
    )
    _validate_bookingAllowedDatetime = serialization_utils.validate_timezoned_datetime("booking_allowed_datetime")
    _validate_stock_booking_limit_datetime = pydantic_v1.root_validator(skip_on_failure=True, allow_reuse=True)(
        _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates
    )

    class Config:
        extra = "forbid"


class ProductsOfferByEanCreation(routes_serialization.ConfiguredBaseModel):
    products: list[ProductOfferByEanCreation] = pydantic_v1.Field(
        description="List of product to create or update", max_items=500
    )
    location: (
        v1_serialization.PhysicalLocation | v1_serialization.DigitalLocation | v1_serialization.AddressLocation
    ) = fields.OFFER_LOCATION

    class Config:
        extra = "forbid"
