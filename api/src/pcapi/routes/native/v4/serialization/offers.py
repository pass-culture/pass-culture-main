import datetime
import logging
import textwrap
from typing import Any

import pydantic as pydantic_v2

from pcapi.core.chronicles import models as chronicle_models
from pcapi.core.offers import models
from pcapi.core.offers import offer_metadata
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.providers import constants as provider_constants
from pcapi.core.users.models import ExpenseDomain
from pcapi.routes.native.v3.serialization import offers as v3_serializers
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


logger = logging.getLogger(__name__)


def _serialize_offer_artists(offer: models.Offer) -> list[v3_serializers.OfferArtist]:
    if offer.product:
        return [
            v3_serializers.OfferArtist(
                id=artist_link.artist.id,
                image=artist_link.artist.thumbUrl,
                name=artist_link.artist.name,
                role=artist_link.artist_type if artist_link.artist_type else None,
            )
            for artist_link in offer.product.artistLinks
            if not artist_link.artist.is_blacklisted
        ]

    artists = []
    for artist_link in offer.artistOfferLinks:
        if artist_link.artist and not artist_link.artist.is_blacklisted:
            artists.append(
                v3_serializers.OfferArtist(
                    id=artist_link.artist_id,
                    image=artist_link.artist.thumbUrl,
                    name=artist_link.artist.name,
                    role=artist_link.artist_type,
                )
            )
        elif artist_link.custom_name:
            artists.append(
                v3_serializers.OfferArtist(
                    id=None,
                    image=None,
                    name=artist_link.custom_name,
                    role=artist_link.artist_type,
                )
            )

    return artists


class OfferResponse(HttpBodyModel):
    id: int
    name: str
    subcategory_id: str
    artists: list[v3_serializers.OfferArtist]
    booking_allowed_datetime: datetime.datetime | None
    expense_domains: list[ExpenseDomain]
    external_ticket_office_url: str | None = None
    extra_data: v3_serializers.OfferExtraDataResponse | None = None
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
    last_30_days_bookings: int | None = None
    publication_date: datetime.datetime | None
    video: v3_serializers.OfferVideo | None = None

    @classmethod
    def build(cls, offer: models.Offer) -> "OfferResponse":
        product = offer.product

        is_external_bookings_disabled = False
        if offer.lastProvider and offer.lastProvider.localClass in provider_constants.PROVIDER_LOCAL_CLASS_TO_FF:
            is_external_bookings_disabled = provider_constants.PROVIDER_LOCAL_CLASS_TO_FF[
                offer.lastProvider.localClass
            ].is_active()

        raw_extra_data = (product.extraData if product else offer.extraData) or {}
        extra_data = v3_serializers.OfferExtraDataResponse.model_validate(raw_extra_data)
        extra_data.duration_minutes = offer.durationMinutes
        gtl_id = raw_extra_data.get("gtl_id")
        if gtl_id is not None:
            extra_data.gtl_labels = v3_serializers.get_gtl_labels(gtl_id)
        if offer.ean:
            extra_data.ean = offer.ean

        video = None
        if offer.metaData and offer.metaData.videoUrl and not offer.metaData.videoExternalId:
            logger.error(
                "This offer has a video URL but no videoExternalId in its metaData, and this should not happen",
                extra={"offer_id": offer.id},
            )
        if offer.metaData and offer.metaData.videoExternalId:
            video = v3_serializers.OfferVideo(
                id=offer.metaData.videoExternalId,
                duration_seconds=offer.metaData.videoDuration,
                thumb_url=offer.metaData.videoThumbnailUrl,
                title=offer.metaData.videoTitle,
            )

        return cls(
            id=offer.id,
            name=offer.name,
            subcategory_id=offer.subcategoryId,
            artists=_serialize_offer_artists(offer),
            booking_allowed_datetime=offer.bookingAllowedDatetime,
            expense_domains=[domain.value for domain in get_expense_domains(offer)],
            external_ticket_office_url=offer.externalTicketOfficeUrl,
            extra_data=extra_data,
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
            last_30_days_bookings=product.last_30_days_booking if product else None,
            publication_date=offer.bookingAllowedDatetime,
            video=video,
        )


# ──────────────────────────────────────────────────────────────────────────────
# GET /native/v4/offer/<id>/header  —  images + likes count + SEO metadata
# ──────────────────────────────────────────────────────────────────────────────


class OfferHeaderResponse(HttpBodyModel):
    """Images, likes count and SEO metadata for the native v4 offer page header."""

    images: dict[str, v3_serializers.OfferImageResponse] | None = None
    likes_count: int
    metadata: dict[str, Any]

    @classmethod
    def build(cls, offer: models.Offer) -> "OfferHeaderResponse":
        product = offer.product

        images = None
        if offer.images:
            images = {
                image_type: v3_serializers.OfferImageResponse(url=img.url, credit=img.credit)
                for image_type, img in offer.images.items()
            }

        likes_count = (product.likesCount if product else None) or 0

        return cls(
            images=images,
            likes_count=likes_count,
            metadata=offer_metadata.get_metadata_from_offer(offer),
        )


