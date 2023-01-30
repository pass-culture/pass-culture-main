from pcapi.routes.serialization import BaseModel


class CollectiveOffersDomainResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CollectiveOffersListDomainsResponseModel(BaseModel):
    __root__: list[CollectiveOffersDomainResponseModel]
