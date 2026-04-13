import enum
import typing
from datetime import datetime
from urllib.parse import urlparse

import pydantic as pydantic_v2
from pydantic import RootModel
from pydantic_core import PydanticCustomError

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.educational import models as educational_models
from pcapi.core.geography.constants import MAX_LATITUDE
from pcapi.core.geography.constants import MAX_LONGITUDE
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.constants import JE_VEUX_AIDER_GOUV_BASE_URL
from pcapi.core.opening_hours import api as opening_hours_api
from pcapi.core.opening_hours import schemas as opening_hours_schemas
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import venue_banners_serialize
from pcapi.routes.serialization import venue_collective_serialize
from pcapi.routes.serialization import venue_finance_serialize
from pcapi.serialization.exceptions import PydanticError
from pcapi.serialization.utils import HttpUrlString
from pcapi.serialization.utils import string_to_boolean
from pcapi.utils import date as date_utils
from pcapi.utils.siren import SIRET_LENGTH


class PostVenueBodyModel(HttpBodyModel):
    activity: offerers_models.Activity | None
    address: address_serialize.LocationBodyModelV2
    booking_email: pydantic_v2.EmailStr = pydantic_v2.Field(max_length=offerers_schemas.BOOKING_EMAIL_MAX_LENGTH)
    cultural_domains: list[str] | None
    comment: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_COMMENT_MAX_LENGTH)
    is_open_to_public: bool | None
    managing_offerer_id: int
    name: str = pydantic_v2.Field(min_length=1, max_length=offerers_schemas.VENUE_NAME_MAX_LENGTH)
    public_name: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_PUBLIC_NAME_MAX_LENGTH)
    siret: str | None = pydantic_v2.Field(min_length=SIRET_LENGTH, max_length=SIRET_LENGTH)
    venue_label_id: int | None
    withdrawal_details: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_WITHDRAWAL_DETAILS_MAX_LENGTH)
    description: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_DESCRIPTION_MAX_LENGTH)
    contact: offerers_schemas.VenueContactModelV2 | None
    audio_disability_compliant: bool | None
    mental_disability_compliant: bool | None
    motor_disability_compliant: bool | None
    visual_disability_compliant: bool | None

    @pydantic_v2.model_validator(mode="after")
    def requires_siret_xor_comment(self) -> typing.Self:
        if (self.comment and self.siret) or (not self.comment and not self.siret):
            raise PydanticCustomError("siret_or_comment_required", "Veuillez saisir soit un SIRET soit un commentaire")
        return self


class GetVenueManagingOffererResponseModel(HttpBodyModel):
    id: int
    isValidated: bool
    name: str
    siren: str


# TODO: move this elsewhere
def get_current_pricing_point(
    venue: offerers_models.Venue,
) -> venue_finance_serialize.GetVenuePricingPointResponseModel | None:
    now = date_utils.get_naive_utc_now()
    for pricing_link in venue.pricing_point_links:
        if pricing_link.timespan.lower <= now and (
            not pricing_link.timespan.upper or pricing_link.timespan.upper > now
        ):
            return venue_finance_serialize.GetVenuePricingPointResponseModel(
                id=pricing_link.pricingPoint.id,
                siret=pricing_link.pricingPoint.siret,
                venueName=pricing_link.pricingPoint.publicName,
            )
    return None


