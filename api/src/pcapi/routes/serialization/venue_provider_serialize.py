from datetime import datetime
from typing import Any
from typing import List

from pydantic.v1.main import BaseModel

from pcapi.core.providers.models import VenueProvider
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class PostVenueProviderBody(BaseModel):
    venueId: int
    providerId: int
    venueIdAtOfferProvider: str | None
    price: str | None
    # absent/ignored for regular providers, required for cinema-related providers
    isDuo: bool | None
    quantity: int | None
    isActive: bool | None


class ProviderResponse(BaseModel):
    name: str
    id: int
    isActive: bool
    hasOffererProvider: bool

    class Config:
        orm_mode = True


class VenueProviderResponse(BaseModel):
    id: int
    isActive: bool
    isDuo: bool | None
    isFromAllocineProvider: bool
    lastSyncDate: datetime | None
    nOffers: int
    price: float | None
    provider: ProviderResponse
    quantity: int | None
    venueId: int
    venueIdAtOfferProvider: str | None

    @classmethod
    def from_orm(cls: Any, venue_provider: VenueProvider) -> "VenueProviderResponse":
        result = super().from_orm(venue_provider)

        if not venue_provider.isFromAllocineProvider:
            result.isDuo = venue_provider.isDuoOffers

        return result

    class Config:
        orm_mode = True


class ListVenueProviderResponse(BaseModel):
    venue_providers: List[VenueProviderResponse]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class ListVenueProviderQuery(BaseModel):
    venue_id: int

    class Config:
        alias_generator = to_camel
        extra = "forbid"
