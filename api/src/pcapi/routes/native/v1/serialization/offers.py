import logging
import textwrap
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from typing import Any
from typing import Callable
from typing import TypeVar
from typing import cast

import pydantic as pydantic_v2
from pydantic.v1.class_validators import validator
from pydantic.v1.fields import Field
from pydantic.v1.utils import GetterDict

import pcapi.core.opening_hours.api as opening_hours_api
import pcapi.core.opening_hours.schemas as opening_hours_schemas
from pcapi.core.artist.models import ArtistType
from pcapi.core.bookings.api import compute_booking_cancellation_limit_date
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres.movie import get_movie_label
from pcapi.core.categories.genres.music import MUSIC_SUB_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.music import MUSIC_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.show import SHOW_SUB_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.show import SHOW_TYPES_LABEL_BY_CODE
from pcapi.core.chronicles.api import get_offer_published_chronicles
from pcapi.core.geography.models import Address
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models
from pcapi.core.offers import offer_metadata
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.offers.models import Reason
from pcapi.core.offers.models import ReasonMeta
from pcapi.core.providers import constants as provider_constants
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.core.users.models import ExpenseDomain
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.routes.shared.price import convert_to_cent
from pcapi.serialization.utils import to_camel
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class OfferOffererResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OfferStockActivationCodeResponse(BaseModel):
    expirationDate: datetime | None


class OfferStockResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        stock = self._obj
        if key == "cancellation_limit_datetime":
            return compute_booking_cancellation_limit_date(stock.beginningDatetime, date_utils.get_naive_utc_now())

        if key == "activationCode":
            if not stock.canHaveActivationCodes:
                return None
            # here we have N+1 requests (for each stock we query an activation code)
            # but it should be more efficient than loading all activationCodes of all stocks
            activation_code = offers_repository.get_available_activation_code(stock)
            if not activation_code:
                return None
            return {"expirationDate": activation_code.expirationDate}

        if key == "priceCategoryLabel":
            if price_category := stock.priceCategory:
                return price_category.priceCategoryLabel.label
            return None

        return super().get(key, default)


class OfferStockResponse(ConfiguredBaseModel):
    id: int
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    cancellation_limit_datetime: datetime | None
    features: list[str]
    isBookable: bool
    is_forbidden_to_underage: bool
    isSoldOut: bool
    isExpired: bool
    price: int
    activationCode: OfferStockActivationCodeResponse | None
    priceCategoryLabel: str | None
    remainingQuantity: int | None

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_remainingQuantity = validator(
        "remainingQuantity",
        pre=True,
        allow_reuse=True,
    )(lambda quantity: quantity if quantity != "unlimited" else None)

    class Config:
        getter_dict = OfferStockResponseGetterDict


class OfferVenueResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        venue = self._obj
        if key == "coordinates":
            return {
                "latitude": venue.offererAddress.address.latitude,
                "longitude": venue.offererAddress.address.longitude,
            }
        if key == "address":
            return venue.offererAddress.address.street
        if key == "city":
            return venue.offererAddress.address.city
        if key == "postalCode":
            return venue.offererAddress.address.postalCode
        if key == "timezone":
            return venue.offererAddress.address.timezone
        if key == "name":
            return venue.common_name

        return super().get(key, default)


class OfferVenueResponse(BaseModel):
    id: int
    address: str | None
    city: str | None
    managingOfferer: OfferOffererResponse = Field(..., alias="offerer")
    name: str
    postalCode: str | None
    publicName: str
    coordinates: Coordinates
    isPermanent: bool
    isOpenToPublic: bool
    timezone: str
    bannerUrl: str | None

    class Config:
        orm_mode = True
        getter_dict = OfferVenueResponseGetterDict
        allow_population_by_field_name = True


def get_id_converter(labels_by_id: dict, field_name: str) -> Callable[[str | None], str | None]:
    def convert_id_into_label(value_id: str | None) -> str | None:
        try:
            return labels_by_id[int(value_id)] if value_id else None
        except ValueError:  # on the second time this function is called twice, the field is already converted
            return None
        except KeyError:
            logger.exception("Invalid '%s' '%s' found on an offer", field_name, value_id)
            return None

    return convert_id_into_label


