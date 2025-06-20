import datetime
import typing

from psycopg2.extras import NumericRange
from pydantic.v1 import ConstrainedList
from pydantic.v1 import EmailStr
from pydantic.v1 import Field
from pydantic.v1 import HttpUrl
from pydantic.v1 import root_validator
from pydantic.v1 import validator

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization import utils as serialization_utils
from pcapi.utils.date import time_to_int
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


OFFER_DESCRIPTION_MAX_LENGTH = 10_000


class TimeSpan(BaseModel):
    open: datetime.time
    close: datetime.time

    @root_validator(pre=False)
    def validate_open_is_before_close(cls, values: dict) -> dict:
        open_value: str | None = values.get("open")
        close_value: str | None = values.get("close")

        if not open_value or not close_value:
            return values

        if open_value > close_value:
            raise ValueError("`open` should be before `close`")

        return values


class TimeSpanListType(ConstrainedList):
    max_items = 2
    __args__ = (TimeSpan,)
    item_type = TimeSpan


def _convert_to_numeric_ranges(time_spans: list[TimeSpan]) -> list[NumericRange]:
    if len(time_spans) == 1:
        open_value = time_spans[0].open
        close = time_spans[0].close
        return [NumericRange(time_to_int(open_value), time_to_int(close), "[]")]

    if len(time_spans) == 2:
        validate_time_spans_dont_overlap(time_spans)
        open1, close1 = _get_open_and_close_time_as_int(time_spans[0])
        open2, close2 = _get_open_and_close_time_as_int(time_spans[1])

        return [
            NumericRange(open1, close1, "[]"),
            NumericRange(open2, close2, "[]"),
        ]

    return []


def validate_time_spans_dont_overlap(time_spans: list[TimeSpan]) -> None:
    if len(time_spans) != 2:
        return

    sorted_time_spans = sorted(time_spans, key=lambda ts: ts.open)
    open1, close1 = _get_open_and_close_time_as_int(sorted_time_spans[0])
    open2, close2 = _get_open_and_close_time_as_int(sorted_time_spans[1])

    if open1 > close1 or open2 > close2:
        raise ValueError("`open` should be before `close`")

    # Because we sorted the timespans by `open` time, we can assume 3 possibilities:
    # Case ok: first time span is before second time span
    # open 1 --- close 1 --- open 2 --- close 2
    # ^             ^             ^             ^
    # |             |             |             |
    # -------------                -------------
    # Equality is weird but technically ok

    # Case not ok: second time span starts before first time span ends
    #              -- open 2 is before close 1
    # open 1 --- open 2 --- close 1 --- close 2
    # ^             ^             ^             ^
    # |             |             |             |
    #  -------------|-------------             |
    #                ---------------------------
    # Case not ok: second time span is inside first time span
    # open 1 --- open 2 --- close 2 --- close 1
    # ^             ^             ^             ^
    # |             |             |             |
    # |              -------------              |
    #  -----------------------------------------

    # We can sum that up in this deceptively simple condition:
    if open2 < close1:
        raise ValueError("Time spans overlaps")


def _get_open_and_close_time_as_int(time_span: TimeSpan) -> tuple[int, int]:
    return time_to_int(time_span.open), time_to_int(time_span.close)


class OpeningHoursByWeekDayModel(BaseModel):
    MONDAY: TimeSpanListType
    TUESDAY: TimeSpanListType
    WEDNESDAY: TimeSpanListType
    THURSDAY: TimeSpanListType
    FRIDAY: TimeSpanListType
    SATURDAY: TimeSpanListType
    SUNDAY: TimeSpanListType

    _convert_monday = validator("MONDAY", allow_reuse=True)(_convert_to_numeric_ranges)
    _convert_tuesday = validator("TUESDAY", allow_reuse=True)(_convert_to_numeric_ranges)
    _convert_wednesday = validator("WEDNESDAY", allow_reuse=True)(_convert_to_numeric_ranges)
    _convert_thursday = validator("THURSDAY", allow_reuse=True)(_convert_to_numeric_ranges)
    _convert_friday = validator("FRIDAY", allow_reuse=True)(_convert_to_numeric_ranges)
    _convert_saturday = validator("SATURDAY", allow_reuse=True)(_convert_to_numeric_ranges)
    _convert_sunday = validator("SUNDAY", allow_reuse=True)(_convert_to_numeric_ranges)

    class Config:
        extra = "forbid"


class CreateEventOpeningHoursModel(BaseModel):
    startDatetime: datetime.datetime
    endDatetime: datetime.datetime | None
    openingHours: OpeningHoursByWeekDayModel

    _validate_startDatetime = serialization_utils.validate_datetime("startDatetime")
    _validate_endDatetime = serialization_utils.validate_datetime("endDatetime")

    @root_validator(pre=False)
    def validate_event_opening_hours_dates(cls, values: dict) -> dict:
        end_datetime: datetime.datetime | None = values.get("endDatetime")
        start_datetime: datetime.datetime | None = values.get("startDatetime")
        now = datetime.datetime.utcnow()

        if not end_datetime or not start_datetime:
            return values

        if end_datetime < start_datetime:
            raise ValueError("`endDatetime` must be superior to `startDatetime`")

        if (end_datetime - start_datetime).days > 365:
            raise ValueError("Your event cannot last for more than a year")

        if (end_datetime - now).days > 730:  # more than 2 years
            raise ValueError("Your event cannot end in more than two years from now")

        return values

    class Config:
        extra = "forbid"


class UpdateEventOpeningHoursModel(CreateEventOpeningHoursModel):
    startDatetime: datetime.datetime | None  # type: ignore[assignment]
    endDatetime: datetime.datetime | None
    openingHours: OpeningHoursByWeekDayModel | None  # type: ignore[assignment]


class PostDraftOfferBodyModel(BaseModel):
    name: str
    subcategory_id: str
    venue_id: int
    description: str | None = Field(max_length=OFFER_DESCRIPTION_MAX_LENGTH)
    url: HttpUrl | None = None
    extra_data: typing.Any = None
    duration_minutes: int | None = None
    product_id: int | None

    @validator("name", pre=True)
    def validate_name(cls, name: str, values: dict) -> str:
        check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"


class PatchDraftOfferBodyModel(BaseModel):
    name: str | None = None
    subcategory_id: str | None = None
    url: HttpUrl | None = None
    description: str | None = Field(max_length=OFFER_DESCRIPTION_MAX_LENGTH)
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
        alias_generator = serialization_utils.to_camel
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
        alias_generator = serialization_utils.to_camel
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
        alias_generator = serialization_utils.to_camel
        extra = "forbid"
