import enum
import typing
from datetime import datetime
from decimal import Decimal
from urllib.parse import urlparse

import pydantic
import pydantic.v1 as pydantic_v1
from pydantic import RootModel
from pydantic.v1 import validator

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.educational import models as educational_models
from pcapi.core.geography import utils as geography_utils
from pcapi.core.geography.constants import MAX_LATITUDE
from pcapi.core.geography.constants import MAX_LONGITUDE
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.constants import JE_VEUX_AIDER_GOUV_BASE_URL
from pcapi.core.opening_hours import api as opening_hours_api
from pcapi.core.opening_hours import schemas as opening_hours_schemas
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import venue_banners_serialize
from pcapi.routes.serialization import venue_collective_serialize
from pcapi.routes.serialization import venue_finance_serialize
from pcapi.serialization.utils import to_camel
from pcapi.utils import date as date_utils


# deja fait
class PostVenueBodyModel(BaseModel, AccessibilityComplianceMixin):
    activity: offerers_models.Activity | None
    address: address_serialize.LocationBodyModel
    bookingEmail: offerers_schemas.VenueBookingEmail
    culturalDomains: list[str] | None
    comment: offerers_schemas.VenueComment | None
    isOpenToPublic: bool | None
    managingOffererId: int
    name: offerers_schemas.VenueName
    publicName: offerers_schemas.VenuePublicName | None
    siret: offerers_schemas.VenueSiret | None
    venueLabelId: int | None
    withdrawalDetails: offerers_schemas.VenueWithdrawalDetails | None
    description: offerers_schemas.VenueDescription | None
    contact: offerers_schemas.VenueContactModel | None

    class Config:
        extra = "forbid"

    @validator("siret", always=True)
    @classmethod
    def requires_siret_xor_comment(cls, siret: str | None, values: dict) -> str | None:
        """siret is defined after comment, so the validator can access the previously validated value of comment"""
        comment = values.get("comment")
        if (comment and siret) or (not comment and not siret):
            raise ValueError("Veuillez saisir soit un SIRET soit un commentaire")
        return siret


class GetVenueManagingOffererResponseModel(HttpBodyModel):
    id: int
    isValidated: bool
    name: str
    siren: str


# TODO: move this elsewhere
def get_current_pricing_point(venue: offerers_models.Venue) -> offerers_models.Venue | None:
    now = date_utils.get_naive_utc_now()
    for pricing_link in venue.pricing_point_links:
        if pricing_link.timespan.lower <= now and (
            not pricing_link.timespan.upper or pricing_link.timespan.upper > now
        ):
            return pricing_link.pricingPoint
    return None


# TODO(PydanticV2): remove after pydantic migration to V2 is finished
class LocationResponseModel(address_serialize.LocationResponseModelV2):
    pass


class GetVenueResponseModel(HttpBodyModel):
    # TODO a evaluer
    model_config = pydantic.ConfigDict(extra="ignore")

    isVirtual: bool
    name: str
    bannerUrl: str | None = None
    contact: offerers_schemas.VenueContactModelV2 | None = None
    description: str | None = pydantic.Field(max_length=1000)
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
    bannerMeta: venue_banners_serialize.BannerMetaModelV2 | None = None
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
    collectiveDmsApplications: list[venue_collective_serialize.DMSApplicationForEAC]
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
    has_non_free_offers: bool = True  # FIXME(jbaudet 13/11/2025): use venues_have_non_free_offers once fixed
    has_partner_page: bool
    can_display_highlights: bool
    has_non_draft_offers: bool
    volunteeringUrl: str | None = pydantic.Field(...)
    audioDisabilityCompliant: bool | None = None
    mentalDisabilityCompliant: bool | None = None
    motorDisabilityCompliant: bool | None = None
    visualDisabilityCompliant: bool | None = None

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> typing.Self:
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

        if venue.openingHours and isinstance(venue.openingHours, list):
            opening_hours = opening_hours_api.format_opening_hours_v2(venue.openingHours)
        else:
            opening_hours = typing.cast(opening_hours_schemas.WeekdayOpeningHoursTimespansV2, venue.openingHours)

        return cls(
            activity=offerers_models.DisplayableActivity[venue.activity.name] if venue.activity else None,
            bannerUrl=venue.bannerUrl or None,
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
            bannerMeta=venue.bannerMeta or {},
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
            collectiveDmsApplications=[
                venue_collective_serialize.DMSApplicationForEAC.build(collective_ds_application, venue.id)
                for collective_ds_application in venue.collectiveDmsApplications
            ],
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
            bankAccountStatus=venue_finance_serialize.parse_bank_account_status(venue.current_bank_account),
            has_partner_page=venue.has_partner_page,
            can_display_highlights=venue.can_display_highlights,
            has_non_draft_offers=venue.has_non_draft_offers,
            volunteeringUrl=venue.volunteeringUrl,
            audioDisabilityCompliant=venue.audioDisabilityCompliant,
            mentalDisabilityCompliant=venue.mentalDisabilityCompliant,
            motorDisabilityCompliant=venue.motorDisabilityCompliant,
            visualDisabilityCompliant=venue.visualDisabilityCompliant,
        )


