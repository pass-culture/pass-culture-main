import enum

from pcapi.routes.serialization import BaseModel


class AdageBaseModel(BaseModel):
    iframeFrom: str
    queryId: str | None
    isFromNoResult: bool | None


class VueTypeMixin(BaseModel):
    vueType: str | None


class AdagePlaylistType(enum.Enum):
    OFFER = "offer"
    VENUE = "venue"
    DOMAIN = "domain"


class CatalogViewBody(AdageBaseModel):
    source: str


class StockIdBody(AdageBaseModel, VueTypeMixin):
    stockId: int


class OfferIdBody(AdageBaseModel, VueTypeMixin):
    offerId: int


class OfferFavoriteBody(AdageBaseModel, VueTypeMixin):
    offerId: int
    isFavorite: bool


class PlaylistBody(AdageBaseModel):
    playlistType: AdagePlaylistType
    playlistId: int
    elementId: int | None
    index: int | None


class SearchBody(AdageBaseModel):
    filters: list[str]
    resultsCount: int


class AdageHeaderLink(enum.Enum):
    SEARCH = "search"
    MY_INSITUTION_OFFERS = "my_institution_offers"
    ADAGE_LINK = "adage_link"
    MY_FAVORITES = "my_favorites"
    DISCOVERY = "discovery"


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


class TrackingShowMoreBody(AdageBaseModel):
    source: str


class TrackingCTAShareBody(AdageBaseModel, VueTypeMixin):
    source: str
    offerId: int
