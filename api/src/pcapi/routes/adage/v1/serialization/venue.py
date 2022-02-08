from typing import Optional

from pcapi.routes.serialization import BaseModel


class VenueModel(BaseModel):
    name: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    postalCode: Optional[str]
    city: Optional[str]
    siret: str
    publicName: Optional[str]
    description: Optional[str]
    id: int

    class Config:
        orm_mode = True


class GetVenuesResponseModel(BaseModel):
    venues: list[VenueModel]
