"""
Please take care not to publish any private information here.
Those serializers are exposed to general view and should not
include GDPR protected data.
"""

from pcapi.routes.serialization import HttpBodyModel


class VenueOfOffererFromSiretResponseModel(HttpBodyModel):
    id: int
    name: str
    publicName: str
    siret: str | None = None
    isPermanent: bool


class GetVenuesOfOffererFromSiretResponseModel(HttpBodyModel):
    offererName: str | None = None
    offererSiren: str | None = None
    venues: list[VenueOfOffererFromSiretResponseModel]


class PostOffererResponseModel(HttpBodyModel):
    name: str
    id: int
    siren: str
