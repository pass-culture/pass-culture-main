from pcapi.routes.serialization import ConfiguredBaseModel


class ArtistResponse(ConfiguredBaseModel):
    id: str
    name: str
    description: str | None
    image: str | None
