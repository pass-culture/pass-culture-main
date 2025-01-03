from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


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
