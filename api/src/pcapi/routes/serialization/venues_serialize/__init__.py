import enum
import typing
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import Annotated

import pydantic as pydantic_v2
import pydantic.v1 as pydantic_v1
from PIL import Image
from pydantic import AfterValidator
from pydantic import BeforeValidator
from pydantic import Field
from pydantic import PlainSerializer
from pydantic.v1 import root_validator
from pydantic.v1 import validator

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import utils as geography_utils
from pcapi.core.geography.constants import MAX_LATITUDE
from pcapi.core.geography.constants import MAX_LONGITUDE
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.validation import VENUE_BANNER_MAX_SIZE
from pcapi.core.offers.validation import ACCEPTED_THUMBNAIL_FORMATS
from pcapi.core.opening_hours import api as opening_hours_api
from pcapi.core.opening_hours import schemas as opening_hours_schemas
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixinV2
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization.venue_types_serialize import VenueTypeResponseModel
from pcapi.routes.serialization.venue_types_serialize import VenueTypeResponseModelV2
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.serialization.utils import string_length_validator
from pcapi.serialization.utils import string_to_boolean_field
from pcapi.serialization.utils import to_camel
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.image_conversion import CropParam
from pcapi.utils.image_conversion import CropParams

from . import deprecated  # noqa: F401


class DMSApplicationstatus(enum.Enum):
    ACCEPTED = "accepte"
    DROPPED = "sans_suite"
    BUILDING = "en_construction"
    REFUSED = "refuse"
    INSTRUCTING = "en_instruction"


# NOTE(jbaudet - 02/2026): deprecated. Please use
# DMSApplicationForEACV2 instead (pydantic v2 migration)
class DMSApplicationForEAC(BaseModel):
    venueId: int
    state: DMSApplicationstatus
    procedure: int
    application: int
    lastChangeDate: datetime
    depositDate: datetime
    expirationDate: datetime | None
    buildDate: datetime | None
    instructionDate: datetime | None
    processingDate: datetime | None
    userDeletionDate: datetime | None

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}

    @classmethod
    def from_orm(  # type: ignore[override]
        cls, collective_dms_application: educational_models.CollectiveDmsApplication, venue_id: int
    ) -> "DMSApplicationForEAC":
        collective_dms_application.venueId = venue_id
        return super().from_orm(collective_dms_application)


class DMSApplicationForEACV2(pydantic_v2.BaseModel):
    venueId: int
    state: DMSApplicationstatus
    procedure: int
    application: int
    lastChangeDate: Annotated[datetime, PlainSerializer(format_into_utc_date)]
    depositDate: Annotated[datetime, PlainSerializer(format_into_utc_date)]
    expirationDate: Annotated[datetime, PlainSerializer(format_into_utc_date)] | None
    buildDate: Annotated[datetime, PlainSerializer(format_into_utc_date)] | None
    instructionDate: Annotated[datetime, PlainSerializer(format_into_utc_date)] | None
    processingDate: Annotated[datetime, PlainSerializer(format_into_utc_date)] | None
    userDeletionDate: Annotated[datetime, PlainSerializer(format_into_utc_date)] | None

    @classmethod
    def build(
        cls, application: educational_models.CollectiveDmsApplication, venue: offerers_models.Venue
    ) -> "DMSApplicationForEACV2":
        return cls(
            venueId=venue.id,
            state=application.state,
            procedure=application.procedure,
            application=application.application,
            lastChangeDate=application.lastChangeDate,
            depositDate=application.depositDate,
            expirationDate=application.expirationDate,
            processingDate=application.processingDate,
            userDeletionDate=application.userDeletionDate,
            buildDate=application.buildDate,
            instructionDate=application.instructionDate,
        )


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


class VenueResponseModel(BaseModel):
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GetVenueManagingOffererResponseModel(pydantic_v2.BaseModel):
    id: int
    isValidated: bool
    name: str
    siren: str


