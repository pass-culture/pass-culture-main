import enum
import typing
from datetime import datetime
from decimal import Decimal
from urllib.parse import urlparse

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
from pcapi.routes.serialization.venue_types_serialize import VenueTypeResponseModel
from pcapi.serialization.utils import string_to_boolean_field
from pcapi.serialization.utils import to_camel
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


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


class GetVenueManagingOffererResponseModel(BaseModel):
    id: int
    isValidated: bool
    name: str
    siren: str

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


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
                # TODO bdalbianco 20/03/26 switch to build when this route is migrated
                venue_collective_serialize.DMSApplicationForEAC.from_orm(collective_ds_application, venue.id)
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
            return venue_finance_serialize.parse_venue_bank_account_status(venue)

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


class GetVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    isVirtual: bool
    name: str
    bannerUrl: str | None
    contact: offerers_schemas.VenueContactModel | None
    description: offerers_schemas.VenueDescription | None
    externalAccessibilityData: acceslibre_serializers.ExternalAccessibilityDataModel | None
    externalAccessibilityUrl: str | None
    externalAccessibilityId: str | None
    isOpenToPublic: bool
    isPermanent: bool | None
    publicName: str
    withdrawalDetails: str | None
    activity: offerers_models.DisplayableActivity | None
    dateCreated: datetime
    id: int
    bannerMeta: venue_banners_serialize.BannerMetaModel | None
    bookingEmail: str | None
    comment: str | None
    managingOfferer: GetVenueManagingOffererResponseModel
    pricingPoint: venue_finance_serialize.GetVenuePricingPointResponseModel | None
    siret: str | None
    venueType: VenueTypeResponseModel
    collectiveDescription: str | None
    collectiveStudents: list[educational_models.StudentLevels] | None
    collectiveWebsite: str | None
    collectiveDomains: list[venue_collective_serialize.GetVenueDomainResponseModel]
    collectiveInterventionArea: list[str] | None
    collectiveLegalStatus: venue_collective_serialize.LegalStatusResponseModel | None
    collectiveNetwork: list[str] | None
    collectiveAccessInformation: str | None
    collectivePhone: str | None
    collectiveEmail: str | None
    collectiveDmsApplications: list[venue_collective_serialize.DMSApplicationForEAC]
    hasAdageId: bool
    adageInscriptionDate: datetime | None
    hasOffers: bool
    location: address_serialize.LocationResponseModel | None
    hasActiveIndividualOffer: bool
    isCaledonian: bool
    openingHours: opening_hours_schemas.WeekdayOpeningHoursTimespans | None
    isActive: bool
    isValidated: bool
    allowedOnAdage: bool
    bankAccountStatus: venue_finance_serialize.SimplifiedBankAccountStatus | None
    hasNonFreeOffers: bool
    hasPartnerPage: bool
    canDisplayHighlights: bool
    hasNonDraftOffers: bool
    volunteeringUrl: str | None = pydantic_v1.Field(...)

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        getter_dict = GetVenueResponseGetterDict

    @validator("bannerMeta")
    @classmethod
    def validate_banner_meta(
        cls, meta: venue_banners_serialize.BannerMetaModel | None, values: dict
    ) -> venue_banners_serialize.BannerMetaModel | None:
        """
        Old venues might have a banner url without banner meta, or an
        incomplete banner meta.
        """
        # do not get a default banner meta object if there is no banner
        if not values["bannerUrl"]:
            return None

        if not meta:
            return venue_banners_serialize.BannerMetaModel()

        return meta


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


class VenueListQueryModel(BaseModel):
    validated: bool | None
    active_offerers_only: bool | None
    offerer_id: int | None

    _string_to_boolean_validated = string_to_boolean_field("validated")
    _string_to_boolean_active_offerers_only = string_to_boolean_field("active_offerers_only")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


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


class GetVenueAddressesResponseModel(RootModel):
    root: list[GetVenueAddressResponseModel]
