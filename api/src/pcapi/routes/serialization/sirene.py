from pcapi.core.offerers.schemas import LocationModelV2
from pcapi.routes.serialization import HttpBodyModel


class StructureDataBodyModel(HttpBodyModel):
    siret: str
    siren: str | None = None
    name: str | None = None
    ape_code: str | None = None
    location: LocationModelV2 | None = None
    is_diffusible: bool
