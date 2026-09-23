from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class RecommendationApiParams(BaseModel):
    ab_test: str | None = None
    call_id: str | None = None
    unique_call_id: str | None = None
    filtered: bool | None = None
    geo_located: bool | None = None
    model_endpoint: str | None = None
    model_name: str | None = None
    model_origin: str | None = None
    model_version: str | None = None
    reco_origin: str | None = None


class SimilarOffersRequestQuery(BaseModel):
    longitude: float | None = None
    latitude: float | None = None
    categories: list[str] | None = None
    subcategories: list[str] | None = None
    search_group_names: list[str] | None = None
    retrieval_model: Literal["coreservation", "graph"] = "coreservation"
    user_id: str | None = None

    @field_validator("categories", "subcategories", "search_group_names", mode="before")
    def validate_categories(cls, v: list[str] | str | None) -> list[str] | None:
        if isinstance(v, list):
            return v
        return v.split(",") if v else None


class SimilarOffersResponse(BaseModel):
    results: list[str] = Field(default_factory=list)
    params: RecommendationApiParams = RecommendationApiParams()
    from_cache: bool | None = None


class PlaylistRequestQuery(BaseModel):
    model_endpoint: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    user_id: str | None = None


class PlaylistRequestBody(BaseModel):
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


class PlaylistResponse(BaseModel):
    playlist_recommended_offers: list[str]
    params: RecommendationApiParams
    from_cache: bool | None = None


class ArtistResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    description_credit: str | None = None
    description_source: str | None = None
    image: str | None = None


class MatchedArtist(BaseModel):
    artist_id_match: str
    rank: int


class SimilarArtistsParams(BaseModel):
    artist_id: str
    call_id: str


class SimilarArtistsResponse(BaseModel):
    similar_artists: list[MatchedArtist]
    params: SimilarArtistsParams
