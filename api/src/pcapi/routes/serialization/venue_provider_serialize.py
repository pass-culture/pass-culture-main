from datetime import datetime
from typing import Any
from typing import List
from typing import Optional

from pydantic.main import BaseModel

from pcapi.core.providers.models import VenueProvider
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class PostVenueProviderBody(BaseModel):
    venueId: str
    providerId: str
    venueIdAtOfferProvider: Optional[str]
    price: Optional[str]
    isDuo: Optional[bool]
    quantity: Optional[int]
    isActive: Optional[bool]


# TODO(asaunier): We usually exposed every field from ORM but some mightbe unecessary
class ProviderResponse(BaseModel):
    name: str
    enabledForPro: bool
    id: str
    isActive: bool
    localClass: Optional[str]

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class VenueProviderResponse(BaseModel):
    id: str
    idAtProviders: Optional[str]
    dateModifiedAtLastProvider: Optional[datetime]
    isActive: bool
    isFromAllocineProvider: bool
    lastProviderId: Optional[str]
    lastSyncDate: Optional[datetime]
    nOffers: int
    providerId: str
    venueId: str
    venueIdAtOfferProvider: str
    provider: ProviderResponse
    # TODO(asaunier): Check if this field is necessary
    fieldsUpdated: List[str]
    quantity: Optional[int]
    isDuo: Optional[bool]
    price: Optional[float]

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
