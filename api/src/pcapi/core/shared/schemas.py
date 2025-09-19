import datetime
import typing

from pydantic import v1 as pydantic_v1
from pydantic.v1 import BaseModel as PydanticBaseModel

from pcapi.routes.serialization import BaseModel
from pcapi.utils import date as date_utils


NOW_LITERAL = typing.Literal["now"]


class AccessibilityComplianceMixin(PydanticBaseModel):
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None


def check_date_in_future_and_remove_timezone(value: datetime.datetime | NOW_LITERAL | None) -> datetime.datetime | None:
    if not value:
        return None
    if value == "now":
        return date_utils.get_naive_utc_now()

    assert isinstance(value, datetime.datetime)  # to make mypy happy

    if value.tzinfo is None:
        raise ValueError("The datetime must be timezone-aware.")
    no_tz_value = date_utils.as_utc_without_timezone(value)
    if no_tz_value < datetime.datetime.utcnow():
        raise ValueError("The datetime must be in the future.")
    return no_tz_value


def validate_datetime(field_name: str, always: bool = False) -> classmethod:
    return pydantic_v1.validator(field_name, pre=False, allow_reuse=True, always=always)(
        check_date_in_future_and_remove_timezone
    )


class AddressResponseModel(BaseModel):
    id: int
    banId: str | None
    inseeCode: str | None
    postalCode: str
    street: str | None
    city: str
    latitude: float
    longitude: float
    departmentCode: str | None

    class Config:
        orm_mode = True

    @pydantic_v1.validator("latitude", "longitude")
    def round(cls, value: float) -> float:
        """Rounding to five digits to keep consistency
        with the model definition.
        """
        return round(value, 5)


class AddressResponseIsLinkedToVenueModel(AddressResponseModel):
    label: str | None = None
    id_oa: int
    isLinkedToVenue: bool | None
    isManualEdition: bool
