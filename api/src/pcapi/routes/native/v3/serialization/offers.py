import datetime
import logging
import textwrap
import typing
from typing import Any
from typing import Callable

import pydantic as pydantic_v2

from pcapi.core.bookings.api import compute_booking_cancellation_limit_date
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres.movie import get_movie_label
from pcapi.core.categories.genres.music import MUSIC_SUB_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.music import MUSIC_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.show import SHOW_SUB_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.show import SHOW_TYPES_LABEL_BY_CODE
from pcapi.core.chronicles import models as chronicle_models
from pcapi.core.chronicles.api import get_offer_published_chronicles
from pcapi.core.geography.models import Address
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models
from pcapi.core.offers import offer_metadata
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.providers import constants as provider_constants
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.core.users.models import ExpenseDomain
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.shared.price import convert_to_cent
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


MAX_PREVIEW_CHRONICLES = 5


class OfferOffererResponse(HttpBodyModel):
    name: str


class OfferStockActivationCodeResponse(HttpBodyModel):
    expiration_date: datetime.datetime | None


class OfferStockResponse(HttpBodyModel):
    id: int
    activation_code: OfferStockActivationCodeResponse | None
    beginning_datetime: datetime.datetime | None
    booking_limit_datetime: datetime.datetime | None
    cancellation_limit_datetime: datetime.datetime | None
    features: list[str]
    is_bookable: bool
    is_expired: bool
    is_forbidden_to_underage: bool
    is_sold_out: bool
    price: int
    price_category_label: str | None
    remaining_quantity: int | None

    @classmethod
    def build(cls, stock: models.Stock) -> "OfferStockResponse":
        activation_code_response = None
        if stock.canHaveActivationCodes:
            # here we have N+1 requests (for each stock we query an activation code)
            # but it should be more efficient than loading all activationCodes of all stocks
            activation_code = offers_repository.get_available_activation_code(stock)
            if activation_code:
                activation_code_response = OfferStockActivationCodeResponse(
                    expiration_date=activation_code.expirationDate
                )

        price = convert_to_cent(stock.price)
        price_category_label = None
        if price_category := stock.priceCategory:
            price_category_label = price_category.priceCategoryLabel.label

        remaining_quantity = stock.remainingQuantity if stock.remainingQuantity != "unlimited" else None

        return cls(
            id=stock.id,
            activation_code=activation_code_response,
            beginning_datetime=stock.beginningDatetime,
            booking_limit_datetime=stock.bookingLimitDatetime,
            cancellation_limit_datetime=compute_booking_cancellation_limit_date(
                stock.beginningDatetime, date_utils.get_naive_utc_now()
            ),
            features=stock.features,
            is_bookable=stock.isBookable,
            is_expired=stock.isExpired,
            is_forbidden_to_underage=stock.is_forbidden_to_underage,
            is_sold_out=stock.isSoldOut,
            price=price,
            price_category_label=price_category_label,
            remaining_quantity=remaining_quantity,
        )


class OfferVenueCoordinates(HttpBodyModel):
    latitude: float | None
    longitude: float | None

    _to_float = pydantic_v2.field_validator("latitude", "longitude", mode="before")(float)