class GtlLabels(BaseModel):
    label: str
    level01Label: str | None
    level02Label: str | None
    level03Label: str | None
    level04Label: str | None


class OfferExtraDataResponse(BaseModel):
    allocineId: int | None
    author: str | None
    durationMinutes: int | None
    ean: str | None
    musicSubType: str | None
    musicType: str | None
    performer: str | None
    showSubType: str | None
    showType: str | None
    stageDirector: str | None
    speaker: str | None
    visa: str | None
    releaseDate: date | None
    certificate: str | None
    bookFormat: str | None
    cast: list[str] | None
    editeur: str | None
    gtlLabels: GtlLabels | None
    genres: list[str] | None

    @validator("genres", pre=True, allow_reuse=True)
    def convert_movie_types(cls, genres: list[str] | None) -> list[str] | None:
        if not genres:
            return None
        movie_types = []
        for genre in genres:
            movie_type = get_movie_label(genre)
            if movie_type:
                movie_types.append(movie_type)
        return movie_types

    _convert_music_sub_type = validator("musicSubType", pre=True, allow_reuse=True)(
        get_id_converter(MUSIC_SUB_TYPES_LABEL_BY_CODE, "musicSubType")
    )
    _convert_music_type = validator("musicType", pre=True, allow_reuse=True)(
        get_id_converter(MUSIC_TYPES_LABEL_BY_CODE, "musicType")
    )
    _convert_show_sub_type = validator("showSubType", pre=True, allow_reuse=True)(
        get_id_converter(SHOW_SUB_TYPES_LABEL_BY_CODE, "showSubType")
    )
    _convert_show_type = validator("showType", pre=True, allow_reuse=True)(
        get_id_converter(SHOW_TYPES_LABEL_BY_CODE, "showType")
    )


class OfferAccessibilityResponse(BaseModel):
    audioDisability: bool | None
    mentalDisability: bool | None
    motorDisability: bool | None
    visualDisability: bool | None


class OfferImageResponse(BaseModel):
    url: str
    credit: str | None

    class Config:
        orm_mode = True


def get_gtl_labels(gtl_id: str) -> GtlLabels | None:
    if gtl_id not in GTLS:
        return None
    gtl_infos = GTLS[gtl_id]
    label = gtl_infos.get("label")
    if label:
        return GtlLabels(
            label=label,
            level01Label=gtl_infos.get("level_01_label"),
            level02Label=gtl_infos.get("level_02_label"),
            level03Label=gtl_infos.get("level_03_label"),
            level04Label=gtl_infos.get("level_04_label"),
        )
    logger.error("GTL label not found for id %s", gtl_id)
    return None


BaseOfferResponseType = TypeVar("BaseOfferResponseType", bound="BaseOfferResponse")


class ReactionCount(BaseModel):
    likes: int


MAX_PREVIEW_CHRONICLES = 5


class BaseOfferResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        offer: models.Offer = self._obj
        product: models.Product | None = offer.product

        if key == "reactions_count":
            if product:
                likes = product.likesCount or 0
            else:
                likes = offer.likesCount or 0
            return ReactionCount(likes=likes)

        if key == "accessibility":
            return {
                "audioDisability": offer.audioDisabilityCompliant,
                "mentalDisability": offer.mentalDisabilityCompliant,
                "motorDisability": offer.motorDisabilityCompliant,
                "visualDisability": offer.visualDisabilityCompliant,
            }

        if key == "artists":
            if not product:
                return []

            return [
                OfferArtist(
                    id=artist_link.artist.id,
                    image=artist_link.artist.image,
                    name=artist_link.artist.name,
                    role=artist_link.artist_type if artist_link.artist_type else None,
                )
                for artist_link in product.artistLinks
                if not artist_link.artist.is_blacklisted
            ]
        if key == "expense_domains":
            return get_expense_domains(offer)

        if key == "isExpired":
            return offer.hasBookingLimitDatetimesPassed

        if key == "isHeadline":
            return offer.is_headline_offer

        if key == "metadata":
            return offer_metadata.get_metadata_from_offer(offer)

        if key == "isExternalBookingsDisabled":
            if offer.lastProvider and offer.lastProvider.localClass in provider_constants.PROVIDER_LOCAL_CLASS_TO_FF:
                return provider_constants.PROVIDER_LOCAL_CLASS_TO_FF[offer.lastProvider.localClass].is_active()

            return False

        if key == "last30DaysBookings":
            return offer.product.last_30_days_booking if offer.product else None

        if key == "stocks":
            return [OfferStockResponse.from_orm(stock) for stock in offer.activeStocks]

        if key == "extraData":
            raw_extra_data = (product.extraData if product else offer.extraData) or {}
            extra_data = OfferExtraDataResponse.parse_obj(raw_extra_data)

            extra_data.durationMinutes = offer.durationMinutes

            gtl_id = raw_extra_data.get("gtl_id")
            if gtl_id is not None:
                extra_data.gtlLabels = get_gtl_labels(gtl_id)
            if self._obj.ean:
                extra_data.ean = self._obj.ean

            return extra_data

        if key == "address":
            offerer_address: offerers_models.OffererAddress | None
            if self._obj.offererAddress:
                offerer_address = self._obj.offererAddress
            else:
                offerer_address = self._obj.venue.offererAddress

            if not offerer_address:
                return None

            address: Address = offerer_address.address
            label = offerer_address.label

            return OfferAddressResponse(
                street=address.street,
                postalCode=address.postalCode,
                city=address.city,
                label=label,
                coordinates=Coordinates(latitude=address.latitude, longitude=address.longitude),
                timezone=address.timezone,
            )

        if key == "chronicles":
            published_chronicles = get_offer_published_chronicles(offer)
            return published_chronicles[:MAX_PREVIEW_CHRONICLES]

        if key == "chroniclesCount":
            return product.chroniclesCount if product and product.chroniclesCount else offer.chroniclesCount

        if key == "publicationDate":
            return (
                offer.bookingAllowedDatetime
            )  # FIXME (bpeyrou): to be removed when min app version stop using publicationDate

        if key == "video":
            if offer.metaData and offer.metaData.videoUrl and not offer.metaData.videoExternalId:
                logger.error(
                    "This offer has a video URL but no videoExternalId in its metaData, and this should not happen",
                    extra={"offer_id": offer.id},
                )  # we want to see this in sentry if ever it happens

            if not (offer.metaData and offer.metaData.videoExternalId):
                return None

            return OfferVideo(
                id=offer.metaData.videoExternalId,
                title=offer.metaData.videoTitle,
                thumbUrl=offer.metaData.videoThumbnailUrl,
                durationSeconds=offer.metaData.videoDuration,
            )

        if key == "openingHours":
            opening_hours = offer.openingHours
            if opening_hours and isinstance(opening_hours, list):
                return opening_hours_api.format_opening_hours(opening_hours)
            return cast(opening_hours_schemas.WeekdayOpeningHoursTimespans | None, opening_hours)

        return super().get(key, default)


class OfferAddressResponse(ConfiguredBaseModel):
    street: str | None
    postalCode: str
    city: str
    label: str | None
    coordinates: Coordinates
    timezone: str

    class Config:
        orm_mode = True


class ChronicleGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        chronicle = self._obj
        if key == "author":
            if chronicle.isIdentityDiffusible:
                return ChronicleAuthor(
                    first_name=chronicle.firstName,
                    age=chronicle.age,
                    city=chronicle.city,
                )
            return None
        if key == "content_preview":
            return textwrap.shorten(chronicle.content, width=255, placeholder="…")

        return super().get(key, default)


class ChronicleAuthor(ConfiguredBaseModel):
    first_name: str | None
    age: int | None
    city: str | None


class BaseChronicle(ConfiguredBaseModel):
    id: int
    date_created: datetime
    author: ChronicleAuthor | None

    class Config:
        getter_dict = ChronicleGetterDict


class ChroniclePreview(BaseChronicle):
    content_preview: str


class OfferChronicle(BaseChronicle):
    content: str


class OfferChronicles(ConfiguredBaseModel):
    chronicles: list[OfferChronicle]


class OfferArtist(ConfiguredBaseModel):
    id: str
    image: str | None
    name: str
    role: ArtistType | None


class OfferVideo(ConfiguredBaseModel):
    id: str
    title: str | None
    thumbUrl: str | None
    durationSeconds: int | None


