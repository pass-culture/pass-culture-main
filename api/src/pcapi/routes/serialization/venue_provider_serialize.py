from datetime import datetime
import decimal
from typing import Any

import pydantic.v1
from pydantic.v1.utils import GetterDict

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


class VenueProviderGetterDict(GetterDict):
    def get(self, key: str, default: Any | None = None) -> Any:
        venue_provider = self._obj
        if key == "price" and venue_provider.isFromAllocineProvider:
            for price_rule in venue_provider.priceRules:
                if price_rule.priceRule():
                    return price_rule.price
            return None
        if key == "isDuo" and not venue_provider.isFromAllocineProvider:
            return venue_provider.isDuoOffers

        return super().get(key, default)


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
