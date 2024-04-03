from pcapi.routes.serialization import BaseModel


class SimilarOffersRequestQuery(BaseModel):
    longitude: float | None
    latitude: float | None
    categories: list[str] | None
    subcategories: list[str] | None

    class Config:
        extra = "forbid"


class PlaylistRequestQuery(BaseModel):
    modelEndpoint: str | None
    longitude: float | None
    latitude: float | None

    class Config:
        extra = "forbid"


class PlaylistRequestBody(BaseModel):
    startDate: str | None
    endDate: str | None
    isEvent: bool | None
    categories: list[str] | None
    priceMin: float | None
    priceMax: float | None
    subcategories: list[str] | None
    isDuo: bool | None
    isRecoShuffled: bool | None
    offerTypeList: list[dict[str, str]] | None

    class Config:
        extra = "forbid"
