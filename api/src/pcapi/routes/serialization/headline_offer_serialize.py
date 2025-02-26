from pcapi.core.offers.models import OfferImage
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class HeadLineOfferResponseModel(BaseModel):
    id: int
    name: str
    image: OfferImage | None
    venue_id: int

    class Config:
        orm_mode = True
        alias_generator = to_camel
        extra = "forbid"


class HeadlineOfferCreationBodyModel(BaseModel):
    offer_id: int

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class HeadlineOfferDeleteBodyModel(BaseModel):
    offerer_id: int

    class Config:
        alias_generator = to_camel
        extra = "forbid"
