from pcapi.routes.serialization import HttpBodyModel


class ArtistResponse(HttpBodyModel):
    id: str
    name: str
    description: str | None = None
    description_credit: str | None = None
    description_source: str | None = None
    image: str | None = None
