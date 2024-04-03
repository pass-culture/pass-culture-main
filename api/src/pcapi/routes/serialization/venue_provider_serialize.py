from datetime import datetime
import decimal
from typing import Any

import pydantic.v1

from pcapi.core.providers.models import VenueProvider
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class PostVenueProviderBody(BaseModel):
    venueId: int
    providerId: int
    venueIdAtOfferProvider: str | None
    price: decimal.Decimal | None
    # absent/ignored for regular providers, required for cinema-related providers
    isDuo: bool | None
    quantity: int | None
    isActive: bool | None

    @pydantic.v1.validator("price")
    def price_must_be_positive(cls, value: decimal.Decimal | None) -> decimal.Decimal | None:
        if not value:
            return value
        if value < 0:
            raise ValueError("Le prix doit être positif.")
        return value


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
    venue_providers: list[VenueProviderResponse]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class ListVenueProviderQuery(BaseModel):
    venue_id: int

    class Config:
        alias_generator = to_camel
        extra = "forbid"