class BaseOfferResponse(ConfiguredBaseModel):
    id: int
    accessibility: OfferAccessibilityResponse
    address: OfferAddressResponse | None
    artists: list[OfferArtist]
    chronicles: list[ChroniclePreview]
    chronicles_count: int | None
    description: str | None
    expense_domains: list[ExpenseDomain]
    externalTicketOfficeUrl: str | None
    extraData: OfferExtraDataResponse | None
    isExpired: bool
    isExternalBookingsDisabled: bool
    isEvent: bool
    isHeadline: bool
    is_forbidden_to_underage: bool
    isReleased: bool
    isSoldOut: bool
    isDigital: bool
    isDuo: bool
    isEducational: bool
    last30DaysBookings: int | None
    metadata: offer_metadata.Metadata
    name: str
    publicationDate: datetime | None
    bookingAllowedDatetime: datetime | None
    reactions_count: ReactionCount
    stocks: list[OfferStockResponse]
    subcategoryId: subcategories.SubcategoryIdEnum
    venue: OfferVenueResponse
    video: OfferVideo | None
    withdrawalDetails: str | None
    openingHours: opening_hours_schemas.WeekdayOpeningHoursTimespans | None

    class Config:
        getter_dict = BaseOfferResponseGetterDict


class OfferResponse(BaseOfferResponse):
    image: OfferImageResponse | None


class OfferResponseV2(BaseOfferResponse):
    images: dict[str, OfferImageResponse] | None


class OffersStocksResponseV2(BaseModel):
    offers: list[OfferResponseV2]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


@dataclass
class RawScreening:
    city: str
    beginning_datetime: datetime
    distance: float
    features: list[str]
    label: str
    price: float
    postal_code: str
    stock_id: int
    street: str
    thumb_url: str
    venue_id: int


class MovieScreeningsRequest(HttpQueryParamsModel):
    allocine_id: str | None = None
    visa: str | None = None
    latitude: float
    longitude: float
    around_radius: int = 50_000  # meters
    from_datetime: datetime = pydantic_v2.Field(alias="from", default_factory=date_utils.get_naive_utc_now)
    to_datetime: datetime = pydantic_v2.Field(
        alias="to", default_factory=lambda: datetime.combine(date.today(), time.max) + timedelta(days=15)
    )

    _datetime_serializer = pydantic_v2.field_serializer("from_datetime", "to_datetime")(format_into_utc_date)

    @pydantic_v2.model_validator(mode="after")
    def validate_params(self) -> "MovieScreeningsRequest":
        if (not self.allocine_id and not self.visa) or (self.allocine_id and self.visa):
            raise ValueError("Only one of allocine_id and visa must be provided")

        return self


class Screening(HttpBodyModel):
    beginning_datetime: datetime
    features: list[str]
    price: float
    stock_id: int

    @classmethod
    def from_raw_screening(cls, screening: RawScreening) -> "Screening":
        return cls(
            stock_id=screening.stock_id,
            price=screening.price,
            features=screening.features,
            beginning_datetime=screening.beginning_datetime,
        )

    @classmethod
    def from_stock(cls, stock: models.Stock) -> "Screening":
        return cls(
            stock_id=stock.id,
            price=stock.price,
            features=stock.features,
            beginning_datetime=stock.beginningDatetime,
        )


class VenueScreenings(HttpBodyModel):
    address: str
    distance: float
    label: str
    thumb_url: str | None
    venue_id: int
    day_screenings: list[Screening]
    next_screening: Screening | None

    @classmethod
    def from_raw_screening(cls, screening: RawScreening) -> "VenueScreenings":
        return cls(
            address=f"{screening.street}, {screening.postal_code} {screening.city}",
            distance=screening.distance,
            label=screening.label,
            thumb_url=screening.thumb_url,
            venue_id=screening.venue_id,
            day_screenings=[],
            next_screening=None,
        )


