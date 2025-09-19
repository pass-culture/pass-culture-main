from datetime import datetime
from typing import Any

from pydantic.v1.utils import GetterDict

from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import to_camel
from pcapi.utils.date import format_into_utc_date


class ProviderResponse(BaseModel):
    name: str
    id: int
    isActive: bool
    hasOffererProvider: bool

    class Config:
        orm_mode = True


class VenueProviderGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        venue_provider = self._obj
        if key == "isDuo" and not venue_provider.isFromAllocineProvider:
            return venue_provider.isDuoOffers

        return super().get(key, default)


class VenueProviderResponse(BaseModel):
    id: int
    isActive: bool
    isDuo: bool | None
    isFromAllocineProvider: bool
    lastSyncDate: datetime | None
    dateCreated: datetime
    price: float | None
    provider: ProviderResponse
    quantity: int | None
    venueId: int
    venueIdAtOfferProvider: str | None

    class Config:
        orm_mode = True
        getter_dict = VenueProviderGetterDict


class ListVenueProviderResponse(BaseModel):
    venue_providers: list[VenueProviderResponse]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class ListVenueProviderQuery(BaseModel):
    venue_id: int

    class Config:
        alias_generator = to_camel
        extra = "forbid"
