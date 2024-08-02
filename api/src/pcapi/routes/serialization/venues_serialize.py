from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
import enum
from io import BytesIO
import typing

from PIL import Image
import pydantic.v1 as pydantic_v1
from pydantic.v1 import root_validator
from pydantic.v1 import validator
from pydantic.v1.utils import GetterDict

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.categories import subcategories_v2
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.validation import VENUE_BANNER_MAX_SIZE
from pcapi.core.offers.validation import ACCEPTED_THUMBNAIL_FORMATS
from pcapi.domain.demarches_simplifiees import DMS_TOKEN_PRO_PREFIX
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import base
from pcapi.routes.serialization.finance_serialize import BankAccountResponseModel
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.serialization.utils import string_length_validator
from pcapi.serialization.utils import string_to_boolean_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.image_conversion import CropParam
from pcapi.utils.image_conversion import CropParams


MAX_LONGITUDE = 180
MAX_LATITUDE = 90


class DMSApplicationstatus(enum.Enum):
    ACCEPTED = "accepte"
    DROPPED = "sans_suite"
    BUILDING = "en_construction"
    REFUSED = "refuse"
    INSTRUCTING = "en_instruction"


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
    def from_orm(
        cls, collective_dms_applicaiton: educational_models.CollectiveDmsApplication
    ) -> "DMSApplicationForEAC":
        collective_dms_applicaiton.venueId = collective_dms_applicaiton.venue.id
        return super().from_orm(collective_dms_applicaiton)