# TODO(jbaudet - 02/2026): deprecated, use BannerMetaModelV2 instead.
# Same model, same data... using pydantic v2.
class BannerMetaModel(BaseModel):
    image_credit: offerers_schemas.VenueImageCredit | None = None
    original_image_url: str | None = None
    crop_params: CropParams = CropParams()

    @validator("crop_params", pre=True)
    @classmethod
    def validate_crop_params(cls, raw_crop_params: CropParams | None) -> CropParams:
        """
        Old venues might have a crop_params key with a null value
        """
        if not raw_crop_params:
            return CropParams()
        return raw_crop_params


# NOTE(jbaudet - 02/2026): please remove this pydantic model
# once the original CropParams has been migrated to pydantic v2
# (it's a dataclass, but... it uses a field that is a confloat
# from pydantic v1).
class CropParamsV2(pydantic_v2.BaseModel):
    x_crop_percent: float = Field(0.0, ge=0.0, le=1.0)
    y_crop_percent: float = Field(0.0, ge=0.0, le=1.0)
    height_crop_percent: float = Field(1.0, ge=0.0, le=1.0)
    width_crop_percent: float = Field(1.0, ge=0.0, le=1.0)


ImageCreditConstraint = pydantic_v2.types.StringConstraints(strip_whitespace=True, max_length=255, min_length=1)


class BannerMetaModelV2(pydantic_v2.BaseModel):
    image_credit: Annotated[str, ImageCreditConstraint] | None = None
    original_image_url: str | None = None
    crop_params: CropParamsV2 = CropParamsV2()

    @pydantic_v2.model_validator(mode="before")
    @classmethod
    def parse_crop_params(cls, data: dict) -> dict:
        crop_params = data.get("crop_params")
        if not crop_params:
            data["crop_params"] = CropParamsV2()
        return data


class GetVenuePricingPointResponseModel(pydantic_v2.BaseModel):
    id: int
    siret: str
    venueName: str


# NOTE(jbaudet - 02/2026): deprecated. Please use
# GetVenueDomainResponseModelV2 instead.
class GetVenueDomainResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class GetVenueDomainResponseModelV2(pydantic_v2.BaseModel):
    id: int
    name: str


# NOTE(jbaudet - 02/2026): deprecated. Please use
# LegalStatusResponseModelV2 instead.
class LegalStatusResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class LegalStatusResponseModelV2(pydantic_v2.BaseModel):
    id: int
    name: str


class SimplifiedBankAccountStatus(enum.Enum):
    PENDING = "pending"
    VALID = "valid"
    PENDING_CORRECTIONS = "pending_corrections"


def parse_venue_bank_account_status(venue: offerers_models.Venue) -> SimplifiedBankAccountStatus | None:
    status_enum = finance_models.BankAccountApplicationStatus
    bank_account = venue.current_bank_account

    # TODO(jbaudet - 10/2025): move this code to a more
    # appropriate api/repository/models module once offerers
    # have been replaced by venues. These rules come from the
    # `get_offerer_and_extradata` function.
    if not bank_account or not bank_account.isActive:
        return None

    match bank_account.status:
        case status_enum.ACCEPTED:
            return SimplifiedBankAccountStatus.VALID
        case status_enum.DRAFT | status_enum.ON_GOING:
            return SimplifiedBankAccountStatus.PENDING
        case status_enum.WITH_PENDING_CORRECTIONS:
            return SimplifiedBankAccountStatus.PENDING_CORRECTIONS
        case _:
            return None


class GetVenueResponseGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: typing.Any | None = None) -> typing.Any:
        venue: offerers_models.Venue = self._obj

        if key == "externalAccessibilityData":
            if not venue.accessibilityProvider:
                return None
            accessibility_infos = venue.accessibilityProvider.externalAccessibilityData
            return acceslibre_serializers.ExternalAccessibilityDataModel.from_accessibility_infos(accessibility_infos)
        if key == "externalAccessibilityUrl":
            if not venue.accessibilityProvider:
                return None
            return venue.accessibilityProvider.externalAccessibilityUrl
        if key == "externalAccessibilityId":
            if not venue.accessibilityProvider:
                return None
            return venue.accessibilityProvider.externalAccessibilityId

        if key == "bankAccount":
            return venue.current_bank_account

        if key == "collectiveLegalStatus":
            return venue.venueEducationalStatus

        if key == "hasAdageId":
            return bool(venue.adageId)

        if key == "pricingPoint":
            now = date_utils.get_naive_utc_now()
            for pricing_link in venue.pricing_point_links:
                if pricing_link.timespan.lower <= now and (
                    not pricing_link.timespan.upper or pricing_link.timespan.upper > now
                ):
                    return pricing_link.pricingPoint
            return None

        if key == "location":
            offerer_address = venue.offererAddress
            if not offerer_address:
                return None
            return address_serialize.LocationResponseModel(
                **address_serialize.retrieve_address_info_from_oa(offerer_address),
                label=venue.publicName,
                isVenueLocation=True,
            )

        if key == "collectiveDmsApplications":
            return [
                DMSApplicationForEAC.from_orm(collective_ds_application, venue.id)
                for collective_ds_application in venue.collectiveDmsApplications
            ]

        if key == "isCaledonian":
            return venue.is_caledonian

        if key == "openingHours":
            opening_hours = venue.openingHours
            if opening_hours and isinstance(opening_hours, list):
                return opening_hours_api.format_opening_hours(opening_hours)
            return typing.cast(opening_hours_schemas.WeekdayOpeningHoursTimespans | None, opening_hours)

        if key == "venueType":
            value = venue.venueTypeCode
            label = value.value if value else ""
            return VenueTypeResponseModel(value=value.name if value else "", label=label)

        if key == "isActive":
            return venue.managingOfferer.isActive

        if key == "isValidated":
            return venue.managingOfferer.isValidated

        if key == "allowedOnAdage":
            return venue.managingOfferer.allowedOnAdage

        if key == "bankAccountStatus":
            return parse_venue_bank_account_status(venue)

        if key == "hasNonFreeOffers":
            # avoid some tricky circular import: schemas is not expected
            # to import a related repository module.
            # from pcapi.core.offerers.repository import venues_have_non_free_offers

            # return venue.id in venues_have_non_free_offers([venue.id])
            # FIXME(jbaudet 13/11/2025): use venues_have_non_free_offers once
            # it has been fixed
            return True

        if key == "hasPartnerPage":
            return venue.has_partner_page

        if key == "activity":
            if not venue.activity or venue.activity == offerers_models.Activity.NOT_ASSIGNED:
                return None
            return offerers_models.DisplayableActivity[venue.activity.name]

        if key == "canDisplayHighlights":
            return venue.can_display_highlights

        if key == "hasNonDraftOffers":
            return venue.has_non_draft_offers

        return super().get(key, default)


