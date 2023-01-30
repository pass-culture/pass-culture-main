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
