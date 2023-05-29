import enum

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


class AdageHeaderLink(enum.Enum):
    SEARCH = "search"
    MY_INSITUTION_OFFERS = "my_institution_offers"
    ADAGE_LINK = "adage_link"


class AdageHeaderLogBody(BaseModel):
    header_link_name: AdageHeaderLink


class CollectiveRequestBody(BaseModel):
    collectiveOfferTemplateId: int
    phoneNumber: str | None
    requestedDate: str | None
    totalStudents: int | None
    totalTeachers: int | None
    comment: str
