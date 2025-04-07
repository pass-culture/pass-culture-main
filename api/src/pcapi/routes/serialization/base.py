import typing

from psycopg2.extras import NumericRange
import pydantic.v1 as pydantic_v1
from pydantic.v1 import validator

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.routes.serialization import BaseModel
from pcapi.utils.date import time_str_to_int


class VenueResponseGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        if key == "openingHours":
            return self._obj.opening_hours
        if key == "externalAccessibilityData":
            if not self._obj.accessibilityProvider:
                return None
            accessibility_infos = self._obj.accessibilityProvider.externalAccessibilityData
            return acceslibre_serializers.ExternalAccessibilityDataModel.from_accessibility_infos(accessibility_infos)
        if key == "externalAccessibilityUrl":
            if not self._obj.accessibilityProvider:
                return None
            return self._obj.accessibilityProvider.externalAccessibilityUrl
        if key == "externalAccessibilityId":
            if not self._obj.accessibilityProvider:
                return None
            return self._obj.accessibilityProvider.externalAccessibilityId
        return super().get(key, default)


class BaseVenueResponse(BaseModel):
    isVirtual: bool
    name: str

    street: str | None
    bannerUrl: str | None
    contact: offerers_schemas.VenueContactModel | None
    city: str | None
    description: offerers_schemas.VenueDescription | None
    externalAccessibilityData: acceslibre_serializers.ExternalAccessibilityDataModel | None
    externalAccessibilityUrl: str | None
    externalAccessibilityId: str | None
    isOpenToPublic: bool
    isPermanent: bool | None
    latitude: float | None
    longitude: float | None
    postalCode: str | None
    publicName: str | None
    openingHours: dict | None
    withdrawalDetails: str | None

    class Config:
        orm_mode = True
        getter_dict = VenueResponseGetterDict


class ListOffersVenueResponseModel(BaseModel):
    id: int
    isVirtual: bool
    name: str
    offererName: str
    publicName: str | None
    departementCode: str | None


class OpeningHoursModel(BaseModel):
    weekday: str
    timespan: list[list[str]] | None

    @validator("timespan", each_item=True)
    def convert_to_numeric_ranges(cls, timespan: list[str]) -> NumericRange:
        start, end = timespan
        return NumericRange(time_str_to_int(start), time_str_to_int(end), "[]")

    @validator("weekday", each_item=True)
    def return_weekday_upper(cls, weekday: str) -> str:
        return weekday.upper()
