from decimal import Decimal
import typing

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class LocalOfferersPlaylistOffer(BaseModel):
    id: int
    name: str
    distance: Decimal | None
    img_url: str | None
    public_name: str | None
    city: str | None

    class Config:
        alias_generator = to_camel


class LocalOfferersPlaylist(BaseModel):
    venues: typing.Sequence[LocalOfferersPlaylistOffer]
