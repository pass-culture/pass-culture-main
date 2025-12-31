from pydantic import RootModel

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


class ArtistOfferResponseModel(ConfiguredBaseModel):
    artist_id: str | None
    artist_type: artist_models.ArtistType
    custom_name: str | None
