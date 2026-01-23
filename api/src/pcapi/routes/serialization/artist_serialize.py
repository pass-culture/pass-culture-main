from pydantic import RootModel
from pydantic.v1 import Field

from pcapi.core.artist import models as artist_models
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class ArtistResponseModel(HttpBodyModel):
    id: str
    name: str
    thumbUrl: str | None


class ArtistsResponseModel(RootModel):
    root: list[ArtistResponseModel]


class ArtistQueryModel(HttpQueryParamsModel):
    search: str


class ArtistOfferLinkResponseModel(ConfiguredBaseModel):
    artist_id: str | None = Field(...)
    artist_type: artist_models.ArtistType
    artist_name: str


class ArtistOfferLinkBodyModel(ConfiguredBaseModel):
    artist_id: str | None
    artist_type: artist_models.ArtistType
    custom_name: str | None
