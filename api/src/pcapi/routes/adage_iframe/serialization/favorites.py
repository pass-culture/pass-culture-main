import logging

from pcapi.routes.serialization import BaseModel


logger = logging.getLogger(__name__)


class FavoritesOfferResponseModel(BaseModel):
    educationalRedactorId: int
    collectiveOfferId: int

    class Config:
        orm_mode = True


class FavoritesTemplateResponseModel(BaseModel):
    educationalRedactorId: int
    collectiveOfferTemplateId: int

    class Config:
        orm_mode = True


class CollectiveOfferFavoritesBodyModel(BaseModel):
    offerId: int
