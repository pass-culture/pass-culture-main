import enum
import re
import typing
from decimal import Decimal
from decimal import InvalidOperation

import pydantic.v1 as pydantic_v1
from pydantic.v1 import validator

from pcapi.core.geography.constants import MAX_LATITUDE
from pcapi.core.geography.constants import MAX_LONGITUDE
from pcapi.core.offerers.models import Target
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.shared.schemas import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import to_camel
from pcapi.routes.shared import validation
from pcapi.utils import phone_number as phone_number_utils


SocialMedia = typing.Literal["facebook", "instagram", "snapchat", "twitter"]
SocialMedias = dict[SocialMedia, pydantic_v1.HttpUrl]


class RequiredStrippedString(pydantic_v1.ConstrainedStr):
    strip_whitespace = True
    min_length = 1


class VenueContactModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
        anystr_strip_whitespace = True
        extra = pydantic_v1.Extra.forbid

    email: pydantic_v1.EmailStr | None
    website: str | None
    phone_number: str | None
    social_medias: SocialMedias | None

    @validator("phone_number")
    def validate_phone_number(cls, phone_number: str) -> str | None:
        if not phone_number:
            return None

        try:
            return phone_number_utils.ParsedPhoneNumber(phone_number).phone_number
        except Exception:
            raise ValueError(f"numéro de téléphone invalide: {phone_number}")

    @validator("website")
    def validate_website_url(cls, website: str) -> str:
        pattern = r"^(?:http(s)?:\/\/)?[\w.-\.-\.@]+(?:\.[\w\.-\.@]+)+[\w\-\._~:\/?#[\]@%!\$&'\(\)\*\+,;=.]+$"
        if website is None or re.match(pattern, website, re.IGNORECASE):
            return website
        raise ValueError(f"url du site web invalide: {website}")


class VenueName(RequiredStrippedString):
    max_length = 140


class VenuePublicName(pydantic_v1.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 255


class VenueDescription(pydantic_v1.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 1000


class VenueBookingEmail(pydantic_v1.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 120


class VenueAddress(RequiredStrippedString):
    max_length = 200


class VenueBanId(pydantic_v1.ConstrainedStr):
    strip_whitespace = True
    max_length = 50


class VenueCity(RequiredStrippedString):
    max_length = 200


class VenueInseeCode(RequiredStrippedString):
    min_length = 4
    max_length = 6


class VenuePostalCode(RequiredStrippedString):
    min_length = 4
    max_length = 6


class VenueSiret(RequiredStrippedString):
    min_length = 14
    max_length = 14


class VenueComment(pydantic_v1.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 500


class VenueWithdrawalDetails(pydantic_v1.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 500


class AddressBodyModel(BaseModel):
    isVenueAddress: bool = False
    isManualEdition: bool = False
    banId: str | None
    city: VenueCity
    inseeCode: VenueInseeCode | None
    label: str | None
    latitude: float | str
    longitude: float | str
    postalCode: VenuePostalCode
    street: VenueAddress

    @validator("city")
    def title_city_when_manually_edited(cls, city: str, values: dict) -> str:
        if values["isManualEdition"] is True:
            return city.title()
        return city

    @validator("latitude", pre=True)
    @classmethod
    def validate_latitude(cls, raw_latitude: str) -> str:
        try:
            latitude = Decimal(raw_latitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        if not -MAX_LATITUDE < latitude < MAX_LATITUDE:
            raise ValueError(f"La latitude doit être comprise entre -{MAX_LATITUDE} et +{MAX_LATITUDE}")
        return raw_latitude

    @validator("longitude", pre=True)
    @classmethod
    def validate_longitude(cls, raw_longitude: str) -> str:
        try:
            longitude = Decimal(raw_longitude)
        except InvalidOperation:
            raise ValueError("Format incorrect")
        if not -MAX_LONGITUDE < longitude < MAX_LONGITUDE:
            raise ValueError(f"La longitude doit être comprise entre -{MAX_LONGITUDE} et +{MAX_LONGITUDE}")
        return raw_longitude


VenueTypeCodeKey = enum.Enum(  # type: ignore[misc]
    "VenueTypeCodeKey",
    {code.name: code.name for code in VenueTypeCode},
)


class GetOffererAddressesWithOffersOption(enum.Enum):
    INDIVIDUAL_OFFERS_ONLY = "INDIVIDUAL_OFFERS_ONLY"
    COLLECTIVE_OFFERS_ONLY = "COLLECTIVE_OFFERS_ONLY"
    COLLECTIVE_OFFER_TEMPLATES_ONLY = "COLLECTIVE_OFFER_TEMPLATES_ONLY"


class PostVenueBodyModel(BaseModel, AccessibilityComplianceMixin):
    address: AddressBodyModel
    bookingEmail: VenueBookingEmail
    comment: VenueComment | None
    isOpenToPublic: bool | None
    managingOffererId: int
    name: VenueName
    publicName: VenuePublicName | None
    siret: VenueSiret | None
    venueLabelId: int | None
    venueTypeCode: str
    withdrawalDetails: VenueWithdrawalDetails | None
    description: VenueDescription | None
    contact: VenueContactModel | None

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


class CreateOffererQueryModel(BaseModel):
    city: str
    latitude: float | None
    longitude: float | None
    name: str
    postalCode: str
    inseeCode: str | None
    siren: str
    street: str | None
    phoneNumber: str | None

    _validate_phone_number = validation.phone_number_validator("phoneNumber", nullable=True)


class SaveNewOnboardingDataQueryModel(BaseModel):
    address: AddressBodyModel
    createVenueWithoutSiret: bool = False
    isOpenToPublic: bool
    publicName: str | None
    siret: str
    target: Target
    token: str
    venueTypeCode: str
    webPresence: str
    phoneNumber: str | None

    _validate_phone_number = validation.phone_number_validator("phoneNumber", nullable=True)

    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True


class OffererMemberStatus(enum.Enum):
    VALIDATED = "validated"
    PENDING = "pending"
