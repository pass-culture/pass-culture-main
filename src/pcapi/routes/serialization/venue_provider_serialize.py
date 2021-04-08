from datetime import datetime
from typing import List
from typing import Optional

from pydantic.main import BaseModel

from pcapi.serialization.utils import humanize_field


class PostVenueProviderBody(BaseModel):
    venueId: str
    providerId: str
    venueIdAtOfferProvider: Optional[str]
    price: Optional[str]
    isDuo: Optional[bool]
    quantity: Optional[int]


# TODO(asaunier): We usually exposed every field from ORM but some mightbe unecessary
class ProviderResponse(BaseModel):
    name: str
    enabledForPro: bool
    id: str
    requireProviderIdentifier: str
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
    syncWorkerId: Optional[str]
    venueId: str
    venueIdAtOfferProvider: str
    provider: ProviderResponse
    # TODO(asaunier): Check if this field is necessary
    fieldsUpdated: List[str]

    _humanize_id = humanize_field("id")
    _humanize_venue_id = humanize_field("venueId")
    _humanize_provider_id = humanize_field("providerId")

    class Config:
        orm_mode = True
