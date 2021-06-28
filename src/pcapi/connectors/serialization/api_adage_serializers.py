from pydantic import BaseModel
from pydantic import Field


class EducationalInstitutionModel(BaseModel):
    uai: str
    name: str = Field(alias="nom")

    class Config:
        allow_population_by_field_name = True


class InstitutionalProjectRedactorResponse(BaseModel):
    civility: str = Field(alias="civilite")
    first_name: str = Field(alias="nom")
    last_name: str = Field(alias="prenom")
    email: str = Field(alias="mail")
    educational_institutions: list[EducationalInstitutionModel] = Field(alias="etablissements")

    class Config:
        allow_population_by_field_name = True
        extra = "forbid"
