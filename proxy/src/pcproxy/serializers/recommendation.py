from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from pydantic.alias_generators import to_snake


class SimilarOffersRequestQuery(BaseModel):
    longitude: float | None = None
    latitude: float | None = None
    categories: list[str] | None = None
    subcategories: list[str] | None = None
    search_group_names: list[str] | None = None

    @field_validator("categories", "subcategories", "search_group_names", mode="before")
    def split_list(cls, v: str | None) -> list[str] | None:
        if v and isinstance(v, list):
            return v[0].split(",")
        return None

    class Config:
        extra = "forbid"


class RecommendationApiParams(BaseModel):
    abTest: str | None = None
    callId: str | None = None
    filtered: bool | None = None
    geoLocated: bool | None = None
    modelEndpoint: str | None = None
    modelName: str | None = None
    modelVersion: str | None = None
    recoOrigin: str | None = None

    class Config:
        alias_generator = to_snake
        populate_by_name = True
        extra = "forbid"


class SimilarOffersResponse(BaseModel):
    results: list[str] = Field(default_factory=list)
    params: RecommendationApiParams

    class Config:
        alias_generator = to_snake
        populate_by_name = True
        extra = "forbid"


class PlaylistRequestQuery(BaseModel):
    modelEndpoint: str | None = None
    longitude: float | None = None
    latitude: float | None = None

    class Config:
        extra = "forbid"


class PlaylistRequestBody(BaseModel):
    startDate: str | None = None
    endDate: str | None = None
    isEvent: bool | None = None
    categories: list[str] | None = None
    priceMin: float | None = None
    priceMax: float | None = None
    subcategories: list[str] | None = None
    isDuo: bool | None = None
    isRecoShuffled: bool | None = None
    offerTypeList: list[dict[str, str]] | None = None

    class Config:
        extra = "forbid"


class PlaylistResponse(BaseModel):
    playlistRecommendedOffers: list[str]
    params: RecommendationApiParams

    class Config:
        alias_generator = to_snake
        populate_by_name = True
        extra = "forbid"
