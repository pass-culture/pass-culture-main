import datetime
import typing

from psycopg2.extras import NumericRange
from pydantic.v1 import ConstrainedList
from pydantic.v1 import ConstrainedStr
from pydantic.v1 import EmailStr
from pydantic.v1 import HttpUrl
from pydantic.v1 import validator

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import time_to_int
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


class HourType(ConstrainedStr):
    regex = r"^([0-1]\d|2[0-3]):[0-5]\d$"


class TimeSpanType(ConstrainedList):
    min_items = 2
    max_items = 2
    __args__ = (HourType,)
    item_type = HourType


class TimeSpanListType(ConstrainedList):
    max_items = 2
    __args__ = (TimeSpanType,)
    item_type = TimeSpanType


def _convert_to_numeric_ranges(time_spans: list[list[str]]) -> list[NumericRange]:
    if len(time_spans) == 1:
        start, end = time_spans[0]
        return [NumericRange(time_to_int(start), time_to_int(end), "[]")]

    if len(time_spans) == 2:
        raw_start1, raw_end1 = time_spans[0]
        raw_start2, raw_end2 = time_spans[1]

        start1 = time_to_int(raw_start1)
        end1 = time_to_int(raw_end1)
        start2 = time_to_int(raw_start2)
        end2 = time_to_int(raw_end2)

        if (start2 <= start1 <= end2) or (start2 <= end1 <= end2):
            raise ValueError("Time spans overlaps")

        return [
            NumericRange(start1, end1, "[]"),
            NumericRange(start2, end2, "[]"),
        ]

    return []


class OpeningHoursModel(BaseModel):
    MONDAY: TimeSpanListType
    TUESDAY: TimeSpanListType
    WEDNESDAY: TimeSpanListType
    THURSDAY: TimeSpanListType
    FRIDAY: TimeSpanListType
    SATURDAY: TimeSpanListType
    SUNDAY: TimeSpanListType

    @validator("MONDAY", pre=False)
    def validate_monday(cls, monday: list[list[str]], values: dict) -> list[NumericRange]:
        return _convert_to_numeric_ranges(monday)

    @validator("TUESDAY", pre=False)
    def validate_tuesday(cls, tuesday: list[list[str]], values: dict) -> list[NumericRange]:
        return _convert_to_numeric_ranges(tuesday)

    @validator("WEDNESDAY", pre=False)
    def validate_wednesday(cls, wednesday: list[list[str]], values: dict) -> list[NumericRange]:
        return _convert_to_numeric_ranges(wednesday)

    @validator("THURSDAY", pre=False)
    def validate_thursday(cls, thursday: list[list[str]], values: dict) -> list[NumericRange]:
        return _convert_to_numeric_ranges(thursday)

    @validator("FRIDAY", pre=False)
    def validate_friday(cls, friday: list[list[str]], values: dict) -> list[NumericRange]:
        return _convert_to_numeric_ranges(friday)

    @validator("SATURDAY", pre=False)
    def validate_saturday(cls, saturday: list[list[str]], values: dict) -> list[NumericRange]:
        return _convert_to_numeric_ranges(saturday)

    @validator("SUNDAY", pre=False)
    def validate_sunday(cls, sunday: list[list[str]], values: dict) -> list[NumericRange]:
        return _convert_to_numeric_ranges(sunday)


class CreateEventOpeningHoursModel(BaseModel):
    startDatetime: datetime.datetime
    endDatetime: datetime.datetime
    openingHours: OpeningHoursModel


def _format_datetime_tzinfo(dt: datetime.datetime | None) -> datetime.datetime | None:
    if dt and not dt.tzinfo:
        return dt.replace(tzinfo=datetime.timezone.utc)
    return dt


class UpdateEventOpeningHoursModel(BaseModel):
    startDatetime: datetime.datetime | None
    endDatetime: datetime.datetime | None
    openingHours: OpeningHoursModel | None

    @validator("startDatetime")
    def validate_start_datetime(cls, start_datetime: datetime.datetime | None) -> datetime.datetime | None:
        return _format_datetime_tzinfo(start_datetime)

    @validator("endDatetime")
    def validate_end_datetime(cls, end_datetime: datetime.datetime | None) -> datetime.datetime | None:
        return _format_datetime_tzinfo(end_datetime)


class PostDraftOfferBodyModel(BaseModel):
    name: str
    subcategory_id: str
    venue_id: int
    description: str | None = None
    url: HttpUrl | None = None
    extra_data: typing.Any = None
    duration_minutes: int | None = None
    product_id: int | None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchDraftOfferBodyModel(BaseModel):
    name: str | None = None
    subcategory_id: str | None = None
    url: HttpUrl | None = None
    description: str | None = None
    extra_data: dict[str, typing.Any] | None = None
    duration_minutes: int | None = None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

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
    extra_data: typing.Any = None
    id_at_provider: str | None = None
    is_duo: bool | None = None
    offerer_address: offerers_models.OffererAddress | None
    url: HttpUrl | None = None
    withdrawal_delay: int | None = None
    withdrawal_details: str | None = None
    withdrawal_type: offers_models.WithdrawalTypeEnum | None = None

    is_active: bool | None = None

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
