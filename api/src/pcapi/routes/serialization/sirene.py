from pcapi.routes import serialization
from pcapi.serialization.utils import to_camel


class Address(serialization.BaseModel):
    street: str
    postal_code: str
    city: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class SirenInfo(serialization.BaseModel):
    siren: str
    name: str
    address: Address


class SiretInfo(serialization.BaseModel):
    siret: str
    name: str
    address: Address