class GetVenueResponseModel(HttpBodyModel, AccessibilityComplianceMixinV2):
    isVirtual: bool
    name: str
    bannerUrl: str | None
    contact: offerers_schemas.VenueContactModelV2 | None
    description: Annotated[str, pydantic_v2.types.StringConstraints(strip_whitespace=True, max_length=1_000)]
    externalAccessibilityData: acceslibre_serializers.ExternalAccessibilityDataModelV2 | None
    externalAccessibilityUrl: str | None
    externalAccessibilityId: str | None
    isOpenToPublic: bool
    isPermanent: bool | None
    publicName: str
    withdrawalDetails: str | None
    activity: offerers_models.DisplayableActivity | None
    dateCreated: Annotated[datetime, PlainSerializer(format_into_utc_date)]
    id: int
    bannerMeta: BannerMetaModelV2 | None
    bookingEmail: str | None
    comment: str | None
    managingOfferer: GetVenueManagingOffererResponseModel
    # pricingPoint: use venue.publicName
    pricingPoint: GetVenuePricingPointResponseModel | None
    siret: str | None
    venueType: VenueTypeResponseModelV2
    collectiveDescription: str | None
    collectiveStudents: list[educational_models.StudentLevels] | None
    collectiveWebsite: str | None
    collectiveDomains: list[GetVenueDomainResponseModelV2]
    collectiveInterventionArea: list[str] | None
    collectiveLegalStatus: LegalStatusResponseModelV2 | None
    collectiveNetwork: list[str] | None
    collectiveAccessInformation: str | None
    collectivePhone: str | None
    collectiveEmail: str | None
    collectiveDmsApplications: list[DMSApplicationForEACV2]
    hasAdageId: bool
    adageInscriptionDate: Annotated[datetime, PlainSerializer(format_into_utc_date)] | None
    hasOffers: bool
    location: address_serialize.LocationResponseModelV2 | None
    hasActiveIndividualOffer: bool
    isCaledonian: bool
    openingHours: opening_hours_schemas.WeekdayOpeningHoursTimespansV2 | None
    isActive: bool
    isValidated: bool
    allowedOnAdage: bool
    bankAccountStatus: SimplifiedBankAccountStatus | None
    hasNonFreeOffers: bool
    hasPartnerPage: bool
    canDisplayHighlights: bool
    hasNonDraftOffers: bool

    @pydantic_v2.model_validator(mode="before")
    @classmethod
    def validate_banner_meta(cls, values: dict) -> dict:
        """
        Old venues might have a banner url without banner meta, or an
        incomplete banner meta.
        """
        # do not get a default banner meta object if there is no banner
        if not values["bannerUrl"]:
            return values

        if not values.get("bannerMeta"):
            values["bannerMeta"] = BannerMetaModel()

        return values

    @classmethod
    def build_contact(cls, venue: offerers_models.Venue) -> offerers_schemas.VenueContactModelV2 | None:
        if not venue.contact:
            return None
        return offerers_schemas.VenueContactModelV2(
            email=venue.contact.email,
            website=venue.contact.website,
            phone_number=venue.contact.phone_number,
            social_medias=venue.contact.social_medias,
        )

    @classmethod
    def build_banner_meta(cls, venue: offerers_models.Venue) -> BannerMetaModelV2 | None:
        banner_meta = None
        if venue.bannerUrl:
            if venue.bannerMeta:
                banner_meta = BannerMetaModelV2(
                    image_credit=venue.bannerMeta.get("image_credit"),
                    original_image_url=venue.bannerMeta.get("original_image_url"),
                    crop_params=venue.bannerMeta.get("crop_params"),
                )
            else:
                banner_meta = BannerMetaModelV2()

        return banner_meta

    @classmethod
    def build_offerer(cls, venue: offerers_models.Venue) -> GetVenueManagingOffererResponseModel:
        return GetVenueManagingOffererResponseModel(
            id=venue.managingOffererId,
            isValidated=venue.managingOfferer.isValidated,
            name=venue.managingOfferer.name,
            siren=venue.managingOfferer.siren,
        )

    @classmethod
    def build_external_accessibility(cls, venue: offerers_models.Venue) -> tuple:
        if not venue.accessibilityProvider:
            external_accessibility_data = None
            external_accessibility_url = None
            external_accessibility_id = None
        else:
            accessibility_infos = venue.accessibilityProvider.externalAccessibilityData
            external_accessibility_data = (
                acceslibre_serializers.ExternalAccessibilityDataModelV2.from_accessibility_infos(accessibility_infos)
            )

            external_accessibility_url = venue.accessibilityProvider.externalAccessibilityUrl
            external_accessibility_id = venue.accessibilityProvider.externalAccessibilityId

        return external_accessibility_data, external_accessibility_url, external_accessibility_id

    @classmethod
    def build_pricing_point(cls, venue: offerers_models.Venue) -> GetVenuePricingPointResponseModel | None:
        pricing_point = None
        now = date_utils.get_naive_utc_now()
        for pricing_link in venue.pricing_point_links:
            if pricing_link.timespan.lower <= now and (
                not pricing_link.timespan.upper or pricing_link.timespan.upper > now
            ):
                pricing_point = GetVenuePricingPointResponseModel(
                    id=pricing_link.pricingPoint.id,
                    siret=pricing_link.pricingPoint.siret,
                    venueName=pricing_link.pricingPoint.publicName,
                )
        return pricing_point

    @classmethod
    def build_location(cls, venue: offerers_models.Venue) -> address_serialize.LocationResponseModelV2 | None:
        offerer_address = venue.offererAddress
        if not offerer_address:
            return None
        else:
            return address_serialize.LocationResponseModelV2.build(
                offerer_address,
                label=venue.publicName,
                is_venue_location=True,
            )

    @classmethod
    def build_collective_dms_applications(cls, venue: offerers_models.Venue) -> list[DMSApplicationForEACV2]:
        return [
            DMSApplicationForEACV2.build(collective_ds_application, venue)
            for collective_ds_application in venue.collectiveDmsApplications
        ]

    @classmethod
    def build_opening_hours(cls, venue: offerers_models.Venue) -> dict:
        raw_opening_hours = venue.openingHours
        if isinstance(raw_opening_hours, list):
            opening_hours = opening_hours_api.format_opening_hours(raw_opening_hours)
        else:
            opening_hours = typing.cast(opening_hours_schemas.WeekdayOpeningHoursTimespans | None, raw_opening_hours)

        # TODO(jbaudet - 02/2026): remove this cast when
        # WeekdayOpeningHoursTimespans has been migrated to pydantic v2.
        # Both models accept the same inputs but in terms of types they
        # are different. This is why casting the data that could come
        # from format_opening_hours (which returns a v1 model) is
        # needed.
        return opening_hours.dict()

    @classmethod
    def build_venue_type(cls, venue: offerers_models.Venue) -> VenueTypeResponseModelV2:
        venue_type_value = venue.venueTypeCode
        venue_type_label = venue_type_value.value if venue_type_value else ""
        return VenueTypeResponseModelV2(value=venue_type_value.name if venue_type_value else "", label=venue_type_label)

    @classmethod
    def build_activity(cls, venue: offerers_models.Venue) -> offerers_models.DisplayableActivity | None:
        if not venue.activity or venue.activity == offerers_models.Activity.NOT_ASSIGNED:
            return None
        else:
            return offerers_models.DisplayableActivity[venue.activity.name]

    @classmethod
    def build_collective_domains(cls, venue: offerers_models.Venue) -> list[GetVenueDomainResponseModelV2]:
        return [GetVenueDomainResponseModelV2(id=domain.id, name=domain.name) for domain in venue.collectiveDomains]

    @classmethod
    def build_collective_legal_status(cls, venue: offerers_models.Venue) -> LegalStatusResponseModelV2 | None:
        if not venue.venueEducationalStatus:
            return None
        return LegalStatusResponseModelV2(
            id=venue.venueEducationalStatus.id,
            name=venue.venueEducationalStatus.name,
        )

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> "GetVenueResponseModel":
        contact = cls.build_contact(venue)
        banner_meta = cls.build_banner_meta(venue)
        offerer = cls.build_offerer(venue)
        external_accessibility_data, external_accessibility_url, external_accessibility_id = (
            cls.build_external_accessibility(venue)
        )
        pricing_point = cls.build_pricing_point(venue)
        location = cls.build_location(venue)
        collective_dms_applications = cls.build_collective_dms_applications(venue)
        opening_hours = cls.build_opening_hours(venue)
        venue_type = cls.build_venue_type(venue)
        activity = cls.build_activity(venue)
        collective_domains = cls.build_collective_domains(venue)
        collective_legal_status = cls.build_collective_legal_status(venue)

        return cls(
            audioDisabilityCompliant=venue.audioDisabilityCompliant,
            motorDisabilityCompliant=venue.motorDisabilityCompliant,
            mentalDisabilityCompliant=venue.mentalDisabilityCompliant,
            visualDisabilityCompliant=venue.visualDisabilityCompliant,
            isVirtual=venue.isVirtual,
            name=venue.name,
            bannerUrl=venue.bannerUrl,
            contact=contact,
            description=venue.description,
            externalAccessibilityData=external_accessibility_data,
            externalAccessibilityUrl=external_accessibility_url,
            externalAccessibilityId=external_accessibility_id,
            collectiveLegalStatus=collective_legal_status,
            hasAdageId=bool(venue.adageId),
            pricingPoint=pricing_point,
            location=location,
            collectiveDmsApplications=collective_dms_applications,
            isCaledonian=venue.is_caledonian,
            openingHours=opening_hours,
            venueType=venue_type,
            isActive=venue.managingOfferer.isActive,
            isValidated=venue.managingOfferer.isValidated,
            allowedOnAdage=venue.managingOfferer.allowedOnAdage,
            bankAccountStatus=parse_venue_bank_account_status(venue),
            # return venue.id in venues_have_non_free_offers([venue.id])
            # FIXME(jbaudet 13/11/2025): use venues_have_non_free_offers once
            # it has been fixed
            hasNonFreeOffers=True,
            hasPartnerPage=venue.has_partner_page,
            activity=activity,
            canDisplayHighlights=venue.can_display_highlights,
            hasNonDraftOffers=venue.has_non_draft_offers,
            isOpenToPublic=venue.isOpenToPublic,
            isPermanent=venue.isPermanent,
            publicName=venue.publicName,
            withdrawalDetails=venue.withdrawalDetails,
            dateCreated=venue.dateCreated,
            id=venue.id,
            bannerMeta=banner_meta,
            bookingEmail=venue.bookingEmail,
            comment=venue.comment,
            managingOfferer=offerer,
            siret=venue.siret,
            collectiveDescription=venue.collectiveDescription,
            collectiveStudents=venue.collectiveStudents,
            collectiveWebsite=venue.collectiveWebsite,
            collectiveDomains=collective_domains,
            collectiveInterventionArea=venue.collectiveInterventionArea,
            collectiveNetwork=venue.collectiveNetwork,
            collectiveAccessInformation=venue.collectiveAccessInformation,
            collectivePhone=venue.collectivePhone,
            collectiveEmail=venue.collectiveEmail,
            adageInscriptionDate=venue.adageInscriptionDate,
            hasOffers=venue.hasOffers,
            hasActiveIndividualOffer=venue.hasActiveIndividualOffer,
        )