class GetVenueResponseModel(HttpBodyModel):
    isVirtual: bool
    name: str
    bannerUrl: str | None = None
    contact: offerers_schemas.VenueContactModelV2 | None = None
    description: str | None = pydantic_v2.Field(max_length=1000)
    externalAccessibilityData: acceslibre_serializers.ExternalAccessibilityDataModelV2 | None = None
    externalAccessibilityUrl: str | None = None
    externalAccessibilityId: str | None = None
    isOpenToPublic: bool
    isPermanent: bool | None = None
    publicName: str
    withdrawalDetails: str | None = None
    activity: offerers_models.DisplayableActivity | None = None
    dateCreated: datetime
    id: int
    bannerMeta: venue_banners_serialize.BannerMetaModel | None = None
    bookingEmail: str | None = None
    comment: str | None = None
    managingOfferer: GetVenueManagingOffererResponseModel
    pricingPoint: venue_finance_serialize.GetVenuePricingPointResponseModel | None = None
    siret: str | None = None
    collectiveDescription: str | None = None
    collectiveStudents: list[educational_models.StudentLevels] | None = None
    collectiveWebsite: str | None = None
    collectiveDomains: list[venue_collective_serialize.GetVenueDomainResponseModel]
    collectiveInterventionArea: list[str] | None = None
    collectiveLegalStatus: venue_collective_serialize.LegalStatusResponseModel | None = None
    collectiveNetwork: list[str] | None = None
    collectiveAccessInformation: str | None = None
    collectivePhone: str | None = None
    collectiveEmail: str | None = None
    lastCollectiveDmsApplication: venue_collective_serialize.DMSApplicationForEAC | None
    hasAdageId: bool
    adageInscriptionDate: datetime | None = None
    hasOffers: bool
    location: address_serialize.LocationResponseModelV2
    hasActiveIndividualOffer: bool
    is_caledonian: bool
    openingHours: opening_hours_schemas.WeekdayOpeningHoursTimespansV2 | None = None
    isActive: bool
    isValidated: bool
    allowedOnAdage: bool
    bankAccountStatus: venue_finance_serialize.SimplifiedBankAccountStatus | None = None
    has_non_free_offers: bool
    has_partner_page: bool
    can_display_highlights: bool
    has_non_draft_offers: bool
    volunteeringUrl: HttpUrlString | None
    audioDisabilityCompliant: bool | None = None
    mentalDisabilityCompliant: bool | None = None
    motorDisabilityCompliant: bool | None = None
    visualDisabilityCompliant: bool | None = None

    @classmethod
    def build(cls, venue: offerers_models.Venue, has_non_free_offers: bool) -> typing.Self:
        external_accessibility_data = None
        external_accessibility_url = None
        external_accessibility_id = None
        if venue.accessibilityProvider:
            external_accessibility_data = (
                acceslibre_serializers.ExternalAccessibilityDataModelV2.from_accessibility_infos(
                    venue.accessibilityProvider.externalAccessibilityData
                )
            )
            external_accessibility_url = venue.accessibilityProvider.externalAccessibilityUrl
            external_accessibility_id = venue.accessibilityProvider.externalAccessibilityId

        opening_hours = opening_hours_api.format_opening_hours_v2(venue.openingHours)

        banner_meta = None
        if venue.bannerUrl:
            if venue.bannerMeta:
                crop_params = venue.bannerMeta.get("crop_params")
                if not crop_params:
                    crop_params = venue_banners_serialize.CropParamsV2()

                banner_meta = venue_banners_serialize.BannerMetaModel(
                    image_credit=None,
                    original_image_url=venue.bannerMeta.get("original_image_url"),
                    crop_params=crop_params,
                )
            else:
                banner_meta = venue_banners_serialize.BannerMetaModel(image_credit=None, original_image_url=None)

        dms_application = venue.last_collective_dms_application
        return cls(
            activity=offerers_models.DisplayableActivity[venue.activity.name]
            if (venue.activity and venue.activity != offerers_models.Activity.NOT_ASSIGNED)
            else None,
            bannerUrl=venue.bannerUrl,
            isVirtual=venue.isVirtual,
            name=venue.name,
            contact=venue.contact,
            description=venue.description,
            externalAccessibilityData=external_accessibility_data,
            externalAccessibilityUrl=external_accessibility_url,
            externalAccessibilityId=external_accessibility_id,
            isOpenToPublic=venue.isOpenToPublic,
            isPermanent=venue.isPermanent,
            publicName=venue.publicName,
            withdrawalDetails=venue.withdrawalDetails,
            dateCreated=venue.dateCreated,
            id=venue.id,
            bannerMeta=banner_meta,
            bookingEmail=venue.bookingEmail,
            comment=venue.comment,
            managingOfferer=venue.managingOfferer,
            pricingPoint=get_current_pricing_point(venue),
            siret=venue.siret,
            collectiveDescription=venue.collectiveDescription,
            collectiveStudents=venue.collectiveStudents,
            collectiveWebsite=venue.collectiveWebsite,
            collectiveDomains=venue.collectiveDomains,
            collectiveInterventionArea=venue.collectiveInterventionArea,
            collectiveLegalStatus=venue.venueEducationalStatus,
            collectiveNetwork=venue.collectiveNetwork,
            collectiveAccessInformation=venue.collectiveAccessInformation,
            collectivePhone=venue.collectivePhone,
            collectiveEmail=venue.collectiveEmail,
            lastCollectiveDmsApplication=venue_collective_serialize.DMSApplicationForEAC.build(
                dms_application, venue_id=venue.id
            )
            if dms_application
            else None,
            hasAdageId=bool(venue.adageId),
            adageInscriptionDate=venue.adageInscriptionDate,
            hasOffers=venue.hasOffers,
            location=address_serialize.LocationResponseModelV2.build(
                offerer_address=venue.offererAddress,
                label=venue.publicName,
                is_venue_location=True,
            ),
            hasActiveIndividualOffer=venue.hasActiveIndividualOffer,
            is_caledonian=venue.is_caledonian,
            openingHours=opening_hours,
            isActive=venue.managingOfferer.isActive,
            isValidated=venue.managingOfferer.isValidated,
            allowedOnAdage=venue.managingOfferer.allowedOnAdage,
            bankAccountStatus=venue_finance_serialize.parse_venue_bank_account_status(venue),
            has_non_free_offers=has_non_free_offers,
            has_partner_page=venue.has_partner_page,
            can_display_highlights=venue.can_display_highlights,
            has_non_draft_offers=venue.has_non_draft_offers,
            volunteeringUrl=venue.volunteeringUrl,
            audioDisabilityCompliant=venue.audioDisabilityCompliant,
            mentalDisabilityCompliant=venue.mentalDisabilityCompliant,
            motorDisabilityCompliant=venue.motorDisabilityCompliant,
            visualDisabilityCompliant=venue.visualDisabilityCompliant,
        )


