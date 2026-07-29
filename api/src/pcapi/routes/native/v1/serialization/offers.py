import logging
import textwrap
from collections.abc import Callable
from datetime import date
from datetime import datetime
from typing import Annotated
from typing import Any
from typing import Self

from pydantic import BaseModel
from pydantic import BeforeValidator
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator

from pcapi.core.artist.models import ArtistType
from pcapi.core.bookings.api import compute_booking_cancellation_limit_date
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres.movie import get_movie_label
from pcapi.core.categories.genres.music import MUSIC_SUB_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.music import MUSIC_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.show import SHOW_SUB_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.show import SHOW_TYPES_LABEL_BY_CODE
from pcapi.core.chronicles.api import get_offer_published_chronicles
from pcapi.core.chronicles.models import Chronicle
from pcapi.core.chronicles.models import ChronicleClubType
from pcapi.core.finance.utils import to_cents
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models
from pcapi.core.offers import offer_metadata
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.providers import constants as provider_constants
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.core.users.models import ExpenseDomain
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.serialization.common_models import LatitudeFloat
from pcapi.serialization.common_models import LongitudeFloat
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


class OfferOffererResponseV2(BaseModel):
    name: str


class OfferStockActivationCodeResponseV2(BaseModel):
    expirationDate: datetime | None = None


def _none_if_unlimited(value: Any) -> Any:
    if value == "unlimited":
        return None
    return value


class OfferStockResponseV2(HttpBodyModel):
    id: int
    beginningDatetime: datetime | None = None
    bookingLimitDatetime: datetime | None = None
    cancellation_limit_datetime: datetime | None = None
    features: list[str]
    isBookable: bool
    is_forbidden_to_underage: bool
    isSoldOut: bool
    isExpired: bool
    price: Annotated[int, BeforeValidator(to_cents)]
    activationCode: OfferStockActivationCodeResponseV2 | None = None
    priceCategoryLabel: str | None = None
    remainingQuantity: Annotated[int | None, BeforeValidator(_none_if_unlimited)] = None

    @classmethod
    def build(cls, stock: models.Stock) -> Self:
        if not stock.canHaveActivationCodes:
            activation_code = None
        else:
            # here we have N+1 requests (for each stock we query an activation code)
            # but it should be more efficient than loading all activationCodes of all stocks
            activation_code = offers_repository.get_available_activation_code(stock)

        return cls(
            id=stock.id,
            beginningDatetime=stock.beginningDatetime,
            bookingLimitDatetime=stock.bookingLimitDatetime,
            cancellation_limit_datetime=compute_booking_cancellation_limit_date(
                stock.beginningDatetime, date_utils.get_naive_utc_now()
            ),
            features=stock.features,
            isBookable=stock.isBookable,
            is_forbidden_to_underage=stock.is_forbidden_to_underage,
            isSoldOut=stock.isSoldOut,
            isExpired=stock.isExpired,
            price=stock.price,
            activationCode=OfferStockActivationCodeResponseV2(expirationDate=activation_code.expirationDate)
            if activation_code
            else None,
            priceCategoryLabel=stock.priceCategory.label if stock.priceCategory else None,
            remainingQuantity=stock.remainingQuantity,
        )


class AddressCoordinates(BaseModel):
    latitude: LatitudeFloat | None = None
    longitude: LongitudeFloat | None = None


class OfferVenueResponseV2(HttpBodyModel):
    id: int
    address: str | None = None
    city: str | None = None
    managingOfferer: OfferOffererResponseV2 = Field(alias="offerer")
    name: str
    postalCode: str | None = None
    publicName: str
    coordinates: AddressCoordinates
    isPermanent: bool
    isOpenToPublic: bool
    timezone: str
    bannerUrl: str | None = None

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> Self:
        address = venue.offererAddress.address
        return cls(
            id=venue.id,
            address=address.street,
            city=address.city,
            managingOfferer=OfferOffererResponseV2(name=venue.managingOfferer.name),
            name=venue.publicName,
            postalCode=address.postalCode,
            publicName=venue.publicName,
            coordinates=AddressCoordinates(latitude=address.latitude, longitude=address.longitude),
            isPermanent=venue.isPermanent,
            isOpenToPublic=venue.isOpenToPublic,
            timezone=address.timezone,
            bannerUrl=venue.bannerUrl,
        )


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


