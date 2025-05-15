import typing
from decimal import Decimal

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class LocalOfferersPlaylistOffer(BaseModel):
    id: int
    name: str
    distance: Decimal | None
    imgUrl: str | None
    publicName: str | None
    city: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class LocalOfferersPlaylist(BaseModel):
    venues: typing.Sequence[LocalOfferersPlaylistOffer]
