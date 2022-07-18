from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from io import BytesIO
import typing

from PIL import Image
import pydantic
from pydantic import root_validator
from pydantic import validator

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.validation import VENUE_BANNER_MAX_SIZE
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base
from pcapi.routes.serialization.finance_serialize import BusinessUnitResponseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import string_length_validator
from pcapi.serialization.utils import string_to_boolean_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.image_conversion import CropParam
from pcapi.utils.image_conversion import CropParams


MAX_LONGITUDE = 180
MAX_LATITUDE = 90


class PostVenueBodyModel(BaseModel, AccessibilityComplianceMixin):
    # pydantic constrained types do not work well with Mypy, see https://github.com/samuelcolvin/pydantic/issues/156
    address: pydantic.constr(max_length=200)  # type: ignore
    bookingEmail: pydantic.constr(max_length=120)  # type: ignore
    city: pydantic.constr(max_length=50)  # type: ignore
    comment: str | None
    latitude: float
    longitude: float
    managingOffererId: str
    name: pydantic.constr(max_length=140)  # type: ignore
    publicName: pydantic.constr(max_length=255) | None  # type: ignore
    postalCode: pydantic.constr(min_length=4, max_length=6)  # type: ignore
    siret: pydantic.constr(min_length=14, max_length=14) | None  # type: ignore
    venueLabelId: str | None
    venueTypeCode: str
    withdrawalDetails: str | None
    description: base.VenueDescription | None  # type: ignore
    contact: base.VenueContactModel | None
    # FUTURE-NEW-BANK-DETAILS: remove businessUnitId when new bank details journey is complete
    businessUnitId: int | None

    class Config:
        extra = "forbid"

    @validator("latitude", pre=True)
    def validate_latitude(cls, raw_latitude):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        try:
            latitude = Decimal(raw_latitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        else:
            if not -MAX_LATITUDE < latitude < MAX_LATITUDE:
                raise ValueError("La latitude doit être comprise entre -90.0 et +90.0")
        return raw_latitude

    @validator("longitude", pre=True)
    def validate_longitude(cls, raw_longitude):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        try:
            longitude = Decimal(raw_longitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        else:
            if not -MAX_LONGITUDE < longitude < MAX_LONGITUDE:
                raise ValueError("La longitude doit être comprise entre -180.0 et +180.0")
        return raw_longitude

    @validator("siret", always=True)
    def requires_siret_xor_comment(cls, siret, values):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        """siret is defined after comment, so the validator can access the previously validated value of comment"""
        comment = values.get("comment")
        if (comment and siret) or (not comment and not siret):
            raise ValueError("Veuillez saisir soit un SIRET soit un commentaire")
        return siret


# FUTURE-NEW-BANK-DETAILS: delete when new bank details journey is complete
class VenueResponseModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

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
    address: str | None
    bic: str | None
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: datetime | None
    demarchesSimplifieesApplicationId: str | None
    fieldsUpdated: list[str]
    iban: str | None
    id: str
    idAtProviders: str | None
    isValidated: bool
    lastProviderId: str | None
    name: str
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: str | None

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class BannerMetaModel(BaseModel):
    image_credit: base.VenueImageCredit | None  # type: ignore [valid-type]
    original_image_url: str | None
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
    id: str
    dateCreated: datetime
    isValidated: bool
    managingOffererId: str
    nonHumanizedId: int

    bannerMeta: BannerMetaModel | None
    bic: str | None
    bookingEmail: str | None
    businessUnitId: int | None
    businessUnit: BusinessUnitResponseModel | None
    comment: str | None
    dateModifiedAtLastProvider: datetime | None
    demarchesSimplifieesApplicationId: str | None
    departementCode: str | None
    dmsToken: str | None
    fieldsUpdated: list[str]
    iban: str | None
    idAtProviders: str | None
    isBusinessUnitMainVenue: bool | None
    lastProviderId: str | None
    managingOfferer: GetVenueManagingOffererResponseModel
    pricingPoint: GetVenuePricingPointResponseModel | None
    reimbursementPointId: int | None
    siret: str | None
    venueLabelId: str | None
    venueTypeCode: offerers_models.VenueTypeCode | None
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

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

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
        venue.venueTypeCode = venue.venueTypeCode.name if venue.venueTypeCode else None  # type: ignore [attr-defined]
        venue.nonHumanizedId = venue.id
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

        venue.collectiveLegalStatus = venue.venueEducationalStatus
        return super().from_orm(venue)


class GetCollectiveVenueResponseModel(BaseModel):
    id: str
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

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "GetCollectiveVenueResponseModel":
        venue.collectiveLegalStatus = venue.venueEducationalStatus
        return super().from_orm(venue)


class EditVenueBodyModel(BaseModel, AccessibilityComplianceMixin):
    name: pydantic.constr(max_length=140) | None  # type: ignore
    address: pydantic.constr(max_length=200) | None  # type: ignore
    siret: pydantic.constr(min_length=14, max_length=14) | None  # type: ignore
    latitude: float | str | None
    longitude: float | str | None
    bookingEmail: pydantic.constr(max_length=120) | None  # type: ignore
    postalCode: pydantic.constr(min_length=4, max_length=6) | None  # type: ignore
    city: pydantic.constr(max_length=50) | None  # type: ignore
    publicName: pydantic.constr(max_length=255) | None  # type: ignore
    comment: str | None
    venueTypeCode: str | None
    venueLabelId: int | None
    withdrawalDetails: str | None
    isAccessibilityAppliedOnAllOffers: bool | None
    isWithdrawalAppliedOnAllOffers: bool | None
    isEmailAppliedOnAllOffers: bool | None
    description: base.VenueDescription | None  # type: ignore
    contact: base.VenueContactModel | None
    businessUnitId: int | None
    reimbursementPointId: int | None
    collectiveDescription: str | None
    collectiveStudents: list[educational_models.StudentLevels] | None
    collectiveWebsite: str | None
    collectiveDomains: list[int] | None
    collectiveInterventionArea: list[str] | None
    collectiveLegalStatus: int | None
    collectiveNetwork: list[str] | None
    collectiveAccessInformation: str | None
    collectivePhone: str | None
    collectiveEmail: str | None

    _dehumanize_venue_label_id = dehumanize_field("venueLabelId")
    _validate_collectiveDescription = string_length_validator("collectiveDescription", length=500)
    _validate_collectiveWebsite = string_length_validator("collectiveWebsite", length=150)
    _validate_collectiveAccessInformation = string_length_validator("collectiveAccessInformation", length=500)
    _validate_collectivePhone = string_length_validator("collectivePhone", length=50)
    _validate_collectiveEmail = string_length_validator("collectiveEmail", length=150)


class VenueListItemResponseModel(BaseModel, AccessibilityComplianceMixin):
    id: str
    managingOffererId: str
    name: str
    offererName: str
    publicName: str | None
    isVirtual: bool
    bookingEmail: str | None
    withdrawalDetails: str | None
    businessUnitId: int | None
    businessUnit: BusinessUnitResponseModel | None
    siret: str | None
    isBusinessUnitMainVenue: bool | None

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")


class GetVenueListResponseModel(BaseModel):
    venues: list[VenueListItemResponseModel]


class VenueListQueryModel(BaseModel):
    # FIXME (dbaty, 2022-05-04): this is a no-op, remove this argument.
    validated_for_user: bool | None
    validated: bool | None
    active_offerers_only: bool | None
    offerer_id: int | None

    _dehumanize_offerer_id = dehumanize_field("offerer_id")
    _string_to_boolean_validated_for_user = string_to_boolean_field("validated_for_user")
    _string_to_boolean_validated = string_to_boolean_field("validated")
    _string_to_boolean_active_offerers_only = string_to_boolean_field("active_offerers_only")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class VenueBannerContentModel(BaseModel):
    content: pydantic.conbytes(min_length=2, max_length=VENUE_BANNER_MAX_SIZE)  # type: ignore
    image_credit: base.VenueImageCredit | None  # type: ignore

    # cropping parameters must be a % (between 0 and 1) of the original
    # bottom right corner and the original height
    x_crop_percent: CropParam
    y_crop_percent: CropParam
    height_crop_percent: CropParam
    width_crop_percent: CropParam

    class Config:
        extra = pydantic.Extra.forbid
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

        legit_image_types = {"jpg", "jpeg", "png"}
        content_type = image.format.lower()

        if content_type not in legit_image_types:
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
        extra = pydantic.Extra.forbid


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


class AdageCulturalPartners(BaseModel):
    partners: list[AdageCulturalPartner]


class AdageCulturalPartnerResponseModel(BaseModel):
    id: int
    communeLibelle: str | None
    libelle: str
    regionLibelle: str | None

    class Config:
        orm_mode = True


class AdageCulturalPartnersResponseModel(BaseModel):
    partners: list[AdageCulturalPartnerResponseModel]

    class Config:
        orm_mode = True