class OfferAccessibilityResponse(HttpBodyModel):
    audio_disability: bool | None = None
    mental_disability: bool | None = None
    motor_disability: bool | None = None
    visual_disability: bool | None = None


class OfferVenueResponse(HttpBodyModel):
    id: int
    banner_url: str | None = None
    is_open_to_public: bool
    is_permanent: bool
    name: str
    public_name: str
    venue_type_code: str


class OfferOffererResponse(HttpBodyModel):
    """Venue, offerer, address, accessibility and description for the native v4 offerer section."""

    accessibility: OfferAccessibilityResponse
    address: v3_serializers.OfferAddressResponse | None = None
    description: str | None = None
    offerer_name: str
    venue: OfferVenueResponse
    withdrawal_details: str | None = None

    @classmethod
    def build(cls, offer: models.Offer) -> "OfferOffererResponse":
        venue = offer.venue

        # address: offer-level override takes precedence over venue-level
        address = None
        offerer_address = offer.offererAddress or venue.offererAddress
        if offerer_address and offerer_address.address:
            addr = offerer_address.address
            address = v3_serializers.OfferAddressResponse(
                city=addr.city,
                coordinates=v3_serializers.OfferVenueCoordinates(
                    latitude=float(addr.latitude),
                    longitude=float(addr.longitude),
                ),
                label=offerer_address.label,
                postal_code=addr.postalCode,
                street=addr.street,
                timezone=addr.timezone,
            )

        return cls(
            accessibility=OfferAccessibilityResponse(
                audio_disability=offer.audioDisabilityCompliant,
                mental_disability=offer.mentalDisabilityCompliant,
                motor_disability=offer.motorDisabilityCompliant,
                visual_disability=offer.visualDisabilityCompliant,
            ),
            address=address,
            description=offer.description,
            offerer_name=venue.managingOfferer.name,
            venue=OfferVenueResponse(
                id=venue.id,
                banner_url=venue.bannerUrl,
                is_open_to_public=venue.isOpenToPublic,
                is_permanent=venue.isPermanent,
                name=venue.name,
                public_name=venue.publicName,
                venue_type_code=venue.venueTypeCode.name,
            ),
            withdrawal_details=offer.withdrawalDetails,
        )


class OfferChroniclesQuery(HttpQueryParamsModel):
    page: int = pydantic_v2.Field(default=1, ge=1, le=100)
    limit: int = pydantic_v2.Field(default=10, ge=1, le=50)


class OfferChronicleAuthorResponse(HttpBodyModel):
    age: int | None = None
    city: str | None = None
    first_name: str | None = None


class OfferChronicleResponse(HttpBodyModel):
    id: int
    author: OfferChronicleAuthorResponse | None = None
    content: str
    date_created: datetime.datetime

    @classmethod
    def build(cls, chronicle: chronicle_models.Chronicle) -> "OfferChronicleResponse":
        author = None
        if chronicle.isIdentityDiffusible:
            author = OfferChronicleAuthorResponse(
                age=chronicle.age,
                city=chronicle.city,
                first_name=chronicle.firstName,
            )
        return cls(
            id=chronicle.id,
            author=author,
            content=chronicle.content,
            date_created=chronicle.dateCreated,
        )


class OfferChroniclesResponse(HttpBodyModel):
    chronicles: list[OfferChronicleResponse]
    chronicles_count: int

    @classmethod
    def build(cls, chronicles: list[chronicle_models.Chronicle], total: int) -> "OfferChroniclesResponse":
        return cls(
            chronicles=[OfferChronicleResponse.build(c) for c in chronicles],
            chronicles_count=total,
        )


class OfferProAdvicesQuery(HttpQueryParamsModel):
    max_content_length: int | None = None
    page: int = pydantic_v2.Field(default=1, ge=1, le=20)
    limit: int = pydantic_v2.Field(default=20, ge=1, le=50)
    latitude: float | None = pydantic_v2.Field(default=None, ge=-90, le=90)
    longitude: float | None = pydantic_v2.Field(default=None, ge=-180, le=180)

    @pydantic_v2.model_validator(mode="after")
    def validate_params(self) -> "OfferProAdvicesQuery":
        if (self.latitude and not self.longitude) or (not self.latitude and self.longitude):
            raise ValueError("Latitude and longitude must be provided together")
        return self


class OfferProAdviceResponse(HttpBodyModel):
    author: str | None = None
    content: str
    distance: int | None = None
    publication_datetime: datetime.datetime
    venue_id: int
    venue_name: str
    venue_thumb_url: str | None = None

    @classmethod
    def build(
        cls,
        pro_advice: models.ProAdvice,
        distance: int | None,
        max_content_length: int | None,
    ) -> "OfferProAdviceResponse":
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


class OfferProAdvicesResponse(HttpBodyModel):
    pro_advices: list[OfferProAdviceResponse]
    pro_advices_count: int


class OfferStocksQuery(HttpQueryParamsModel):
    page: int = pydantic_v2.Field(default=1, ge=1, le=1000)
    limit: int = pydantic_v2.Field(default=20, ge=1, le=50)


class OfferStocksResponse(HttpBodyModel):
    stocks: list[v3_serializers.OfferStockResponse]
    stocks_count: int
