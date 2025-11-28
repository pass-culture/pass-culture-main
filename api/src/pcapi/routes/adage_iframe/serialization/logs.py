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


class OfferListSwitch(AdageBaseModel):
    source: str
    isMobile: bool | None


class CatalogViewBody(AdageBaseModel):
    source: str


class StockIdBody(AdageBaseModel, VueTypeMixin):
    stockId: int


class OfferIdBody(AdageBaseModel, VueTypeMixin):
    offerId: int


class OfferBody(AdageBaseModel, VueTypeMixin):
    offerId: int
    playlistId: int | None


class OfferFavoriteBody(AdageBaseModel, VueTypeMixin):
    isFavorite: bool
    offerId: int
    playlistId: int | None


class PlaylistBody(AdageBaseModel):
    playlistType: AdagePlaylistType
    playlistId: int
    offerId: int | None
    venueId: int | None
    domainId: int | None
    index: int | None
    numberOfTiles: int | None


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


class PaginationType(enum.Enum):
    NEXT = "next"
    PREVIOUS = "previous"


class TrackingAutocompleteSuggestionBody(AdageBaseModel):
    suggestionType: SuggestionType
    suggestionValue: str


class TrackingShowMoreBody(AdageBaseModel):
    source: str
    type: PaginationType


class TrackingCTAShareBody(AdageBaseModel, VueTypeMixin):
    source: str
    offerId: int


class HighlightBannerBody(AdageBaseModel):
    banner: str


class ConsultOfferBody(AdageBaseModel):
    offerId: int
    playlistId: int | None
    source: str | None
