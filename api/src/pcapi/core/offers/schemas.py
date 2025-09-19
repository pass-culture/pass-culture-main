import datetime
import re
import typing

from pydantic.v1 import EmailStr
from pydantic.v1 import Field
from pydantic.v1 import HttpUrl
from pydantic.v1 import StrictInt
from pydantic.v1 import root_validator
from pydantic.v1 import validator

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.core.opening_hours import schemas as opening_hours_schemas
from pcapi.core.shared import schemas as shared_schemas
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.public.individual_offers.v1 import serialization as individual_offers_v1_serialization
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import to_camel


OFFER_DESCRIPTION_MAX_LENGTH = 10_000


def check_offer_name_length_is_valid(offer_name: str) -> None:
    max_offer_name_length = 90
    if len(offer_name) > max_offer_name_length:
        api_error = ApiErrors()
        api_error.add_error("name", "Le titre de l’offre doit faire au maximum 90 caractères.")
        raise api_error


def extract_youtube_video_id(url: str) -> str | None:
    if not isinstance(url, str):
        return None

    youtube_regex = (
        r"(https?://)?"
        r"(www\.)?"
        r"(m\.)?"
        r"(youtube\.com|youtu\.be)"
        r'(/watch\?v=|/embed/|/v/|/e/|/shorts/|/)(?P<video_id>[^"&?\/\s]{11})'
    )
    pattern = re.compile(youtube_regex)
    if match := pattern.match(url):
        return match.group("video_id")

    return None


def check_video_url(video_url: HttpUrl | None) -> str | None:
    if not video_url:
        return None

    video_id = extract_youtube_video_id(video_url)
    if not video_id:
        raise ApiErrors(errors={"videoUrl": ["Veuillez renseigner une URL provenant de la plateforme Youtube"]})
    return video_id


class PostDraftOfferBodyModel(BaseModel):
    name: str
    subcategory_id: str
    venue_id: int
    description: str | None = Field(max_length=OFFER_DESCRIPTION_MAX_LENGTH)
    url: HttpUrl | None = None
    extra_data: typing.Any = None
    duration_minutes: int | None = None
    product_id: int | None
    video_url: HttpUrl | None
    # These props become mandatory when `WIP_ENABLE_NEW_OFFER_CREATION_FLOW` feature flag is enabled.
    # They are optional here in order to not break the existing POST `/offers/drafts` route while both flows coexist.
    audio_disability_compliant: bool | None
    mental_disability_compliant: bool | None
    motor_disability_compliant: bool | None
    visual_disability_compliant: bool | None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    @validator("video_url", pre=True)
    def clean_video_url(cls, v: str) -> str | None:
        if v == "":
            return None
        return v

    @validator("video_url")
    def validate_video_url(cls, video_url: HttpUrl, values: dict) -> str:
        check_video_url(video_url)
        return video_url

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchDraftOfferBodyModel(BaseModel):
    name: str | None = None
    subcategory_id: str | None = None
    url: HttpUrl | None = None
    description: str | None = Field(max_length=OFFER_DESCRIPTION_MAX_LENGTH)
    extra_data: dict[str, typing.Any] | None = None
    duration_minutes: int | None = None
    video_url: HttpUrl | None
    audio_disability_compliant: bool | None
    mental_disability_compliant: bool | None
    motor_disability_compliant: bool | None
    visual_disability_compliant: bool | None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    @validator("video_url", pre=True)
    def clean_video_url(cls, v: str) -> str | None:
        if v == "":
            return None
        return v

    @validator("video_url")
    def validate_video_url(cls, video_url: HttpUrl, values: dict) -> str:
        check_video_url(video_url)
        return video_url

    @validator("subcategory_id", pre=True)
    def validate_subcategory_id(cls, subcategory_id: str, values: dict) -> str:
        from .validation import check_offer_subcategory_is_valid

        check_offer_subcategory_is_valid(subcategory_id)
        return subcategory_id

    class Config:
        alias_generator = to_camel
        extra = "forbid"


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
        alias_generator = to_camel
        extra = "forbid"


class UpdateOffer(BaseModel):
    name: str | None = None
    audio_disability_compliant: bool | None = None
    mental_disability_compliant: bool | None = None
    motor_disability_compliant: bool | None = None
    visual_disability_compliant: bool | None = None

    address: offerers_schemas.AddressBodyModel | None = None
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

    class Config:
        arbitrary_types_allowed = True
        alias_generator = to_camel
        extra = "forbid"


class OfferOpeningHoursSchema(BaseModel):
    openingHours: opening_hours_schemas.WeekdayOpeningHoursTimespans

    class Config:
        use_enum_values = True


class SerializedProductsStocks(typing.TypedDict):
    quantity: StrictInt | individual_offers_v1_serialization.UNLIMITED_LITERAL | None
    price: int
    booking_limit_datetime: datetime.datetime | None
    publication_datetime: datetime.datetime | None
    booking_allowed_datetime: datetime.datetime | None


class CreateOrUpdateEANOffersRequest(BaseModel):
    serialized_products_stocks: dict[str, SerializedProductsStocks]
    venue_id: int
    provider_id: int
    address_id: int | None
    address_label: str | None


class EventStockCreateBodyModel(BaseModel):
    beginning_datetime: datetime.datetime
    price_category_id: int
    quantity: int | None = Field(None, ge=0, le=offers_models.Stock.MAX_STOCK_QUANTITY)
    booking_limit_datetime: datetime.datetime | None

    _validate_beginning_datetime = shared_schemas.validate_datetime("beginning_datetime")
    _validate_booking_limit_datetime = shared_schemas.validate_datetime("booking_limit_datetime")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EventStocksBulkCreateBodyModel(BaseModel):
    offer_id: int
    stocks: list[EventStockCreateBodyModel]

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EventStockUpdateBodyModel(EventStockCreateBodyModel):
    id: int

    class Config:
        alias_generator = to_camel
        extra = "forbid"
