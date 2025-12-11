from pcapi.core.offerers.schemas import LocationModel
from pcapi.routes import serialization


class StructureDataBodyModel(serialization.BaseModel):
    siret: str
    siren: str | None
    name: str | None
    apeCode: str | None
    location: LocationModel | None
    isDiffusible: bool
