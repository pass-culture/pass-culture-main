from pcapi.routes.serialization import BaseModel


class CatalogViewBody(BaseModel):
    source: str


class StockIdBody(BaseModel):
    stockId: int


class OfferIdBody(BaseModel):
    offerId: int


class SearchBody(BaseModel):
    filters: list[str]
    resultsCount: int
