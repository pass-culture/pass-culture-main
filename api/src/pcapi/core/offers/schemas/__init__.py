import datetime
import decimal
import typing

from pydantic.v1 import EmailStr
from pydantic.v1 import HttpUrl
from pydantic.v1 import StrictInt
from pydantic.v1 import root_validator
from pydantic.v1 import validator

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.core.opening_hours import schemas as opening_hours_schemas
from pcapi.routes.public.individual_offers.v1 import serialization as individual_offers_v1_serialization
from pcapi.routes.serialization import BaseModel
from pcapi.serialization import utils as serialization_utils

from . import deprecated  # noqa: F401


class CreateOffer(BaseModel):
    name: str
    subcategory_id: str
    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool

    booking_contact: EmailStr | None = None
    booking_email: EmailStr | None = None
    description: str | None = None
    duration_minutes: int | None = None
    external_ticket_office_url: HttpUrl | None = None
    ean: str | None
    extra_data: typing.Any = None
    id_at_provider: str | None = None
    is_duo: bool | None = None
    url: HttpUrl | None = None
    withdrawal_delay: int | None = None
    withdrawal_details: str | None = None
    withdrawal_type: offers_models.WithdrawalTypeEnum | None = None
    video_url: HttpUrl | None = None

    # is_national must be placed after url so that the validator
    # can access the url field in the dict of values
    # (which contains only previously validated fields)
    is_national: bool | None = None

    @root_validator(pre=True)
    def set_ean_from_extra_data(cls, values: dict) -> dict:
        if "extraData" in values and values["extraData"]:
            ean = values["extraData"].get("ean")
            if ean:
                values["ean"] = ean
                values["extraData"].pop("ean")
        return values

    @validator("is_duo")
    def validate_is_duo(cls, is_duo: bool | None) -> bool:
        return bool(is_duo)

    @validator("is_national")
    def validate_is_national(cls, is_national: bool | None, values: dict) -> bool:
        url = values.get("url")
        is_national = True if url else bool(is_national)
        return is_national

    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"


class UpdateOffer(BaseModel):
    name: str | None = None
    audio_disability_compliant: bool | None = None
    mental_disability_compliant: bool | None = None
    motor_disability_compliant: bool | None = None
    visual_disability_compliant: bool | None = None

    location: offerers_schemas.LocationModel | offerers_schemas.LocationOnlyOnVenueModel | None = None
    booking_contact: EmailStr | None = None
    booking_email: EmailStr | None = None
    description: str | None = None
    duration_minutes: int | None = None
    external_ticket_office_url: HttpUrl | None = None
    ean: str | None = None
    extra_data: typing.Any = None
    id_at_provider: str | None = None
    is_duo: bool | None = None
    offerer_address: offerers_models.OffererAddress | None
    url: HttpUrl | None = None
    withdrawal_delay: int | None = None
    withdrawal_details: str | None = None
    withdrawal_type: offers_models.WithdrawalTypeEnum | None = None
    publicationDatetime: datetime.datetime | None
    bookingAllowedDatetime: datetime.datetime | None
    video_url: HttpUrl | None
    subcategory_id: str | None = None

    # is_national must be placed after url so that the validator
    # can access the url field in the dict of values
    # (which contains only previously validated fields)
    is_national: bool | None = None

    should_send_mail: bool | None = None

    @validator("is_duo")
    def validate_is_duo(cls, is_duo: bool | None) -> bool:
        return bool(is_duo)

    @validator("is_national")
    def validate_is_national(cls, is_national: bool | None, values: dict) -> bool:
        url = values.get("url")
        is_national = True if url else bool(is_national)
        return is_national

    @validator("video_url", pre=True)
    def clean_video_url(cls, v: str) -> str | None:
        if v == "":
            return None
        return v

    @validator("video_url")
    def validate_video_url(cls, video_url: HttpUrl, values: dict) -> str:
        offers_validation.check_video_url(video_url)
        return video_url

    class Config:
        arbitrary_types_allowed = True
        alias_generator = serialization_utils.to_camel
        extra = "forbid"


class OfferOpeningHoursSchema(BaseModel):
    openingHours: opening_hours_schemas.WeekdayOpeningHoursTimespans

    class Config:
        use_enum_values = True


class SerializedProductsStock(typing.TypedDict):
    quantity: StrictInt | individual_offers_v1_serialization.UNLIMITED_LITERAL | None
    price: int
    booking_limit_datetime: datetime.datetime | None
    publication_datetime: datetime.datetime | None
    booking_allowed_datetime: datetime.datetime | None


class CreateOrUpdateEANOffersRequest(BaseModel):
    serialized_products_stocks: dict[str, SerializedProductsStock]
    venue_id: int
    provider_id: int
    address_id: int | None
    address_label: str | None


class CreateOfferHighlightRequestBodyModel(BaseModel):
    highlight_ids: list[int]


class ThingStockUpsertInput(typing.TypedDict):
    id: int | None
    activation_codes: list[str] | None
    activation_codes_expiration_datetime: datetime.datetime | None
    booking_limit_datetime: datetime.datetime | None
    price: decimal.Decimal | None
    quantity: int | None