class OfferVenueResponse(HttpBodyModel):
    id: int
    address: str | None
    banner_url: str | None
    city: str | None
    coordinates: OfferVenueCoordinates
    is_open_to_public: bool
    is_permanent: bool
    managing_offerer: OfferOffererResponse = pydantic_v2.Field(..., alias="offerer")
    name: str
    postal_code: str | None
    public_name: str
    timezone: str

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> "OfferVenueResponse":
        return cls(
            id=venue.id,
            address=venue.offererAddress.address.street,
            banner_url=venue.bannerUrl,
            city=venue.offererAddress.address.city,
            coordinates=OfferVenueCoordinates(
                latitude=venue.offererAddress.address.latitude,
                longitude=venue.offererAddress.address.longitude,
            ),
            is_permanent=venue.isPermanent,
            is_open_to_public=venue.isOpenToPublic,
            managing_offerer=OfferOffererResponse.model_validate(venue.managingOfferer),
            name=venue.common_name,
            postal_code=venue.offererAddress.address.postalCode,
            public_name=venue.publicName,
            timezone=venue.offererAddress.address.timezone,
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


class GtlLabels(HttpBodyModel):
    label: str
    level_01_label: str | None
    level_02_label: str | None
    level_03_label: str | None
    level_04_label: str | None


class OfferExtraDataResponse(HttpBodyModel):
    allocine_id: int | None = None
    author: str | None = None
    book_format: str | None = None
    cast: list[str] | None = None
    certificate: str | None = None
    duration_minutes: int | None = None
    ean: str | None = None
    editeur: str | None = None
    genres: list[str] | None = None
    gtl_labels: GtlLabels | None = None
    music_sub_type: str | None = None
    music_type: str | None = None
    performer: str | None = None
    release_date: datetime.date | None = None
    show_sub_type: str | None = None
    show_type: str | None = None
    speaker: str | None = None
    stage_director: str | None = None
    visa: str | None = None

    model_config = pydantic_v2.ConfigDict(extra="ignore")

    @pydantic_v2.field_validator("genres", mode="before")
    def convert_movie_types(cls, genres: Any) -> list[str] | None:
        if not genres:
            return None
        movie_types = []
        for genre in genres or []:
            movie_type = get_movie_label(genre)
            if movie_type:
                movie_types.append(movie_type)
        return movie_types

    _convert_music_sub_type = pydantic_v2.field_validator("music_sub_type", mode="before")(
        get_id_converter(MUSIC_SUB_TYPES_LABEL_BY_CODE, "music_sub_type")
    )
    _convert_music_type = pydantic_v2.field_validator("music_type", mode="before")(
        get_id_converter(MUSIC_TYPES_LABEL_BY_CODE, "music_type")
    )
    _convert_show_sub_type = pydantic_v2.field_validator("show_sub_type", mode="before")(
        get_id_converter(SHOW_SUB_TYPES_LABEL_BY_CODE, "show_sub_type")
    )
    _convert_show_type = pydantic_v2.field_validator("show_type", mode="before")(
        get_id_converter(SHOW_TYPES_LABEL_BY_CODE, "show_type")
    )


class OfferAccessibilityResponse(HttpBodyModel):
    audio_disability: bool | None
    mental_disability: bool | None
    motor_disability: bool | None
    visual_disability: bool | None


class OfferImageResponse(HttpBodyModel):
    credit: str | None
    url: str


def get_gtl_labels(gtl_id: str) -> GtlLabels | None:
    if gtl_id not in GTLS:
        return None
    gtl_infos = GTLS[gtl_id]
    label = gtl_infos.get("label")
    if label:
        return GtlLabels(
            label=label,
            level_01_label=gtl_infos.get("level_01_label"),
            level_02_label=gtl_infos.get("level_02_label"),
            level_03_label=gtl_infos.get("level_03_label"),
            level_04_label=gtl_infos.get("level_04_label"),
        )
    logger.error("GTL label not found for id %s", gtl_id)
    return None


class OfferAddressResponse(HttpBodyModel):
    city: str
    coordinates: OfferVenueCoordinates
    label: str | None
    postal_code: str
    street: str | None
    timezone: str


class ChronicleAuthor(HttpBodyModel):
    age: int | None
    first_name: str | None
    city: str | None


class ChroniclePreview(HttpBodyModel):
    id: int
    author: ChronicleAuthor | None
    content_preview: str
    date_created: datetime.datetime

    @classmethod
    def build(cls, chronicle: chronicle_models.Chronicle) -> "ChroniclePreview":
        author = None
        if chronicle.isIdentityDiffusible:
            author = ChronicleAuthor(
                age=chronicle.age,
                city=chronicle.city,
                first_name=chronicle.firstName,
            )

        return cls(
            id=chronicle.id,
            author=author,
            content_preview=textwrap.shorten(chronicle.content, width=255, placeholder="…"),
            date_created=chronicle.dateCreated,
        )


class OfferArtist(HttpBodyModel):
    id: str | None
    image: str | None
    name: str


class OfferVideo(HttpBodyModel):
    id: str
    duration_seconds: int | None
    thumb_url: str | None
    title: str | None


# Enums are described slightly differently between pydantic v1 and v2.
# As `ExpenseDomain` and `SubcategoryIdEnum` are still used in other pydantic v1 models,
# we need this one to have the exact same description, not to create
# a conflict during the migration. That's why we use `WithJsonSchema` here.
ExpenseDomainV3 = typing.Annotated[
    ExpenseDomain,
    pydantic_v2.WithJsonSchema(
        {"description": "An enumeration.", "enum": [e.value for e in ExpenseDomain], "title": "ExpenseDomain"}
    ),
]
SubcategoryIdEnumV3 = typing.Annotated[
    subcategories.SubcategoryIdEnum,
    pydantic_v2.WithJsonSchema(
        {
            "description": "An enumeration.",
            "enum": [s.value for s in subcategories.SubcategoryIdEnum],
            "title": "SubcategoryIdEnum",
        }
    ),
]


class OfferResponse(HttpBodyModel):
    id: int
    accessibility: OfferAccessibilityResponse
    address: OfferAddressResponse | None = None
    artists: list[OfferArtist]
    booking_allowed_datetime: datetime.datetime | None
    chronicles: list[ChroniclePreview]
    chronicles_count: int | None = None
    description: str | None = None
    expense_domains: list[ExpenseDomainV3]
    external_ticket_office_url: str | None = None
    extra_data: OfferExtraDataResponse | None = None
    is_digital: bool
    is_duo: bool
    is_educational: bool
    is_event: bool
    is_expired: bool
    is_external_bookings_disabled: bool
    is_forbidden_to_underage: bool
    is_headline: bool
    is_released: bool
    is_sold_out: bool
    images: dict[str, OfferImageResponse] | None = None
    last_30_days_bookings: int | None = None
    likes_count: int
    metadata: offer_metadata.Metadata
    name: str
    publication_date: datetime.datetime | None
    stocks: list[OfferStockResponse]
    subcategory_id: SubcategoryIdEnumV3
    venue: OfferVenueResponse
    video: OfferVideo | None = None
    withdrawal_details: str | None = None

    @classmethod
    def build(cls, offer: models.Offer) -> "OfferResponse":
        product: models.Product | None = offer.product

        likes_count = 0
        if product:
            likes_count = product.likesCount or 0
        else:
            likes_count = offer.likesCount or 0

        accessibility = OfferAccessibilityResponse(
            audio_disability=offer.audioDisabilityCompliant,
            mental_disability=offer.mentalDisabilityCompliant,
            motor_disability=offer.motorDisabilityCompliant,
            visual_disability=offer.visualDisabilityCompliant,
        )

        if product:
            artists = [OfferArtist.model_validate(artist) for artist in product.artists if not artist.is_blacklisted]
        else:
            artists = []
            for artist_link in offer.artistOfferLinks:
                if artist_link.artist and not artist_link.artist.is_blacklisted:
                    artists.append(OfferArtist.model_validate(artist_link.artist))
                elif artist_link.custom_name:
                    artists.append(OfferArtist(id=None, image=None, name=artist_link.custom_name))

        is_external_bookings_disabled = False
        if offer.lastProvider and offer.lastProvider.localClass in provider_constants.PROVIDER_LOCAL_CLASS_TO_FF:
            is_external_bookings_disabled = provider_constants.PROVIDER_LOCAL_CLASS_TO_FF[
                offer.lastProvider.localClass
            ].is_active()

        raw_extra_data = (product.extraData if product else offer.extraData) or {}
        extra_data = OfferExtraDataResponse.model_validate(raw_extra_data)
        extra_data.duration_minutes = offer.durationMinutes
        gtl_id = raw_extra_data.get("gtl_id")
        if gtl_id is not None:
            extra_data.gtl_labels = get_gtl_labels(gtl_id)
        if offer.ean:
            extra_data.ean = offer.ean

        address_response = None
        offerer_address: offerers_models.OffererAddress | None
        if offer.offererAddress:
            offerer_address = offer.offererAddress
        else:
            offerer_address = offer.venue.offererAddress

        if offerer_address:
            address: Address = offerer_address.address
            address_response = OfferAddressResponse(
                city=address.city,
                coordinates=OfferVenueCoordinates(latitude=address.latitude, longitude=address.longitude),
                label=offerer_address.label,
                postal_code=address.postalCode,
                street=address.street,
                timezone=address.timezone,
            )

        published_chronicles = get_offer_published_chronicles(offer)

        video = None
        if offer.metaData and offer.metaData.videoUrl and not offer.metaData.videoExternalId:
            logger.error(
                "This offer has a video URL but no videoExternalId in its metaData, and this should not happen",
                extra={"offer_id": offer.id},
            )

        if offer.metaData and offer.metaData.videoExternalId:
            video = OfferVideo(
                id=offer.metaData.videoExternalId,
                duration_seconds=offer.metaData.videoDuration,
                thumb_url=offer.metaData.videoThumbnailUrl,
                title=offer.metaData.videoTitle,
            )

        return cls(
            id=offer.id,
            accessibility=accessibility,
            address=address_response,
            artists=artists,
            booking_allowed_datetime=offer.bookingAllowedDatetime,
            chronicles=[ChroniclePreview.build(c) for c in published_chronicles[:MAX_PREVIEW_CHRONICLES]],
            chronicles_count=product.chroniclesCount if product and product.chroniclesCount else offer.chroniclesCount,
            description=offer.description,
            expense_domains=map(lambda domain: domain.value, get_expense_domains(offer)),
            external_ticket_office_url=offer.externalTicketOfficeUrl,
            extra_data=extra_data,
            images=offer.images,
            is_digital=offer.isDigital,
            is_duo=offer.isDuo,
            is_educational=offer.isEducational,
            is_event=offer.isEvent,
            is_expired=offer.hasBookingLimitDatetimesPassed,
            is_external_bookings_disabled=is_external_bookings_disabled,
            is_forbidden_to_underage=offer.is_forbidden_to_underage,
            is_headline=offer.is_headline_offer,
            is_released=offer.isReleased,
            is_sold_out=offer.isSoldOut,
            last_30_days_bookings=offer.product.last_30_days_booking if offer.product else None,
            likes_count=likes_count,
            metadata=offer_metadata.get_metadata_from_offer(offer),
            name=offer.name,
            publication_date=offer.bookingAllowedDatetime,
            stocks=[OfferStockResponse.build(stock) for stock in offer.activeStocks],
            subcategory_id=offer.subcategoryId,
            venue=OfferVenueResponse.build(offer.venue),
            video=video,
            withdrawal_details=offer.withdrawalDetails,
        )
