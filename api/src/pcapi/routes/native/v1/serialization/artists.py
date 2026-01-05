from pcapi.routes.serialization import ConfiguredBaseModel


class ArtistResponse(ConfiguredBaseModel):
    id: str
    name: str
    description: str | None
    description_credit: str | None
    description_source: str | None
    image: str | None
