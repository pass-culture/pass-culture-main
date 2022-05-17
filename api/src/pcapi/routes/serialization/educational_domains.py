from pcapi.routes.serialization import BaseModel


class EducationalDomainResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class EducationalDomainsResponseModel(BaseModel):
    __root__: list[EducationalDomainResponseModel]

    class Config:
        orm_mode = True
