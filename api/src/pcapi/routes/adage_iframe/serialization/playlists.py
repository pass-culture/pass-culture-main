import typing

from pcapi.routes.serialization import BaseModel


class LocalOfferersPlaylistOffer(BaseModel):
    id: int
    name: str
    distance: float
    img_url: str | None
    public_name: str | None
    city: str | None


class LocalOfferersPlaylist(BaseModel):
    venues: typing.Sequence[LocalOfferersPlaylistOffer]
