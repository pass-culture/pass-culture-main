from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from io import BytesIO
import typing
from typing import Optional
from typing import Union

from PIL import Image
import pydantic
from pydantic import BaseModel
from pydantic import root_validator
from pydantic import validator

from pcapi.core.offerers.validation import VENUE_BANNER_MAX_SIZE
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import string_to_boolean_field
from pcapi.serialization.utils import to_camel
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils.date import format_into_utc_date


MAX_LONGITUDE = 180
MAX_LATITUDE = 90


SocialMedia = typing.Literal["facebook", "instagram", "snapchat", "twitter"]
SocialMedias = dict[SocialMedia, pydantic.HttpUrl]  # type: ignore


class VenueContactModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
        anystr_strip_whitespace = True
        extra = pydantic.Extra.forbid

    email: Optional[pydantic.EmailStr]
    website: Optional[pydantic.HttpUrl]
    phone_number: Optional[str]
    social_medias: Optional[SocialMedias]

    @validator("phone_number")
    def validate_phone_number(cls, phone_number: str) -> str:  # pylint: disable=no-self-argument
        if phone_number is None:
            return phone_number

        try:
            return phone_number_utils.ParsedPhoneNumber(phone_number, "FR").phone_number
        except Exception:
            raise ValueError(f"numéro de téléphone invalide: {phone_number}")


VenueDescription = pydantic.constr(max_length=1000, strip_whitespace=True)


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
    venueTypeId: str
    withdrawalDetails: Optional[str]
    description: Optional[VenueDescription]  # type: ignore
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    contact: Optional[VenueContactModel]

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


class GetVenueResponseModel(BaseModel):
    address: Optional[str]
    bic: Optional[str]
    bookingEmail: Optional[str]
    city: Optional[str]
    comment: Optional[str]
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    demarchesSimplifieesApplicationId: Optional[str]
    departementCode: Optional[str]
    fieldsUpdated: list[str]
    iban: Optional[str]
    id: str
    idAtProviders: Optional[str]
    isValidated: bool
    isVirtual: bool
    lastProviderId: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    managingOfferer: GetVenueManagingOffererResponseModel
    managingOffererId: str
    name: str
    postalCode: Optional[str]
    publicName: Optional[str]
    siret: Optional[str]
    venueLabelId: Optional[str]
    venueTypeId: Optional[str]
    withdrawalDetails: Optional[str]
    description: Optional[VenueDescription]  # type: ignore
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    contact: Optional[VenueContactModel]

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")
    _humanize_venue_type_id = humanize_field("venueTypeId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


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
    venueTypeId: Optional[int]
    venueLabelId: Optional[int]
    withdrawalDetails: Optional[str]
    isAccessibilityAppliedOnAllOffers: Optional[bool]
    isWithdrawalAppliedOnAllOffers: Optional[bool]
    isEmailAppliedOnAllOffers: Optional[bool]
    description: Optional[VenueDescription]  # type: ignore
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    contact: Optional[VenueContactModel]

    _dehumanize_venue_label_id = dehumanize_field("venueLabelId")
    _dehumanize_venue_type_id = dehumanize_field("venueTypeId")


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
    content_type: pydantic.constr(strip_whitespace=True, to_lower=True, max_length=16)  # type: ignore
    file_name: pydantic.constr(strip_whitespace=True, to_lower=True, min_length=5, max_length=256)  # type: ignore

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
        values["content_type"] = image.format.lower()

        if not values["content_type"] in legit_image_types:
            raise ValueError("Format de l'image invalide")

        return values

    @classmethod
    def from_request(cls, request: typing.Any) -> "VenueBannerContentModel":
        cls.validate_request(request)

        file = request.files["banner"]
        return VenueBannerContentModel(
            content=file.read(VENUE_BANNER_MAX_SIZE),
            file_name=file.filename,
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
