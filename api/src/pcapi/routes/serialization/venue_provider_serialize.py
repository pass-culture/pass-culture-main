from datetime import datetime
from typing import Any
from typing import List

from pydantic.main import BaseModel

from pcapi.core.providers.models import VenueProvider
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class PostVenueProviderBody(BaseModel):
    venueId: str
    providerId: str
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

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class VenueProviderResponse(BaseModel):
    id: str
    idAtProviders: str | None
    dateModifiedAtLastProvider: datetime | None
    isActive: bool
    isFromAllocineProvider: bool
    lastProviderId: str | None
    lastSyncDate: datetime | None
    nOffers: int
    providerId: str
    venueId: str
    venueIdAtOfferProvider: str
    provider: ProviderResponse
    # TODO(asaunier): Check if this field is necessary
    fieldsUpdated: List[str]
    quantity: int | None
    isDuo: bool | None
    price: float | None

    _humanize_id = humanize_field("id")
    _humanize_venue_id = humanize_field("venueId")
    _humanize_provider_id = humanize_field("providerId")

    @classmethod
    def from_orm(cls: Any, venue_provider: VenueProvider):  # type: ignore
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

    _dehumanize_venue_id = dehumanize_field("venue_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"
