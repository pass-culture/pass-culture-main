from pcapi.core.offerers.schemas import AddressBodyModel
from pcapi.routes import serialization


class StructureDataBodyModel(serialization.BaseModel):
    siret: str
    siren: str | None
    name: str | None
    apeCode: str | None
    address: AddressBodyModel | None
    isDiffusible: bool
