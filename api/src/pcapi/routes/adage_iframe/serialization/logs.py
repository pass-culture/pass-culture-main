import enum

from pcapi.routes.serialization import BaseModel


class AdageBaseModel(BaseModel):
    AdageHeaderFrom: str


class CatalogViewBody(AdageBaseModel):
    source: str


class StockIdBody(AdageBaseModel):
    stockId: int


class OfferIdBody(AdageBaseModel):
    offerId: int


class SearchBody(AdageBaseModel):
    filters: list[str]
    resultsCount: int


class AdageHeaderLink(enum.Enum):
    SEARCH = "search"
    MY_INSITUTION_OFFERS = "my_institution_offers"
    ADAGE_LINK = "adage_link"


class AdageHeaderLogBody(AdageBaseModel):
    header_link_name: AdageHeaderLink


class CollectiveRequestBody(AdageBaseModel):
    collectiveOfferTemplateId: int
    phoneNumber: str | None
    requestedDate: str | None
    totalStudents: int | None
    totalTeachers: int | None
    comment: str
