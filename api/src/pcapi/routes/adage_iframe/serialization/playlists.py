from decimal import Decimal
import typing

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pydantic import ConfigDict


class LocalOfferersPlaylistOffer(BaseModel):
    id: int
    name: str
    distance: Decimal | None
    imgUrl: str | None
    publicName: str | None
    city: str | None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class LocalOfferersPlaylist(BaseModel):
    venues: typing.Sequence[LocalOfferersPlaylistOffer]
