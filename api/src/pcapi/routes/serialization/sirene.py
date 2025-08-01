from pcapi.core.offerers.schemas import AddressBodyModel
from pcapi.routes import serialization
from pcapi.serialization.utils import to_camel


class Address(serialization.BaseModel):
    street: str
    postal_code: str
    city: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class SiretInfo(serialization.BaseModel):
    siret: str
    name: str
    active: bool
    address: Address
    ape_code: str
    legal_category_code: str


class StructureDataBodyModel(serialization.BaseModel):
    siret: str
    siren: str | None
    name: str | None
    apeCode: str | None
    address: AddressBodyModel | None
    isDiffusible: bool
