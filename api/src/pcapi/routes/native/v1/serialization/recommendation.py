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
    start_date: str | None
    end_date: str | None
    is_event: bool | None
    categories: list[str] | None
    price_min: float | None
    price_max: float | None
    subcategories: list[str] | None
    is_duo: bool | None
    is_reco_shuffled: bool | None
    offer_type_list: list[dict[str, str]] | None

    class Config:
        extra = "forbid"