class GtlLabelsV2(BaseModel):
    label: str
    level01Label: str | None = None
    level02Label: str | None = None
    level03Label: str | None = None
    level04Label: str | None = None


class OfferExtraDataResponseV2(HttpBodyModel):
    allocineId: int | None = None
    author: str | None = None
    durationMinutes: int | None = None
    ean: str | None = None
    musicSubType: Annotated[
        str | None, BeforeValidator(get_id_converter(MUSIC_SUB_TYPES_LABEL_BY_CODE, "musicSubType"))
    ] = None
    musicType: Annotated[str | None, BeforeValidator(get_id_converter(MUSIC_TYPES_LABEL_BY_CODE, "musicType"))] = None
    performer: str | None = None
    showSubType: Annotated[
        str | None, BeforeValidator(get_id_converter(SHOW_SUB_TYPES_LABEL_BY_CODE, "showSubType"))
    ] = None
    showType: Annotated[str | None, BeforeValidator(get_id_converter(SHOW_TYPES_LABEL_BY_CODE, "showType"))] = None
    stageDirector: str | None = None
    speaker: str | None = None
    visa: str | None = None
    releaseDate: date | None = None
    certificate: str | None = None
    bookFormat: str | None = None
    cast: list[str] | None = None
    editeur: str | None = None
    gtlLabels: GtlLabelsV2 | None = None
    genres: list[str] | None = None

    model_config = ConfigDict(extra="ignore")

    @field_validator("genres", mode="after")
    def convert_movie_types(cls, genres: list[str] | None) -> list[str] | None:
        if not genres:
            return None
        movie_types = []
        for genre in genres:
            movie_type = get_movie_label(genre)
            if movie_type:
                movie_types.append(movie_type)
        return movie_types


class OfferAccessibilityResponseV2(HttpBodyModel):
    audioDisability: bool | None = None
    mentalDisability: bool | None = None
    motorDisability: bool | None = None
    visualDisability: bool | None = None


class OfferImageResponseV2(HttpBodyModel):
    url: str
    credit: str | None = None


def get_gtl_labels(gtl_id: str) -> GtlLabelsV2 | None:
    if gtl_id not in GTLS:
        return None
    gtl_infos = GTLS[gtl_id]
    label = gtl_infos.get("label")
    if label:
        return GtlLabelsV2(
            label=label,
            level01Label=gtl_infos.get("level_01_label"),
            level02Label=gtl_infos.get("level_02_label"),
            level03Label=gtl_infos.get("level_03_label"),
            level04Label=gtl_infos.get("level_04_label"),
        )
    logger.error("GTL label not found for id %s", gtl_id)
    return None


class ReactionCountV2(BaseModel):
    likes: int


MAX_PREVIEW_CHRONICLES = 5


class ChroniclePreviewAuthorV2(HttpBodyModel):
    first_name: str | None = None
    age: int | None = None
    city: str | None = None


class ChroniclePreviewV2(HttpBodyModel):
    id: int
    author: ChroniclePreviewAuthorV2 | None = None
    content_preview: str
    date_created: datetime

    @classmethod
    def build(cls, chronicle: Chronicle) -> Self:
        if chronicle.isIdentityDiffusible:
            author = ChroniclePreviewAuthorV2(
                first_name=chronicle.firstName,
                age=chronicle.age,
                city=chronicle.city,
            )
        else:
            author = None

        return cls(
            id=chronicle.id,
            author=author,
            content_preview=textwrap.shorten(chronicle.content, width=255, placeholder="…"),
            date_created=chronicle.dateCreated,
        )


class OfferChronicleAuthor(HttpBodyModel):
    first_name: str | None = None
    age: int | None = None
    city: str | None = None


