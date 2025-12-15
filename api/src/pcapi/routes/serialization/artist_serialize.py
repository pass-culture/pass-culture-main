from pydantic import RootModel

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