class EditVenueBodyModel(BaseModel, AccessibilityComplianceMixin):
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic | None
    culturalDomains: list[str] | None
    name: offerers_schemas.VenueName | None
    street: offerers_schemas.VenueAddress | None
    banId: offerers_schemas.VenueBanId | None
    siret: offerers_schemas.VenueSiret | None
    latitude: Decimal | None
    longitude: Decimal | None
    bookingEmail: offerers_schemas.VenueBookingEmail | None
    postalCode: offerers_schemas.VenuePostalCode | None
    inseeCode: str | None
    city: offerers_schemas.VenueCity | None
    publicName: offerers_schemas.VenuePublicName | None
    comment: offerers_schemas.VenueComment | None
    venueLabelId: int | None
    withdrawalDetails: offerers_schemas.VenueWithdrawalDetails | None
    isAccessibilityAppliedOnAllOffers: bool | None
    isManualEdition: bool | None
    description: offerers_schemas.VenueDescription | None
    contact: offerers_schemas.VenueContactModel | None
    openingHours: opening_hours_schemas.WeekdayOpeningHoursTimespans | None
    isOpenToPublic: bool | None
    volunteeringUrl: pydantic_v1.HttpUrl | None = pydantic_v1.Field(
        example="https://www.jeveuxaider.gouv.fr/organisations/structure-name"
    )

    # TODO: move and rationalize Venue validation after serialization refactoring
    @validator("latitude", pre=True)
    @classmethod
    def check_and_format_latitude(cls, raw_latitude: typing.Any) -> Decimal | None:
        if raw_latitude is None:
            return raw_latitude
        try:
            latitude = geography_utils.format_coordinate(raw_latitude)
        except ValueError:
            raise ValueError("La latitude doit être un nombre")
        if not -MAX_LATITUDE < latitude < MAX_LATITUDE:
            raise ValueError(f"La latitude doit être comprise entre -{MAX_LATITUDE} et +{MAX_LATITUDE}")
        return latitude

    @validator("longitude", pre=True)
    @classmethod
    def check_and_format_longitude(cls, raw_longitude: typing.Any) -> Decimal | None:
        if raw_longitude is None:
            return raw_longitude
        try:
            longitude = geography_utils.format_coordinate(raw_longitude)
        except ValueError:
            raise ValueError("La longitude doit être un nombre")
        if not -MAX_LONGITUDE < longitude < MAX_LONGITUDE:
            raise ValueError(f"La longitude doit être comprise entre -{MAX_LONGITUDE} et +{MAX_LONGITUDE}")
        return longitude

    @validator("bookingEmail", always=True)
    @classmethod
    def validate_booking_email(cls, booking_email: str | None) -> str | None:
        if booking_email == "":
            return None
        return booking_email

    @validator("volunteeringUrl")
    @classmethod
    def validate_volunteering_url(cls, volunteering_url: pydantic_v1.HttpUrl | None) -> pydantic_v1.HttpUrl | None:
        if not volunteering_url:
            return None

        parsed = urlparse(volunteering_url)

        if parsed.netloc.replace("www.", "") != JE_VEUX_AIDER_GOUV_BASE_URL:
            raise exceptions.OffererException(
                {"volunteeringUrl": ["Veuillez renseigner une URL provenant de la plateforme jeveuxaider.gouv"]}
            )

        if not parsed.path.startswith("/organisations"):
            raise exceptions.OffererException(
                {
                    "volunteeringUrl": [
                        "Veuillez renseigner l’URL de votre page organisation. Ex : https://www.jeveuxaider.gouv.fr/organisations/exemple"
                    ]
                }
            )

        return volunteering_url


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

    @classmethod
    def build(cls, venues: list[offerers_models.Venue]) -> "GetVenueListLiteResponseModel":
        return cls(venues=[VenueListItemLiteResponseModel.build(venue) for venue in venues])


class VenueListQueryModel(HttpBodyModel):
    validated: bool | None = None
    active_offerers_only: bool | None = None
    offerer_id: int | None = None


class GetOffersStatsResponseModel(HttpBodyModel):
    published_public_offers: int
    published_educational_offers: int
    pending_public_offers: int
    pending_educational_offers: int


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


class (RootModel):
    root: list[GetVenueAddressResponseModel]