class OfferChronicle(HttpBodyModel):
    id: int
    author: OfferChronicleAuthor | None = None
    club_type: ChronicleClubType
    content: str
    date_created: datetime

    @classmethod
    def build(cls, chronicle: Chronicle) -> Self:
        if chronicle.isIdentityDiffusible:
            author = OfferChronicleAuthor(
                first_name=chronicle.firstName,
                age=chronicle.age,
                city=chronicle.city,
            )
        else:
            author = None

        return cls(
            id=chronicle.id,
            author=author,
            club_type=chronicle.clubType,
            content=chronicle.content,
            date_created=chronicle.dateCreated,
        )


class OfferChronicles(HttpBodyModel):
    chronicles: list[OfferChronicle]


class OfferArtistV2(HttpBodyModel):
    id: str
    image: str | None = None
    name: str
    role: ArtistType | None = None


class OfferVideoV2(HttpBodyModel):
    id: str
    title: str | None = None
    thumbUrl: str | None = None
    durationSeconds: int | None = None


class OfferAddressResponseV2(HttpBodyModel):
    street: str | None = None
    postalCode: str
    city: str
    label: str | None = None
    coordinates: AddressCoordinates
    timezone: str


class OfferResponseV2(HttpBodyModel):
    id: int
    accessibility: OfferAccessibilityResponseV2
    address: OfferAddressResponseV2 | None = None
    artists: list[OfferArtistV2]
    chronicles: list[ChroniclePreviewV2]
    chronicles_count: int | None = None
    description: str | None = None
    expense_domains: list[ExpenseDomain]
    externalTicketOfficeUrl: str | None = None
    extraData: OfferExtraDataResponseV2 | None = None
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
    images: dict[str, OfferImageResponseV2] | None = None
    last30DaysBookings: int | None = None
    metadata: offer_metadata.Metadata
    name: str
    publicationDate: datetime | None = None
    bookingAllowedDatetime: datetime | None = None
    reactions_count: ReactionCountV2
    stocks: list[OfferStockResponseV2]
    subcategoryId: subcategories.SubcategoryIdEnum
    venue: OfferVenueResponseV2
    video: OfferVideoV2 | None = None
    withdrawalDetails: str | None = None

    @classmethod
    def build(cls, offer: models.Offer) -> Self:
        product: models.Product | None = offer.product
        if product:
            likes = product.likesCount or 0
            artists = [
                OfferArtistV2(
                    id=artist_link.artist.id,
                    image=artist_link.artist.image,
                    name=artist_link.artist.name,
                    role=artist_link.artist_type if artist_link.artist_type else None,
                )
                for artist_link in product.artistLinks
                if not artist_link.artist.is_blacklisted
            ]
            last_30_days_bookings = product.last_30_days_booking
            raw_extra_data = product.extraData or {}
            chronicles_count = product.chroniclesCount or offer.chroniclesCount
        else:
            likes = offer.likesCount or 0
            artists = []
            last_30_days_bookings = None
            raw_extra_data = offer.extraData or {}
            chronicles_count = offer.chroniclesCount

        if offer.lastProvider and offer.lastProvider.localClass in provider_constants.PROVIDER_LOCAL_CLASS_TO_FF:
            is_external_bookings_disabled = provider_constants.PROVIDER_LOCAL_CLASS_TO_FF[
                offer.lastProvider.localClass
            ].is_active()
        else:
            is_external_bookings_disabled = False

        extra_data = OfferExtraDataResponseV2.model_validate(raw_extra_data)
        extra_data.durationMinutes = offer.durationMinutes
        gtl_id = raw_extra_data.get("gtl_id")
        if gtl_id is not None:
            extra_data.gtlLabels = get_gtl_labels(gtl_id)
        if offer.ean:
            extra_data.ean = offer.ean

        offerer_address = offer.offererAddress or offer.venue.offererAddress
        address = offerer_address.address
        address_response = OfferAddressResponseV2(
            street=address.street,
            postalCode=address.postalCode,
            city=address.city,
            label=offerer_address.label,
            coordinates=AddressCoordinates(latitude=address.latitude, longitude=address.longitude),
            timezone=address.timezone,
        )

        if offer.metaData and offer.metaData.videoUrl and not offer.metaData.videoExternalId:
            logger.error(
                "This offer has a video URL but no videoExternalId in its metaData, and this should not happen",
                extra={"offer_id": offer.id},
            )

        if offer.metaData and offer.metaData.videoExternalId:
            video = OfferVideoV2(
                id=offer.metaData.videoExternalId,
                title=offer.metaData.videoTitle,
                thumbUrl=offer.metaData.videoThumbnailUrl,
                durationSeconds=offer.metaData.videoDuration,
            )
        else:
            video = None

        return cls(
            id=offer.id,
            accessibility=OfferAccessibilityResponseV2(
                audioDisability=offer.audioDisabilityCompliant,
                mentalDisability=offer.mentalDisabilityCompliant,
                motorDisability=offer.motorDisabilityCompliant,
                visualDisability=offer.visualDisabilityCompliant,
            ),
            address=address_response,
            artists=artists,
            chronicles=[
                ChroniclePreviewV2.build(chronicle)
                for chronicle in get_offer_published_chronicles(offer)[:MAX_PREVIEW_CHRONICLES]
            ],
            chronicles_count=chronicles_count,
            description=offer.description,
            expense_domains=get_expense_domains(offer),
            externalTicketOfficeUrl=offer.externalTicketOfficeUrl,
            extraData=extra_data,
            isExpired=offer.hasBookingLimitDatetimesPassed,
            isExternalBookingsDisabled=is_external_bookings_disabled,
            isEvent=offer.isEvent,
            isHeadline=offer.is_headline_offer,
            is_forbidden_to_underage=offer.is_forbidden_to_underage,
            isReleased=offer.isReleased,
            isSoldOut=offer.isSoldOut,
            isDigital=offer.isDigital,
            isDuo=offer.isDuo,
            isEducational=offer.isEducational,
            images={
                image_type: OfferImageResponseV2(url=image.url, credit=image.credit)
                for image_type, image in offer.images.items()
            }
            if offer.images
            else None,
            last30DaysBookings=last_30_days_bookings,
            metadata=offer_metadata.get_metadata_from_offer(offer),
            name=offer.name,
            publicationDate=offer.bookingAllowedDatetime,  # FIXME (bpeyrou): to be removed when min app version stop using publicationDate
            bookingAllowedDatetime=offer.bookingAllowedDatetime,
            reactions_count=ReactionCountV2(likes=likes),
            stocks=[OfferStockResponseV2.build(stock) for stock in offer.activeStocks],
            subcategoryId=offer.subcategoryId,
            venue=OfferVenueResponseV2.build(offer.venue),
            video=video,
            withdrawalDetails=offer.withdrawalDetails,
        )


