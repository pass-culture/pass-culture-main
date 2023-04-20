from datetime import datetime
from typing import Any
from typing import List

from pydantic.main import BaseModel

from pcapi.core.providers.models import VenueProvider
from pcapi.serialization.utils import humanize_field
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


# TODO(asaunier): We usually exposed every field from ORM but some mightbe unecessary
class ProviderResponse(BaseModel):
    name: str
    enabledForPro: bool
    id: str
    isActive: bool
    localClass: str | None
    hasOffererProvider: bool

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class VenueProviderResponse(BaseModel):
    dateModifiedAtLastProvider: datetime | None
    # TODO(asaunier): Check if this field is necessary
    fieldsUpdated: List[str]
    id: int
    idAtProviders: str | None
    isActive: bool
    isDuo: bool | None
    isFromAllocineProvider: bool
    lastProviderId: str | None
    lastSyncDate: datetime | None
    nOffers: int
    price: float | None
    provider: ProviderResponse
    providerId: int
    quantity: int | None
    venueId: int
    venueIdAtOfferProvider: str

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
