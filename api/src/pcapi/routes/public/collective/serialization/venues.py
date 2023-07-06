import pcapi.routes.public.serialization.venues as venues_serialization
from pcapi.routes.serialization import BaseModel


class CollectiveOffersListVenuesResponseModel(BaseModel):
    __root__: list[venues_serialization.VenueResponse]
