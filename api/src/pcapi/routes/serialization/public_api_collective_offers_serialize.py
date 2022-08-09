from pcapi.routes.serialization import BaseModel


class CollectiveOffersVenueResponseModel(BaseModel):
    id: int
    name: str
    address: str | None
    postalCode: str | None
    city: str | None

    class Config:
        orm_mode = True


class CollectiveOffersListVenuesResponseModel(BaseModel):
    __root__: list[CollectiveOffersVenueResponseModel]


class CollectiveOffersCategoryResponseModel(BaseModel):
    id: str
    name: str


class CollectiveOffersListCategoriesResponseModel(BaseModel):
    __root__: list[CollectiveOffersCategoryResponseModel]


class CollectiveOffersDomainResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CollectiveOffersListDomainsResponseModel(BaseModel):
    __root__: list[CollectiveOffersDomainResponseModel]


class CollectiveOffersStudentLevelResponseModel(BaseModel):
    id: str
    name: str


class CollectiveOffersListStudentLevelsResponseModel(BaseModel):
    __root__: list[CollectiveOffersStudentLevelResponseModel]