def validate_volunteering_url(volunteering_url: str | None) -> str | None:
    if not volunteering_url:
        return None

    parsed = urlparse(str(volunteering_url))

    if parsed.netloc.replace("www.", "") != JE_VEUX_AIDER_GOUV_BASE_URL:
        raise PydanticError("Veuillez renseigner une URL provenant de la plateforme jeveuxaider.gouv")

    if not parsed.path.startswith("/organisations"):
        raise PydanticError(
            "Veuillez renseigner l’URL de votre page organisation. Ex : https://www.jeveuxaider.gouv.fr/organisations/exemple"
        )

    return volunteering_url


def empty_to_null(value: str | None, handler: pydantic_v2.ValidatorFunctionWrapHandler) -> str | None:
    if value == "":
        return None
    return handler(value)


class EditVenueBodyModel(HttpBodyModel):
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic | None = None
    culturalDomains: list[str] | None = None
    name: str | None = pydantic_v2.Field(min_length=1, max_length=offerers_schemas.VENUE_NAME_MAX_LENGTH, default=None)
    street: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_ADDRESS_MAX_LENGTH, default=None)
    banId: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_BAN_ID_MAX_LENGTH, default=None)
    siret: str | None = pydantic_v2.Field(min_length=SIRET_LENGTH, max_length=SIRET_LENGTH, default=None)
    latitude: offerers_schemas.CoordinateField | None = pydantic_v2.Field(
        gt=-MAX_LATITUDE, lt=MAX_LATITUDE, default=None
    )
    longitude: offerers_schemas.CoordinateField | None = pydantic_v2.Field(
        gt=-MAX_LONGITUDE, lt=MAX_LONGITUDE, default=None
    )
    bookingEmail: (
        typing.Annotated[
            pydantic_v2.EmailStr,
            pydantic_v2.StringConstraints(max_length=offerers_schemas.BOOKING_EMAIL_MAX_LENGTH),
            pydantic_v2.WrapValidator(empty_to_null),
        ]
        | None
    ) = None
    postalCode: str | None = pydantic_v2.Field(
        min_length=offerers_schemas.VENUE_POSTAL_CODE_MIN_LENGTH,
        max_length=offerers_schemas.VENUE_POSTAL_CODE_MAX_LENGTH,
        default=None,
    )
    inseeCode: str | None = pydantic_v2.Field(
        min_length=offerers_schemas.VENUE_INSEE_CODE_MIN_LENGTH,
        max_length=offerers_schemas.VENUE_INSEE_CODE_MAX_LENGTH,
        default=None,
    )
    city: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_CITY_MAX_LENGTH, default=None)
    publicName: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_PUBLIC_NAME_MAX_LENGTH, default=None)
    comment: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_COMMENT_MAX_LENGTH, default=None)
    venueLabelId: int | None = None
    withdrawalDetails: str | None = pydantic_v2.Field(
        max_length=offerers_schemas.VENUE_WITHDRAWAL_DETAILS_MAX_LENGTH, default=None
    )
    isAccessibilityAppliedOnAllOffers: bool | None = None
    isManualEdition: bool | None = None
    description: str | None = pydantic_v2.Field(max_length=offerers_schemas.VENUE_DESCRIPTION_MAX_LENGTH, default=None)
    contact: offerers_schemas.VenueContactModelV2 | None = None
    openingHours: opening_hours_schemas.WeekdayOpeningHoursTimespansV2 | None = None
    isOpenToPublic: bool | None = None
    volunteeringUrl: typing.Annotated[HttpUrlString, pydantic_v2.AfterValidator(validate_volunteering_url)] | None = (
        None
    )
    audioDisabilityCompliant: bool | None = None
    mentalDisabilityCompliant: bool | None = None
    motorDisabilityCompliant: bool | None = None
    visualDisabilityCompliant: bool | None = None


