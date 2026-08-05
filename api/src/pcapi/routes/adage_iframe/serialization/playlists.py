from pcapi.routes.serialization import HttpBodyModel


class LocalOfferersPlaylistOffer(HttpBodyModel):
    id: int
    name: str
    distance: float | None
    imgUrl: str | None
    publicName: str
    city: str | None


class LocalOfferersPlaylist(HttpBodyModel):
    venues: list[LocalOfferersPlaylistOffer]
