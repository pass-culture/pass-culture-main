import enum

from pcapi.routes.serialization import BaseModel


class AdageBaseModel(BaseModel):
    iframeFrom: str
    queryId: str | None


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
    MY_FAVORITES = "my_favorites"


class AdageHeaderLogBody(AdageBaseModel):
    header_link_name: AdageHeaderLink


class CollectiveRequestBody(AdageBaseModel):
    collectiveOfferTemplateId: int
    phoneNumber: str | None
    requestedDate: str | None
    totalStudents: int | None
    totalTeachers: int | None
    comment: str


class TrackingFilterBody(AdageBaseModel):
    resultNumber: int
    filterValues: dict


class SuggestionType(enum.Enum):
    VENUE = "venue"
    OFFER_BY_CATEGORY = "offer category"
    OFFER = "offer"


class TrackingAutocompleteSuggestionBody(AdageBaseModel):
    suggestionType: SuggestionType
    suggestionValue: str