class OffersStocksResponseV2(HttpBodyModel):
    offers: list[OfferResponseV2]


class OffersStocksRequest(HttpBodyModel):
    offer_ids: list[int]


class OfferProAdviceQuery(HttpQueryParamsModel):
    max_content_length: int | None = None
    page: int = Field(default=1, ge=1, le=20)
    results_per_page: int = Field(default=20, ge=1, le=50)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def validate_params(self) -> "OfferProAdviceQuery":
        if (self.latitude and not self.longitude) or (not self.latitude and self.longitude):
            raise ValueError("Latitude and longitude must be provided together")

        return self


class OfferProAdvice(HttpBodyModel):
    author: str | None = None
    content: str
    distance: int | None = None
    publication_datetime: datetime
    venue_id: int
    venue_name: str
    venue_thumb_url: str | None = None

    @classmethod
    def build(
        cls, pro_advice: models.ProAdvice, distance: int | None, max_content_length: int | None
    ) -> "OfferProAdvice":
        content = pro_advice.content
        if max_content_length:
            content = textwrap.shorten(content, width=max_content_length, placeholder="…")

        return cls(
            author=pro_advice.author,
            content=content,
            distance=distance if pro_advice.venue.isOpenToPublic else None,
            venue_id=pro_advice.venue.id,
            venue_name=pro_advice.venue.publicName,
            venue_thumb_url=pro_advice.venue.bannerUrl,
            publication_datetime=pro_advice.updatedAt,
        )


class OfferProAdvices(HttpBodyModel):
    pro_advices: list[OfferProAdvice]
    nb_results: int
