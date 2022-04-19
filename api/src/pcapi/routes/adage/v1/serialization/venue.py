from typing import Optional

from pcapi.routes.serialization import BaseModel


class BaseVenueModel(BaseModel):
    name: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    city: Optional[str]
    publicName: Optional[str]
    description: Optional[str]
    id: int

    class Config:
        orm_mode = True


class VenueModelWithOptionalSiret(BaseVenueModel):
    siret: Optional[str]


class VenueModelWithRequiredSiret(BaseVenueModel):
    siret: str


class GetVenuesBySiretResponseModel(BaseModel):
    venues: list[VenueModelWithRequiredSiret]


class GetVenuesByNameResponseModel(BaseModel):
    venues: list[VenueModelWithOptionalSiret]
