from pydantic import RootModel
from pydantic.v1 import Field

from pcapi.core.artist import models as artist_models
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class ArtistResponseModel(HttpBodyModel):
    id: str
    name: str
    description: str | None
    thumbUrl: str | None


class ArtistsResponseModel(RootModel):
    root: list[ArtistResponseModel]


class ArtistQueryModel(HttpQueryParamsModel):
    search: str


class ArtistOfferLinkBodyModel(ConfiguredBaseModel):
    artist_id: str | None = Field(default=None)
    artist_type: artist_models.ArtistType
    artist_name: str


class ArtistOfferLinkBodyModelV2(HttpBodyModel):
    artist_id: str | None = None
    artist_type: artist_models.ArtistType
    artist_name: str


class ArtistOfferLinkResponseModelV2(ArtistOfferLinkBodyModelV2): ...
