import re
import typing
from typing import Optional

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

    email: Optional[pydantic.EmailStr]
    website: Optional[str]
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

    @validator("website")
    def validate_website_url(cls, website: str) -> str:  # pylint: disable=no-self-argument
        pattern = r"^(?:http(s)?:\/\/)?[\w.-\.-\.@]+(?:\.[\w\.-\.@]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
        if website is None or re.match(pattern, website):
            return website
        raise ValueError(f"url du site web invalide: {website}")


VenueImageCredit = pydantic.constr(strip_whitespace=True, min_length=1, max_length=255)

VenueDescription = pydantic.constr(max_length=1000, strip_whitespace=True)


class BaseVenueResponse(BaseModel):
    isVirtual: bool
    name: str

    address: typing.Optional[str]
    bannerUrl: typing.Optional[str]
    contact: typing.Optional[VenueContactModel]
    city: typing.Optional[str]
    description: typing.Optional[VenueDescription]  # type: ignore
    isPermanent: typing.Optional[bool]
    latitude: typing.Optional[float]
    longitude: typing.Optional[float]
    postalCode: typing.Optional[str]
    publicName: typing.Optional[str]
    withdrawalDetails: typing.Optional[str]
