import logging
import typing

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import HttpBodyModel


logger = logging.getLogger(__name__)


class GetRelativeVenuesQueryModel(HttpBodyModel):
    getRelative: bool = False


class VenueResponse(HttpBodyModel):
    id: int
    publicName: str
    name: str
    departementCode: str
    relative: list[int]
    adageId: str | None

    @classmethod
    def build(cls, venue: offerers_models.Venue, relative: list[int] | None = None) -> typing.Self:
        return cls(
            id=venue.id,
            publicName=venue.publicName,
            name=venue.name,
            departementCode=venue.offererAddress.address.departmentCode,
            relative=relative or [],
            adageId=venue.adageId,
        )
