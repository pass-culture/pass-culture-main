import enum
import re
import typing
from decimal import Decimal
from decimal import InvalidOperation

import pydantic.v1 as pydantic_v1
from pydantic.v1 import validator

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils import phone_number as phone_number_utils


MAX_LONGITUDE = 180
MAX_LATITUDE = 90

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


class VenueImageCredit(RequiredStrippedString):
    max_length = 255


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


class VenueBookingEmail(pydantic_v1.EmailStr):
    strip_whitespace = True
    # optional, hence no `min_length`
    max_length = 120

    @classmethod
    def validate(cls, value: str) -> str:
        if value == "":
            return value
        return super().validate(value)


class VenueAddress(RequiredStrippedString):
    max_length = 200


class VenueBanId(pydantic_v1.ConstrainedStr):
    strip_whitespace = True
    max_length = 50


class VenueCity(RequiredStrippedString):
    max_length = 200


class VenueInseeCode(RequiredStrippedString):
    min_length = 5
    max_length = 5


class VenuePostalCode(RequiredStrippedString):
    min_length = 5
    max_length = 5


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


class LocationOnlyOnVenueModel(BaseModel):
    isVenueLocation: bool = True

    @validator("isVenueLocation")
    def validate_is_venue_location(cls, is_venue_location: bool) -> bool:
        if is_venue_location is not True:
            raise ValueError()
        return is_venue_location


class LocationModel(BaseModel):
    isManualEdition: bool = False
    isVenueLocation: bool = False
    banId: str | None
    city: VenueCity
    inseeCode: VenueInseeCode | None
    label: str | None
    latitude: float | str
    longitude: float | str
    postalCode: VenuePostalCode
    street: VenueAddress

    @validator("isVenueLocation")
    def validate_is_venue_location(cls, is_venue_location: bool) -> bool:
        if is_venue_location is not False:
            raise ValueError()
        return is_venue_location

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


class BannerMetaModel(typing.TypedDict, total=False):
    image_credit: VenueImageCredit | None
    image_credit_url: str | None
    is_from_google: bool


# [DEPRECATION NOTICE - ETA T1 2026]
# This typology is to be replaced by Activity (Venue's main business activity) and EducationalDomains (Venue's cultural domains)
# Once activity and domains are implemented and data migrated, this will be deleted
# Keep this enum ordered and with the OTHER value first
class VenueTypeCode(enum.Enum):
    OTHER = "Autre"
    VISUAL_ARTS = "Arts visuels, arts plastiques et galeries"
    LIBRARY = "Bibliothèque ou médiathèque"
    CULTURAL_CENTRE = "Centre culturel"
    MOVIE = "Cinéma - Salle de projections"
    TRAVELING_CINEMA = "Cinéma itinérant"
    ARTISTIC_COURSE = "Cours et pratique artistiques"
    SCIENTIFIC_CULTURE = "Culture scientifique"
    FESTIVAL = "Festival"
    GAMES = "Jeux / Jeux vidéos"
    BOOKSTORE = "Librairie"
    CREATIVE_ARTS_STORE = "Magasin arts créatifs"
    DISTRIBUTION_STORE = "Magasin de distribution de produits culturels"
    RECORD_STORE = "Musique - Disquaire"
    MUSICAL_INSTRUMENT_STORE = "Musique - Magasin d’instruments"
    CONCERT_HALL = "Musique - Salle de concerts"
    MUSEUM = "Musée"
    DIGITAL = "Offre numérique"
    PATRIMONY_TOURISM = "Patrimoine et tourisme"
    PERFORMING_ARTS = "Spectacle vivant"

    # These methods are used by pydantic in order to return the enum name and validate the value
    # instead of returning the enum directly.
    @classmethod
    def __get_validators__(cls) -> typing.Iterator[typing.Callable]:
        yield cls.validate

    @classmethod
    def validate(cls, value: str | enum.Enum) -> str:
        if isinstance(value, enum.Enum):
            value = value.name

        if not hasattr(cls, value):
            raise ValueError(f"{value}: invalide")

        return value


VenueTypeCodeKey = enum.Enum(  # type: ignore[misc]
    "VenueTypeCodeKey",
    {code.name: code.name for code in VenueTypeCode},
)


class GetOffererAddressesWithOffersOption(enum.Enum):
    INDIVIDUAL_OFFERS_ONLY = "INDIVIDUAL_OFFERS_ONLY"
    COLLECTIVE_OFFERS_ONLY = "COLLECTIVE_OFFERS_ONLY"
    COLLECTIVE_OFFER_TEMPLATES_ONLY = "COLLECTIVE_OFFER_TEMPLATES_ONLY"
