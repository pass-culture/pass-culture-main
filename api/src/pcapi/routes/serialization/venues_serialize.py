from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from io import BytesIO
import typing
from typing import Optional
from typing import Union

from PIL import Image
import pydantic
from pydantic import root_validator
from pydantic import validator

from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.validation import VENUE_BANNER_MAX_SIZE
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base
from pcapi.routes.serialization.finance_serialize import BusinessUnitResponseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
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
    comment: Optional[str]
    latitude: float
    longitude: float
    managingOffererId: str
    name: pydantic.constr(max_length=140)  # type: ignore
    publicName: Optional[pydantic.constr(max_length=255)]  # type: ignore
    postalCode: pydantic.constr(min_length=4, max_length=6)  # type: ignore
    siret: Optional[pydantic.constr(min_length=14, max_length=14)]  # type: ignore
    venueLabelId: Optional[str]
    venueTypeCode: str
    withdrawalDetails: Optional[str]
    description: Optional[base.VenueDescription]  # type: ignore
    contact: Optional[base.VenueContactModel]
    # FUTURE-NEW-BANK-DETAILS: remove businessUnitId when new bank details journey is complete
    businessUnitId: Optional[int]

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
    address: Optional[str]
    bic: Optional[str]
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    demarchesSimplifieesApplicationId: Optional[str]
    fieldsUpdated: list[str]
    iban: Optional[str]
    id: str
    idAtProviders: Optional[str]
    isValidated: bool
    lastProviderId: Optional[str]
    name: str
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: Optional[str]

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class BannerMetaModel(BaseModel):
    image_credit: Optional[base.VenueImageCredit]  # type: ignore [valid-type]
    original_image_url: Optional[str]
    crop_params: CropParams = CropParams()

    @validator("crop_params", pre=True)
    @classmethod
    def validate_crop_params(cls, raw_crop_params: Optional[CropParams]) -> CropParams:
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


class GetVenueResponseModel(base.BaseVenueResponse, AccessibilityComplianceMixin):
    id: str
    dateCreated: datetime
    isValidated: bool
    managingOffererId: str
    nonHumanizedId: int

    bannerMeta: Optional[BannerMetaModel]
    bic: Optional[str]
    bookingEmail: Optional[str]
    businessUnitId: Optional[int]
    businessUnit: Optional[BusinessUnitResponseModel]
    comment: Optional[str]
    dateModifiedAtLastProvider: Optional[datetime]
    demarchesSimplifieesApplicationId: Optional[str]
    departementCode: Optional[str]
    dmsToken: Optional[str]
    fieldsUpdated: list[str]
    iban: Optional[str]
    idAtProviders: Optional[str]
    isBusinessUnitMainVenue: Optional[bool]
    lastProviderId: Optional[str]
    managingOfferer: GetVenueManagingOffererResponseModel
    pricingPoint: Optional[GetVenuePricingPointResponseModel]
    reimbursementPointId: Optional[int]
    siret: Optional[str]
    venueLabelId: Optional[str]
    venueTypeCode: Optional[offerers_models.VenueTypeCode]

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}

    @validator("bannerMeta")
    @classmethod
    def validate_banner_meta(cls, meta: Optional[BannerMetaModel], values: dict) -> Optional[BannerMetaModel]:
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
        return super().from_orm(venue)


class EditVenueBodyModel(BaseModel, AccessibilityComplianceMixin):
    name: Optional[pydantic.constr(max_length=140)]  # type: ignore
    address: Optional[pydantic.constr(max_length=200)]  # type: ignore
    siret: Optional[pydantic.constr(min_length=14, max_length=14)]  # type: ignore
    latitude: Optional[Union[float, str]]
    longitude: Optional[Union[float, str]]
    bookingEmail: Optional[pydantic.constr(max_length=120)]  # type: ignore
    postalCode: Optional[pydantic.constr(min_length=4, max_length=6)]  # type: ignore
    city: Optional[pydantic.constr(max_length=50)]  # type: ignore
    publicName: Optional[pydantic.constr(max_length=255)]  # type: ignore
    comment: Optional[str]
    venueTypeCode: Optional[str]
    venueLabelId: Optional[int]
    withdrawalDetails: Optional[str]
    isAccessibilityAppliedOnAllOffers: Optional[bool]
    isWithdrawalAppliedOnAllOffers: Optional[bool]
    isEmailAppliedOnAllOffers: Optional[bool]
    description: Optional[base.VenueDescription]  # type: ignore
    contact: Optional[base.VenueContactModel]
    businessUnitId: Optional[int]
    reimbursementPointId: Optional[int]

    _dehumanize_venue_label_id = dehumanize_field("venueLabelId")


class VenueListItemResponseModel(BaseModel, AccessibilityComplianceMixin):
    id: str
    managingOffererId: str
    name: str
    offererName: str
    publicName: Optional[str]
    isVirtual: bool
    bookingEmail: Optional[str]
    withdrawalDetails: Optional[str]
    businessUnitId: Optional[int]
    businessUnit: Optional[BusinessUnitResponseModel]
    siret: Optional[str]
    isBusinessUnitMainVenue: Optional[bool]

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")


class GetVenueListResponseModel(BaseModel):
    venues: list[VenueListItemResponseModel]


class VenueListQueryModel(BaseModel):
    # FIXME (dbaty, 2022-05-04): this is a no-op, remove this argument.
    validated_for_user: Optional[bool]
    validated: Optional[bool]
    active_offerers_only: Optional[bool]
    offerer_id: Optional[int]

    _dehumanize_offerer_id = dehumanize_field("offerer_id")
    _string_to_boolean_validated_for_user = string_to_boolean_field("validated_for_user")
    _string_to_boolean_validated = string_to_boolean_field("validated")
    _string_to_boolean_active_offerers_only = string_to_boolean_field("active_offerers_only")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class VenueBannerContentModel(BaseModel):
    content: pydantic.conbytes(min_length=2, max_length=VENUE_BANNER_MAX_SIZE)  # type: ignore
    image_credit: Optional[base.VenueImageCredit]  # type: ignore

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
    def crop_params(self) -> Optional[CropParams]:
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
    venueId: int
    siret: int
    regionId: int
    academieId: str
    statutId: int
    labelId: int
    typeId: int
    communeId: str
    libelle: str
    adresse: str
    siteWeb: int
    latitude: float
    longitude: float
    statutLibelle: str
    labelLibelle: str
    typeIcone: str
    typeLibelle: str
    communeLibelle: str
    communeDepartement: str
    academieLibelle: str
    regionLibelle: str
    domaines: str
    actif: int
    dateModification: datetime


class AdageCulturalPartners(BaseModel):
    partners: list[AdageCulturalPartner]


class AdageCulturalPartnerResponseModel(BaseModel):
    id: int
    communeLibelle: str
    libelle: str
    regionLibelle: str

    class Config:
        orm_mode = True


class AdageCulturalPartnersResponseModel(BaseModel):
    partners: list[AdageCulturalPartnerResponseModel]

    class Config:
        orm_mode = True
