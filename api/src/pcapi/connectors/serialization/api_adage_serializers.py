from pydantic import Field

from pcapi.routes.serialization import BaseModel


class EducationalInstitutionModel(BaseModel):
    uai: str
    name: str = Field(alias="nom")

    class Config:
        allow_population_by_field_name = True


class AdageVenue(BaseModel):
    siret: str
