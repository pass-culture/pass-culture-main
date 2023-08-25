import logging

from pcapi.routes.serialization import BaseModel


logger = logging.getLogger(__name__)


class FavoriesResponseModel(BaseModel):
    educationalRedactor: str
    offerId: int

    class Config:
        orm_mode = True


class CollectiveOfferFavoriesBodyModel(BaseModel):
    offerId: int
