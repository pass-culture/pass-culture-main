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
