from pcapi.routes.serialization import BaseModel


class StockIdBody(BaseModel):
    stockId: int


class OfferIdBody(BaseModel):
    offerId: int


class SearchBody(BaseModel):
    filters: list[str]
    resultsCount: int
