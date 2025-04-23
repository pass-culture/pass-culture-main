import pydantic.v1 as pydantic_v1

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class SimilarOffersRequestQuery(BaseModel):
    longitude: float | None
    latitude: float | None
    categories: list[str] | None
    subcategories: list[str] | None
    search_group_names: list[str] | None

    @pydantic_v1.validator("categories", "subcategories", "search_group_names", pre=True)
    def validate_categories(cls, v: list[str] | str | None) -> list[str] | None:
        if isinstance(v, list):
            return v
        return v.split(",") if v else None

    class Config:
        extra = "forbid"


class RecommendationApiParams(BaseModel):
    ab_test: str | None = None
    call_id: str | None = None
    filtered: bool | None = None
    geo_located: bool | None = None
    model_endpoint: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    reco_origin: str | None = None


class SimilarOffersResponse(BaseModel):
    results: list[str] = pydantic_v1.Field(default_factory=list)
    params: RecommendationApiParams

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


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


class PlaylistResponse(BaseModel):
    playlist_recommended_offers: list[str]
    params: RecommendationApiParams

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
