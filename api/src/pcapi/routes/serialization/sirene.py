from pcapi.routes import serialization
from pcapi.serialization.utils import to_camel
from pydantic import ConfigDict


class Address(serialization.BaseModel):
    street: str
    postal_code: str
    city: str
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SirenInfo(serialization.BaseModel):
    siren: str
    name: str
    address: Address
    ape_code: str


class SiretInfo(serialization.BaseModel):
    siret: str
    name: str
    active: bool
    address: Address
    ape_code: str
    legal_category_code: str
