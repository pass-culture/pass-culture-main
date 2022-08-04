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
    def validate_phone_number(cls, phone_number: str) -> str:  # pylint: disable=no-self-argument
        if phone_number is None:
            return phone_number

        try:
            return phone_number_utils.ParsedPhoneNumber(phone_number, "FR").phone_number
        except Exception:
            raise ValueError(f"numéro de téléphone invalide: {phone_number}")

    @validator("website")
    def validate_website_url(cls, website: str) -> str:  # pylint: disable=no-self-argument
        pattern = r"^(?:http(s)?:\/\/)?[\w.-\.-\.@]+(?:\.[\w\.-\.@]+)+[\w\-\._~:\/?#[\]@%!\$&'\(\)\*\+,;=.]+$"
        if website is None or re.match(pattern, website, re.IGNORECASE):
            return website
        raise ValueError(f"url du site web invalide: {website}")


VenueImageCredit = pydantic.constr(strip_whitespace=True, min_length=1, max_length=255)


class BaseVenueResponse(BaseModel):
    isVirtual: bool
    name: str

    address: str | None
    bannerUrl: str | None
    contact: VenueContactModel | None
    city: str | None
    description: pydantic.constr(max_length=1000, strip_whitespace=True) | None  # type: ignore [valid-type]
    isPermanent: bool | None
    latitude: float | None
    longitude: float | None
    postalCode: str | None
    publicName: str | None
    withdrawalDetails: str | None