class GetCollectiveVenueResponseModel(BaseModel):
    collectiveDescription: str | None
    collectiveStudents: list[educational_models.StudentLevels] | None
    collectiveWebsite: str | None
    collectiveDomains: list[GetVenueDomainResponseModel]
    collectiveInterventionArea: list[str] | None
    collectiveLegalStatus: LegalStatusResponseModel | None
    collectiveNetwork: list[str] | None
    collectiveAccessInformation: str | None
    collectivePhone: str | None
    collectiveEmail: str | None
    siret: str | None

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "GetCollectiveVenueResponseModel":
        venue.collectiveLegalStatus = venue.venueEducationalStatus
        return super().from_orm(venue)


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


class EditVenueCollectiveDataBodyModel(BaseModel):
    collectiveDescription: str | None
    collectiveStudents: list[educational_models.StudentLevels] | None
    collectiveWebsite: str | None
    collectiveDomains: list[int] | None
    collectiveInterventionArea: list[str] | None
    venueEducationalStatusId: int | None
    collectiveNetwork: list[str] | None
    collectiveAccessInformation: str | None
    collectivePhone: str | None
    collectiveEmail: str | None
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic | None

    _validate_collectiveDescription = string_length_validator("collectiveDescription", length=500)
    _validate_collectiveWebsite = string_length_validator("collectiveWebsite", length=150)
    _validate_collectiveAccessInformation = string_length_validator("collectiveAccessInformation", length=500)
    _validate_collectivePhone = string_length_validator("collectivePhone", length=50)
    _validate_collectiveEmail = string_length_validator("collectiveEmail", length=150)

    @validator("collectiveStudents")
    def validate_students(cls, students: list[str]) -> list[educational_models.StudentLevels] | None:
        if not students:
            return []
        return shared_offers.validate_students(students)

    @validator("collectiveInterventionArea")
    def validate_intervention_area(cls, intervention_area: list[str] | None) -> list[str] | None:
        if intervention_area and any(area not in ALL_INTERVENTION_AREA for area in intervention_area):
            raise ValueError("One or more element is not a valid area")

        return intervention_area