class PostVenueBodyModel(BaseModel, AccessibilityComplianceMixin):
    street: base.VenueAddress
    banId: base.VenueBanId | None
    bookingEmail: base.VenueBookingEmail
    city: base.VenueCity
    comment: base.VenueComment | None
    latitude: float
    longitude: float
    managingOffererId: int
    name: base.VenueName
    publicName: base.VenuePublicName | None
    postalCode: base.VenuePostalCode
    siret: base.VenueSiret | None
    venueLabelId: int | None
    venueTypeCode: str
    withdrawalDetails: base.VenueWithdrawalDetails | None
    description: base.VenueDescription | None
    contact: base.VenueContactModel | None

    class Config:
        extra = "forbid"

    @validator("latitude", pre=True)
    @classmethod
    def validate_latitude(cls, raw_latitude: str) -> str:
        try:
            latitude = Decimal(raw_latitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        if not -MAX_LATITUDE < latitude < MAX_LATITUDE:
            raise ValueError("La latitude doit être comprise entre -90.0 et +90.0")
        return raw_latitude

    @validator("longitude", pre=True)
    @classmethod
    def validate_longitude(cls, raw_longitude: str) -> str:
        try:
            longitude = Decimal(raw_longitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        if not -MAX_LONGITUDE < longitude < MAX_LONGITUDE:
            raise ValueError("La longitude doit être comprise entre -180.0 et +180.0")
        return raw_longitude

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


class VenueStatsResponseModel(BaseModel):
    activeBookingsQuantity: int
    validatedBookingsQuantity: int
    activeOffersCount: int
    soldOutOffersCount: int


class GetVenueManagingOffererResponseModel(BaseModel):
    city: str
    dateCreated: datetime
    demarchesSimplifieesApplicationId: str | None
    id: int
    isValidated: bool
    name: str
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: str | None
    street: str | None
    allowedOnAdage: bool

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class BannerMetaModel(BaseModel):
    image_credit: base.VenueImageCredit | None = None
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


class GetVenuePricingPointResponseModel(BaseModel):
    id: int
    siret: str
    venueName: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "GetVenuePricingPointResponseModel":
        venue.venueName = venue.publicName or venue.name
        return super().from_orm(venue)


class GetVenueDomainResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class LegalStatusResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class GetVenueResponseModel(base.BaseVenueResponse, AccessibilityComplianceMixin):
    dateCreated: datetime
    id: int
    bannerMeta: BannerMetaModel | None
    banId: str | None
    bookingEmail: str | None
    comment: str | None
    demarchesSimplifieesApplicationId: str | None
    departementCode: str | None
    dmsToken: str
    managingOfferer: GetVenueManagingOffererResponseModel
    pricingPoint: GetVenuePricingPointResponseModel | None
    reimbursementPointId: int | None
    siret: str | None
    timezone: str
    venueLabelId: int | None
    venueTypeCode: offerers_models.VenueTypeCode
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
    collectiveSubCategoryId: str | None
    collectiveDmsApplications: list[DMSApplicationForEAC]
    hasAdageId: bool
    adageInscriptionDate: datetime | None
    bankAccount: BankAccountResponseModel | None
    isVisibleInApp: bool = True

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}

    @validator("bannerMeta")
    @classmethod
    def validate_banner_meta(cls, meta: BannerMetaModel | None, values: dict) -> BannerMetaModel | None:
        """
        Old venues might have a banner url without banner meta, or an
        incomplete banner meta.
        """
        # do not get a default banner meta object if there is no banner
        if not values["bannerUrl"]:
            return None

        if not meta:
            return BannerMetaModel()

        return meta

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "GetVenueResponseModel":
        # pydantic expects an enum key in order to build it, and therefore
        # does not work when passing directly an enum instance.
        now = datetime.utcnow()
        venue.pricingPoint = None
        for pricing_link in venue.pricing_point_links:
            if pricing_link.timespan.lower > now:
                continue
            if not pricing_link.timespan.upper or pricing_link.timespan.upper > now:
                venue.pricingPoint = pricing_link.pricingPoint

        venue.reimbursementPointId = None
        for reimbursement_link in venue.reimbursement_point_links:
            if reimbursement_link.timespan.lower > now:
                continue
            if not reimbursement_link.timespan.upper or reimbursement_link.timespan.upper > now:
                venue.reimbursementPointId = reimbursement_link.reimbursementPointId
        venue.bankAccount = venue.current_bank_account_link.bankAccount if venue.current_bank_account_link else None
        venue.collectiveLegalStatus = venue.venueEducationalStatus
        venue.dmsToken = DMS_TOKEN_PRO_PREFIX + venue.dmsToken
        venue.hasAdageId = bool(venue.adageId)

        return super().from_orm(venue)


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
    collectiveSubCategoryId: str | None
    siret: str | None

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "GetCollectiveVenueResponseModel":
        venue.collectiveLegalStatus = venue.venueEducationalStatus
        return super().from_orm(venue)


class EditVenueBodyModel(BaseModel, AccessibilityComplianceMixin):
    name: base.VenueName | None
    street: base.VenueAddress | None
    banId: base.VenueBanId | None
    siret: base.VenueSiret | None
    latitude: float | str | None
    longitude: float | str | None
    bookingEmail: base.VenueBookingEmail | None
    postalCode: base.VenuePostalCode | None
    city: base.VenueCity | None
    publicName: base.VenuePublicName | None
    comment: base.VenueComment | None
    venueTypeCode: offerers_models.VenueTypeCode | None
    venueLabelId: int | None
    withdrawalDetails: base.VenueWithdrawalDetails | None
    isAccessibilityAppliedOnAllOffers: bool | None
    isWithdrawalAppliedOnAllOffers: bool | None
    isEmailAppliedOnAllOffers: bool | None
    description: base.VenueDescription | None
    contact: base.VenueContactModel | None
    shouldSendMail: bool | None
    openingHours: list[base.OpeningHoursModel] | None


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
    collectiveSubCategoryId: str | None

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

    @validator("collectiveSubCategoryId")
    @classmethod
    def validate_subcategory_id(cls, subcategory_id: str | None) -> str | None:
        if subcategory_id and not subcategory_id in subcategories_v2.COLLECTIVE_SUBCATEGORIES:
            raise ValueError(f"Must be one of [{list(subcategories_v2.COLLECTIVE_SUBCATEGORIES)}]")
        return subcategory_id


class VenueListItemResponseGetterDict(GetterDict):
    def get(self, key: str, default: typing.Any | None = None) -> typing.Any:
        if key == "address":
            offerer_address = self._obj.offererAddress
            if not offerer_address:
                return None
            data = {
                "id": offerer_address.id,
                "banId": offerer_address.address.banId,
                "inseeCode": offerer_address.address.inseeCode,
                "longitude": offerer_address.address.longitude,
                "latitude": offerer_address.address.latitude,
                "postalCode": offerer_address.address.postalCode,
                "street": offerer_address.address.street,
                "city": offerer_address.address.city,
                "label": self._obj.common_name,
                "isEditable": False,
            }
            return address_serialize.AddressResponseIsEditableModel(**data)
        return super().get(key, default)


class VenueListItemResponseModel(BaseModel, AccessibilityComplianceMixin):
    id: int
    managingOffererId: int
    name: str
    offererName: str
    publicName: str | None
    isVirtual: bool
    bookingEmail: str | None
    withdrawalDetails: str | None
    siret: str | None
    hasCreatedOffer: bool
    collectiveSubCategoryId: str | None
    venueTypeCode: offerers_models.VenueTypeCode
    externalAccessibilityData: acceslibre_serializers.ExternalAccessibilityDataModel | None
    address: address_serialize.AddressResponseIsEditableModel | None

    @classmethod
    def from_orm(
        cls,
        venue: offerers_models.Venue,
        ids_of_venues_with_offers: typing.Iterable[int] = (),
    ) -> "VenueListItemResponseModel":
        venue.offererName = venue.managingOfferer.name
        venue.hasCreatedOffer = venue.id in ids_of_venues_with_offers
        if venue.accessibilityProvider:
            venue.externalAccessibilityData = acceslibre_serializers.ExternalAccessibilityDataModel.from_orm(
                venue.accessibilityProvider.externalAccessibilityData
            )
        return super().from_orm(venue)

    class Config:
        orm_mode = True
        getter_dict = VenueListItemResponseGetterDict


class GetVenueListResponseModel(BaseModel):
    venues: list[VenueListItemResponseModel]


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
    image_credit: base.VenueImageCredit | None

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


class AdageCulturalPartner(BaseModel):
    id: int
    venueId: int | None
    siret: str | None
    regionId: int | None
    academieId: str | None
    statutId: int | None
    labelId: int | None
    typeId: int | None
    communeId: str | None
    libelle: str
    adresse: str | None
    siteWeb: str | None
    latitude: float | None
    longitude: float | None
    statutLibelle: str | None
    labelLibelle: str | None
    typeIcone: str | None
    typeLibelle: str | None
    communeLibelle: str | None
    communeDepartement: str | None
    academieLibelle: str | None
    regionLibelle: str | None
    domaines: str | None
    actif: int | None
    dateModification: datetime
    synchroPass: int | None
    domaineIds: str | None


class AdageCulturalPartners(BaseModel):
    partners: list[AdageCulturalPartner]


class AdageCulturalPartnerResponseModel(BaseModel):
    id: int
    statutId: int | None
    siteWeb: str | None
    domaineIds: list[int]

    @validator("domaineIds", pre=True)
    @classmethod
    def transform_domaine_ids(cls, domaine_ids: str | list[int] | None) -> list[int]:
        if not domaine_ids:
            return []

        if isinstance(domaine_ids, list):
            return domaine_ids

        split_domaine_ids = domaine_ids.split(",")
        ids = []
        for domaine_id in split_domaine_ids:
            if not domaine_id.isdigit():
                raise ValueError("Domaine id must be an integer")
            ids.append(int(domaine_id))

        return ids

    class Config:
        orm_mode = True


class CulturalPartner(BaseModel):
    id: int
    communeLibelle: str | None
    libelle: str
    regionLibelle: str | None

    class Config:
        orm_mode = True


class AdageCulturalPartnersResponseModel(BaseModel):
    partners: list[CulturalPartner]

    class Config:
        orm_mode = True


class VenueOfOffererFromSiretResponseModel(BaseModel):
    id: int
    name: str
    publicName: str | None
    siret: str | None
    isPermanent: bool

    class Config:
        orm_mode = True


class GetVenuesOfOffererFromSiretResponseModel(BaseModel):
    offererName: str | None
    offererSiren: str | None
    venues: list[VenueOfOffererFromSiretResponseModel]