class MovieCalendarResponse(HttpBodyModel):
    calendar: dict[date, list[VenueScreenings]]

    @classmethod
    def from_raw_screenings(
        cls, raw_screenings: list[RawScreening], start_date: datetime, end_date: datetime
    ) -> "MovieCalendarResponse":
        calendar = {}
        for day_delta in range((end_date - start_date).days + 1):
            day = (start_date + timedelta(days=day_delta)).date()
            venues: dict[int, VenueScreenings] = {}
            for raw_screening in raw_screenings:
                venue_id = raw_screening.venue_id
                if venue_id not in venues:
                    venues[venue_id] = VenueScreenings.from_raw_screening(raw_screening)

                venue = venues[venue_id]
                screening = Screening.from_raw_screening(raw_screening)
                if screening.beginning_datetime.date() == day:
                    venue.day_screenings.append(screening)

                if not venue.next_screening:
                    venue.next_screening = screening
                    continue

                current_delta_from_day = (venue.next_screening.beginning_datetime.date() - day).days
                new_delta_from_day = (screening.beginning_datetime.date() - day).days
                if abs(new_delta_from_day) < abs(current_delta_from_day):
                    venue.next_screening = screening

            sorted_screenings = sorted(
                venues.values(), key=lambda venue: (len(venue.day_screenings) == 0, venue.distance)
            )
            for venue in venues.values():
                venue.day_screenings.sort(key=lambda screening: screening.beginning_datetime)

            calendar[day] = sorted_screenings

        return cls(calendar=calendar)


class VenueMovieScreeningsRequest(HttpBodyModel):
    from_datetime: datetime = pydantic_v2.Field(alias="from", default_factory=date_utils.get_naive_utc_now)
    to_datetime: datetime = pydantic_v2.Field(
        alias="to", default_factory=lambda: datetime.combine(date.today(), time.max) + timedelta(days=15)
    )

    _datetime_serializer = pydantic_v2.field_serializer("from_datetime", "to_datetime")(format_into_utc_date)


class MovieScreenings(HttpBodyModel):
    duration: int | None
    genres: list[str]
    last_30_days_bookings: int
    movie_name: str
    offer_id: int
    thumb_url: str | None
    day_screenings: list[Screening]
    next_screening: Screening | None

    @classmethod
    def from_offer(cls, offer: models.Offer) -> "MovieScreenings":
        genres = []
        if offer.extraData and offer.extraData.get("genres"):
            for genre in offer.extraData["genres"] or []:  # `or []` helps mypy
                label = get_movie_label(genre)
                if label:
                    genres.append(label)

        last_30_days_bookings = 0
        if offer.product and offer.product.last_30_days_booking:
            last_30_days_bookings = offer.product.last_30_days_booking

        return cls(
            duration=offer.durationMinutes,
            genres=genres,
            last_30_days_bookings=last_30_days_bookings,
            movie_name=offer.name,
            offer_id=offer.id,
            thumb_url=offer.thumbUrl,
            day_screenings=[],
            next_screening=None,
        )


class VenueMovieCalendarResponse(HttpBodyModel):
    calendar: dict[date, list[MovieScreenings]]

    @classmethod
    def from_offers(
        cls, offers: list[models.Offer], start_date: datetime, end_date: datetime
    ) -> "VenueMovieCalendarResponse":
        calendar = {}
        for day_delta in range((end_date - start_date).days + 1):
            day = (start_date + timedelta(days=day_delta)).date()
            movies: dict[int, MovieScreenings] = {}
            for offer in offers:
                if offer.id not in movies:
                    movies[offer.id] = MovieScreenings.from_offer(offer)

                movie = movies[offer.id]
                for stock in offer.stocks:
                    screening = Screening.from_stock(stock)
                    if screening.beginning_datetime.date() == day:
                        movie.day_screenings.append(screening)

                    if not movie.next_screening:
                        movie.next_screening = screening
                        continue

                    current_delta_from_day = (movie.next_screening.beginning_datetime.date() - day).days
                    new_delta_from_day = (screening.beginning_datetime.date() - day).days
                    if abs(new_delta_from_day) < abs(current_delta_from_day):
                        movie.next_screening = screening

            sorted_screenings = sorted(
                movies.values(), key=lambda movie: (len(movie.day_screenings) == 0, -movie.last_30_days_bookings)
            )
            for movie in movies.values():
                movie.day_screenings.sort(key=lambda screening: screening.beginning_datetime)

            calendar[day] = sorted_screenings

        return cls(calendar=calendar)


class OffersStocksRequest(BaseModel):
    offer_ids: list[int]


class OfferReportReasons(BaseModel):
    class Config:
        alias_generator = to_camel

    reasons: dict[str, ReasonMeta]


class ReportedOffer(BaseModel):
    offer_id: int
    reported_at: datetime
    reason: Reason

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True
