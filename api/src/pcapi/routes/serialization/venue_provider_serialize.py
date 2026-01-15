from datetime import datetime
from typing import Annotated

import pydantic as pydantic_v2
from pydantic import RootModel

from pcapi.routes.serialization import HttpBodyModel


class ProviderResponse(HttpBodyModel):
    id: int
    name: str
    enabled_for_pro: bool
    is_active: bool
    has_offerer_provider: bool


class ListProviderResponse(RootModel):
    root: list[ProviderResponse]


class PostVenueProviderBody(HttpBodyModel):
    provider_id: int
    venue_id_at_offer_provider: str | None = None
    price: Annotated[float, pydantic_v2.Field(ge=0)] | None = None
    # absent/ignored for regular providers, required for cinema-related providers
    is_duo: bool | None = None
    quantity: int | None = None
    is_active: bool | None = None


class PutVenueProviderBody(HttpBodyModel):
    venue_id_at_offer_provider: str | None = None
    price: Annotated[float, pydantic_v2.Field(ge=0)] | None = None
    # absent/ignored for regular providers, required for cinema-related providers
    is_duo: bool | None = None
    quantity: int | None = None
    is_active: bool | None = None


class VenueProviderResponse(HttpBodyModel):
    id: int
    isActive: bool
    isDuoOffers: bool | None = pydantic_v2.Field(alias="isDuo")
    isFromAllocineProvider: bool
    lastSyncDate: datetime | None
    dateCreated: datetime
    price: float | None = None
    provider: ProviderResponse
    quantity: int | None = None
    venueId: int
    venueIdAtOfferProvider: str | None


class ListVenueProviderResponse(HttpBodyModel):
    venue_providers: list[VenueProviderResponse]
