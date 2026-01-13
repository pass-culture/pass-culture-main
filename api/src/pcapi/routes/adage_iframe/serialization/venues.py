import logging

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel


logger = logging.getLogger(__name__)


class GetRelativeVenuesQueryModel(BaseModel):
    getRelative: bool = False


class VenueResponse(BaseModel):
    id: int
    publicName: str
    name: str
    departementCode: str | None
    relative: list[int]
    adageId: str | None

    @classmethod
    def build(
        cls: "type[VenueResponse]", venue: offerers_models.Venue, relative: list[int] | None = None
    ) -> "VenueResponse":
        return cls(
            id=venue.id,
            publicName=venue.publicName,
            name=venue.name,
            departementCode=venue.offererAddress.address.departmentCode,
            relative=relative or [],
            adageId=venue.adageId,
        )