class VenueListItemLiteResponseModel(HttpBodyModel):
    id: int
    location: address_serialize.LocationResponseModelV2
    managingOffererId: int
    publicName: str

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> "VenueListItemLiteResponseModel":
        return cls(
            id=venue.id,
            location=cls._build_address(venue),
            managingOffererId=venue.managingOffererId,
            publicName=venue.publicName,
        )

    @classmethod
    def _build_address(cls, venue: offerers_models.Venue) -> address_serialize.LocationResponseModelV2:
        return address_serialize.LocationResponseModelV2.build(
            offerer_address=venue.offererAddress,
            label=venue.publicName,
            is_venue_location=True,
        )


class GetVenueListLiteResponseModel(HttpBodyModel):
    venues: list[VenueListItemLiteResponseModel]
    venues_with_pending_validation: list[VenueListItemLiteResponseModel]

    @classmethod
    def build(
        cls,
        venues: typing.Collection[offerers_models.Venue],
        with_pending_validation: typing.Collection[offerers_models.Venue],
    ) -> "GetVenueListLiteResponseModel":
        return cls(
            venues=[VenueListItemLiteResponseModel.build(venue) for venue in venues],
            venues_with_pending_validation=[
                VenueListItemLiteResponseModel.build(venue) for venue in with_pending_validation
            ],
        )


class VenueListQueryModel(HttpQueryParamsModel):
    validated: typing.Annotated[bool, pydantic_v2.BeforeValidator(string_to_boolean)] | None = None
    active_offerers_only: typing.Annotated[bool, pydantic_v2.BeforeValidator(string_to_boolean)] | None = None
    offerer_id: int | None = None


class GetOffersStatsResponseModel(HttpBodyModel):
    published_public_offers: int
    published_educational_offers: int
    pending_public_offers: int
    pending_educational_offers: int


# TODO(pydantic_v2): remove this serializer once ListOffersOfferResponseModel is migrated
class ListOffersVenueResponseModel(BaseModel):
    id: int
    isVirtual: bool
    name: str
    offererName: str
    publicName: str
    departementCode: str | None


class ListOffersVenueResponseModelV2(HttpBodyModel):
    id: int
    isVirtual: bool
    name: str
    offererName: str
    publicName: str
    departementCode: str

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> typing.Self:
        return cls(
            id=venue.id,
            isVirtual=venue.isVirtual,
            name=venue.name,
            offererName=venue.managingOfferer.name,
            publicName=venue.publicName,
            departementCode=venue.offererAddress.address.departmentCode,
        )


class GetVenueAddressesWithOffersOption(enum.Enum):
    INDIVIDUAL_OFFERS_ONLY = "INDIVIDUAL_OFFERS_ONLY"
    COLLECTIVE_OFFERS_ONLY = "COLLECTIVE_OFFERS_ONLY"
    COLLECTIVE_OFFER_TEMPLATES_ONLY = "COLLECTIVE_OFFER_TEMPLATES_ONLY"


class GetVenueAddressesQueryModel(HttpBodyModel):
    withOffersOption: GetVenueAddressesWithOffersOption


class GetVenueAddressResponseModel(HttpBodyModel):
    id: int
    addressId: int
    label: str | None
    venueId: int
    venueName: str | None
    street: str | None
    postalCode: str
    city: str
    departmentCode: str | None


class GetVenueAddressesResponseModel(RootModel):
    root: list[GetVenueAddressResponseModel]