class VenueListItemLiteResponseModel(BaseModel):
    id: int
    name: str


class GetVenueListLiteResponseModel(BaseModel):
    venues: list[VenueListItemLiteResponseModel]


class VenueListQueryModel(BaseModel):
    validated: bool | None
    active_offerers_only: bool | None
    offerer_id: int | None

    _string_to_boolean_validated = string_to_boolean_field("validated")
    _string_to_boolean_active_offerers_only = string_to_boolean_field("active_offerers_only")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class VenueBannerContentModel(BaseModel):
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        content: bytes
    else:
        content: pydantic_v1.conbytes(min_length=2, max_length=VENUE_BANNER_MAX_SIZE)
    image_credit: offerers_schemas.VenueImageCredit | None

    # cropping parameters must be a % (between 0 and 1) of the original
    # bottom right corner and the original height
    x_crop_percent: CropParam
    y_crop_percent: CropParam
    height_crop_percent: CropParam
    width_crop_percent: CropParam

    class Config:
        extra = pydantic_v1.Extra.forbid
        anystr_strip_whitespace = True

    @root_validator(pre=True)
    @classmethod
    def validate_banner(cls, values: dict) -> dict:
        """
        Validate content (is not an invalid image) using PIL
        + set and validate content type using image build from previous
          step
        """
        try:
            image = Image.open(BytesIO(values["content"]))
        except Exception:
            raise ValueError("Format de l'image invalide")
        assert image.format is not None  # helps mypy

        content_type = image.format.lower()

        if content_type not in ACCEPTED_THUMBNAIL_FORMATS:
            raise ValueError("Format de l'image invalide")

        return values

    @classmethod
    def from_request(cls, request: typing.Any) -> "VenueBannerContentModel":
        cls.validate_request(request)

        file = request.files["banner"]
        return VenueBannerContentModel(
            content=file.read(VENUE_BANNER_MAX_SIZE),
            image_credit=request.args.get("image_credit"),
            x_crop_percent=request.args.get("x_crop_percent"),
            y_crop_percent=request.args.get("y_crop_percent"),
            height_crop_percent=request.args.get("height_crop_percent"),
            width_crop_percent=request.args.get("width_crop_percent"),
        )

    @classmethod
    def validate_request(cls, request: typing.Any) -> typing.Any:
        """
        If the request has a content_lenght information, use directly to
        avoid reading the whole content to check its size. If not, do not
        consider this a an error: it will be checked later.
        """
        try:
            file = request.files["banner"]
        except (AttributeError, KeyError):
            raise exceptions.InvalidVenueBannerContent("Image manquante")

        if file.content_length and file.content_length > VENUE_BANNER_MAX_SIZE:
            raise exceptions.VenueBannerTooBig(f"Image trop grande, max: {VENUE_BANNER_MAX_SIZE / 1_000}Ko")

        return request

    @property
    def crop_params(self) -> CropParams | None:
        if {self.x_crop_percent, self.y_crop_percent, self.height_crop_percent, self.width_crop_percent} == {None}:
            return None

        return CropParams(
            x_crop_percent=self.x_crop_percent,
            y_crop_percent=self.y_crop_percent,
            height_crop_percent=self.height_crop_percent,
            width_crop_percent=self.width_crop_percent,
        )


class LinkVenueToPricingPointBodyModel(BaseModel):
    pricingPointId: int

    class Config:
        extra = "forbid"


class VenuesEducationalStatusResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        extra = pydantic_v1.Extra.forbid


class VenuesEducationalStatusesResponseModel(BaseModel):
    statuses: list[VenuesEducationalStatusResponseModel]


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
