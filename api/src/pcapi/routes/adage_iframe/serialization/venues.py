import logging

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel


logger = logging.getLogger(__name__)


class GetRelativeVenuesQueryModel(BaseModel):
    getRelative: bool = False


class VenueResponse(BaseModel):
    id: int
    publicName: str | None
    name: str
    departementCode: str | None
    relative: list[int]
    adageId: str | None

    @classmethod
    def build(
        cls: "type[VenueResponse]", venue: offerers_models.Venue, relative: list[int] | None = None
    ) -> "VenueResponse":
        if venue.offererAddress is not None:
            department_code = venue.offererAddress.address.departmentCode
        else:
            # TODO(OA): remove this when the virtual venues are migrated
            department_code = None

        return cls(
            id=venue.id,
            publicName=venue.publicName,
            name=venue.name,
            departementCode=department_code,
            relative=relative or [],
            adageId=venue.adageId,
        )
