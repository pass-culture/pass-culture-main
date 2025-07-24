import datetime
import typing

from pydantic.v1 import ConstrainedList
from pydantic.v1 import ConstrainedStr
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
from pcapi.validation.routes.offers import check_offer_name_length_is_valid
from pcapi.validation.routes.offers import check_video_url


OFFER_DESCRIPTION_MAX_LENGTH = 10_000


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
        alias_generator = serialization_utils.to_camel
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


class Hour(ConstrainedStr):
    """defines a time string that matches the HH:MM format"""

    __args__ = (str,)
    regex = r"^(([0-1][0-9])|(2[0-3])):[0-5][0-9]$"
    strip_whitespace = True
    strict = True


class OpeningHours(ConstrainedList):
    """defines start and end opening hours
    eg. ["10:00", "18:00"] (from 10:00 to 18:00)
    """

    __args__ = (Hour,)
    item_type = Hour
    min_items = 2
    max_items = 2
    unique_items = True


class OpeningHoursTimespans(ConstrainedList):
    """defines a whole day's opening hours

    eg. [["10:00", "13:00"], ["14:00", "18:00"]]
    """

    __args__ = (OpeningHours,)
    item_type = OpeningHours
    min_items = 1
    max_items = 2
    unique_items = True


def validate_timespans(timespans: OpeningHoursTimespans | None) -> OpeningHoursTimespans | None:
    """Check that timespans are well-formed (if any)

    -> Each timespan is a (start, end) pair.
    -> Check that start is always before end.
    -> Check that there is no overlapping pair, eg. from 10:00 to
    14:00 and from 13:00 to 17:00.
    """

    def unpack_opening_hours(oh: OpeningHours) -> tuple[datetime.time, datetime.time]:
        start, end = oh
        return datetime.time.fromisoformat(start), datetime.time.fromisoformat(end)

    if timespans is None:
        return None

    # check that start and end pairs are well ordered
    ranges = [unpack_opening_hours(ts) for ts in timespans]

    for start, end in ranges:
        if start >= end:
            raise ValueError(f"opening hours start ({start}) cannot be after end ({end})")

    # check that there is no overlapping (start, end) pair
    ranges = sorted(ranges, key=lambda opening_hours: opening_hours[0])
    previous_end = ranges[0][1]

    for start, end in ranges[1:]:
        if start < previous_end:
            raise ValueError(f"overlapping opening hours: {start} <> {previous_end}")
        previous_end = end

    return timespans


class WeekdayOpeningHoursTimespans(BaseModel):
    MONDAY: OpeningHoursTimespans | None
    TUESDAY: OpeningHoursTimespans | None
    WEDNESDAY: OpeningHoursTimespans | None
    THURSDAY: OpeningHoursTimespans | None
    FRIDAY: OpeningHoursTimespans | None
    SATURDAY: OpeningHoursTimespans | None
    SUNDAY: OpeningHoursTimespans | None

    _validate_monday = validator("MONDAY", allow_reuse=True)(validate_timespans)
    _validate_tuesday = validator("TUESDAY", allow_reuse=True)(validate_timespans)
    _validate_wednesday = validator("WEDNESDAY", allow_reuse=True)(validate_timespans)
    _validate_thursday = validator("THURSDAY", allow_reuse=True)(validate_timespans)
    _validate_friday = validator("FRIDAY", allow_reuse=True)(validate_timespans)
    _validate_saturday = validator("SATURDAY", allow_reuse=True)(validate_timespans)
    _validate_sunday = validator("SUNDAY", allow_reuse=True)(validate_timespans)

    class Config:
        extra = "forbid"


class OfferOpeningHoursSchema(BaseModel):
    openingHours: WeekdayOpeningHoursTimespans

    class Config:
        use_enum_values = True
