"""
Please take care not to publish any private information here.
Those serializers are exposed to general view and should not
include GDPR protected data.
"""

from pcapi.routes.serialization import BaseModel


class VenueOfOffererFromSiretResponseModel(BaseModel):
    id: int
    name: str
    publicName: str
    siret: str | None
    isPermanent: bool

    class Config:
        orm_mode = True


class GetVenuesOfOffererFromSiretResponseModel(BaseModel):
    offererName: str | None
    offererSiren: str | None
    venues: list[VenueOfOffererFromSiretResponseModel]


class PostOffererResponseModel(BaseModel):
    name: str
    id: int
    siren: str

    class Config:
        orm_mode = True
