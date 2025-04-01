import logging

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.utils import regions


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
        offerer_address = venue.offererAddress

        departement_code: str | None
        if offerer_address is None:
            # we only use this model on venues related to a collective offer template, those should have an offererAddress
            logger.error("Found venue with id %s without offererAddress", venue.id)
            departement_code = None
        else:
            departement_code = offerer_address.address.departmentCode
            if departement_code is None:
                # Address.departmentCode is nullable, if None fallback to postalCode
                departement_code = regions.get_department_code_from_city_code(offerer_address.address.postalCode)

        return cls(
            id=venue.id,
            publicName=venue.publicName,
            name=venue.name,
            departementCode=departement_code,
            relative=relative or [],
            adageId=venue.adageId,
        )
