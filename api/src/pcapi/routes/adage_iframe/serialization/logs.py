from pcapi.routes.serialization import BaseModel


class StockIdBody(BaseModel):
    stockId: int


class OfferIdBody(BaseModel):
    offerId: int
