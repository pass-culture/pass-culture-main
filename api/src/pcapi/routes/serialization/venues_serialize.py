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
from typing_extensions import TypedDict

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.validation import VENUE_BANNER_MAX_SIZE
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


class PostVenueBodyModel(BaseModel):
    address: str
    bookingEmail: str
    city: str
    comment: Optional[str]
    latitude: float
    longitude: float
    managingOffererId: str
    name: str
    publicName: Optional[str]
    postalCode: str
    siret: Optional[str]
    venueLabelId: Optional[str]
    venueTypeCode: str
    withdrawalDetails: Optional[str]
    description: Optional[base.VenueDescription]  # type: ignore
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    contact: Optional[base.VenueContactModel]
    businessUnitId: Optional[int]

    class Config:
        extra = "forbid"

    @validator("latitude", pre=True)
    def validate_latitude(cls, raw_latitude):  # pylint: disable=no-self-argument
        try:
            latitude = Decimal(raw_latitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        else:
            if not -MAX_LATITUDE < latitude < MAX_LATITUDE:
                raise ValueError("La latitude doit être comprise entre -90.0 et +90.0")
        return raw_latitude

    @validator("longitude", pre=True)
    def validate_longitude(cls, raw_longitude):  # pylint: disable=no-self-argument
        try:
            longitude = Decimal(raw_longitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        else:
            if not -MAX_LONGITUDE < longitude < MAX_LONGITUDE:
                raise ValueError("La longitude doit être comprise entre -180.0 et +180.0")
        return raw_longitude


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


class BannerMetaModel(TypedDict, total=False):
    image_credit: Optional[str]


class GetVenueResponseModel(base.BaseVenueResponse):
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
    fieldsUpdated: list[str]
    iban: Optional[str]
    idAtProviders: Optional[str]
    isBusinessUnitMainVenue: Optional[bool]
    lastProviderId: Optional[str]
    managingOfferer: GetVenueManagingOffererResponseModel
    siret: Optional[str]
    venueLabelId: Optional[str]
    venueTypeCode: Optional[offerers_models.VenueTypeCode]
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "GetVenueResponseModel":
        # pydantic expects an enum key in order to build it, and therefore
        # does not work when passing directly an enum instance.
        venue.venueTypeCode = venue.venueTypeCode.name if venue.venueTypeCode else None
        venue.nonHumanizedId = venue.id
        return super().from_orm(venue)


class EditVenueBodyModel(BaseModel):
    name: Optional[str]
    address: Optional[str]
    siret: Optional[str]
    latitude: Optional[Union[float, str]]
    longitude: Optional[Union[float, str]]
    bookingEmail: Optional[str]
    postalCode: Optional[str]
    city: Optional[str]
    publicName: Optional[str]
    comment: Optional[str]
    venueTypeCode: Optional[str]
    venueLabelId: Optional[int]
    withdrawalDetails: Optional[str]
    isAccessibilityAppliedOnAllOffers: Optional[bool]
    isWithdrawalAppliedOnAllOffers: Optional[bool]
    isEmailAppliedOnAllOffers: Optional[bool]
    description: Optional[base.VenueDescription]  # type: ignore
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    contact: Optional[base.VenueContactModel]
    businessUnitId: Optional[int]

    _dehumanize_venue_label_id = dehumanize_field("venueLabelId")


class VenueListItemResponseModel(BaseModel):
    id: str
    managingOffererId: str
    name: str
    offererName: str
    publicName: Optional[str]
    isVirtual: bool
    bookingEmail: Optional[str]
    withdrawalDetails: Optional[str]
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    businessUnitId: Optional[int]
    businessUnit: Optional[BusinessUnitResponseModel]
    siret: Optional[str]
    isBusinessUnitMainVenue: Optional[bool]

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")


class GetVenueListResponseModel(BaseModel):
    venues: list[VenueListItemResponseModel]


class VenueListQueryModel(BaseModel):
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
    image_credit: Optional[pydantic.constr(strip_whitespace=True, min_length=1, max_length=255)]  # type: ignore

    # cropping parameters must be a % (between 0 and 1) of the original
    # bottom right corner and the original height
    x_crop_percent: CropParam  # type: ignore
    y_crop_percent: CropParam  # type: ignore
    height_crop_percent: CropParam  # type: ignore

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
            raise ValueError("Image manquante")

        if file.content_length and file.content_length > VENUE_BANNER_MAX_SIZE:
            raise ValueError(f"Image trop grande, max: {VENUE_BANNER_MAX_SIZE / 1_000}Ko")

        return request

    @property
    def crop_params(self) -> Optional[CropParams]:
        if {self.x_crop_percent, self.y_crop_percent, self.height_crop_percent} == {None}:
            return None
        return (self.x_crop_percent, self.y_crop_percent, self.height_crop_percent)
