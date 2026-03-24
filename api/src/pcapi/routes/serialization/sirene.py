import pcapi.core.offerers.schemas as offerers_schemas
from pcapi.routes.serialization import HttpBodyModel


class LocationModelV2(HttpBodyModel, offerers_schemas.CoreLocationModelV2):
    pass


class StructureDataBodyModel(HttpBodyModel):
    siret: str
    siren: str | None
    name: str | None
    apeCode: str | None
    location: LocationModelV2 | None
    isDiffusible: bool
