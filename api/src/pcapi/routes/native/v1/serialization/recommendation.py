from pydantic import Field, field_validator

from pcapi.routes.serialization import HttpBodyModel
from pcapi.serialization.utils import to_camel


class SimilarOffersRequestQuery(HttpBodyModel):
    longitude: float | None = None
    latitude: float | None = None
    categories: list[str] | None = None
    subcategories: list[str] | None = None
    search_group_names: list[str] | None = None

    @field_validator("categories", "subcategories", "search_group_names", mode="before")
    def validate_categories(cls, v: list[str] | str | None) -> list[str] | None:
        if isinstance(v, list):
            return v
        return v.split(",") if v else None

    class Config:
        extra = "forbid"


class RecommendationApiParams(HttpBodyModel):
    ab_test: str | None = None
    call_id: str | None = None
    filtered: bool | None = None
    geo_located: bool | None = None
    model_endpoint: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    reco_origin: str | None = None


class SimilarOffersResponse(HttpBodyModel):
    results: list[str] = Field(default_factory=list)
    params: RecommendationApiParams

    class Config:
        alias_generator = to_camel
        validate_by_name = True


class PlaylistRequestQuery(HttpBodyModel):
    model_endpoint: str | None = None
    longitude: float | None = None
    latitude: float | None = None

    class Config:
        extra = "forbid"


class PlaylistRequestBody(HttpBodyModel):
    start_date: str | None = None
    end_date: str | None = None
    is_event: bool | None = None
    categories: list[str] | None = None
    price_min: float | None = None
    price_max: float | None = None
    subcategories: list[str] | None = None
    is_duo: bool | None = None
    is_reco_shuffled: bool | None = None
    offer_type_list: list[dict[str, str]] | None = None

    class Config:
        extra = "forbid"


class PlaylistResponse(HttpBodyModel):
    playlist_recommended_offers: list[str]
    params: RecommendationApiParams

    class Config:
        alias_generator = to_camel
        validate_by_name = True
