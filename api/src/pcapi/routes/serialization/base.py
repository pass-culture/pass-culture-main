import re
import typing

import pydantic
from pydantic import validator

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils import phone_number as phone_number_utils


SocialMedia = typing.Literal["facebook", "instagram", "snapchat", "twitter"]
SocialMedias = dict[SocialMedia, pydantic.HttpUrl]


class VenueContactModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
        anystr_strip_whitespace = True
        extra = pydantic.Extra.forbid

    email: pydantic.EmailStr | None
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


class RequiredStrippedString(pydantic.ConstrainedStr):
    strip_whitespace = True
    min_length = 1


class VenueImageCredit(RequiredStrippedString):
    max_length = 255


class VenueName(RequiredStrippedString):
    max_length = 140


class VenuePublicName(pydantic.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 255


class VenueDescription(pydantic.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 1000


class VenueBookingEmail(pydantic.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 120


class VenueAddress(RequiredStrippedString):
    max_length = 200


class VenueCity(RequiredStrippedString):
    max_length = 200


class VenuePostalCode(RequiredStrippedString):
    min_length = 4
    max_length = 6


class VenueSiret(RequiredStrippedString):
    min_length = 14
    max_length = 14


class VenueComment(pydantic.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 500


class VenueWithdrawalDetails(pydantic.ConstrainedStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 500


class BaseVenueResponse(BaseModel):
    isVirtual: bool
    name: str

    address: str | None
    bannerUrl: str | None
    contact: VenueContactModel | None
    city: str | None
    description: VenueDescription | None
    isPermanent: bool | None
    latitude: float | None
    longitude: float | None
    postalCode: str | None
    publicName: str | None
    withdrawalDetails: str | None


class ListOffersVenueResponseModel(BaseModel):
    nonHumanizedId: int
    isVirtual: bool
    managingOffererId: str
    name: str
    offererName: str
    publicName: str | None
    departementCode: str | None
