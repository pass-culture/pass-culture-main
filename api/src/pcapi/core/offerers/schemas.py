import enum
import re
import typing
from decimal import Decimal
from decimal import InvalidOperation

import pydantic.v1 as pydantic_v1
from pydantic.v1 import validator

from pcapi.core.geography.constants import MAX_LATITUDE
from pcapi.core.geography.constants import MAX_LONGITUDE
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
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


class BannerMetaModel(typing.TypedDict, total=False):
    image_credit: VenueImageCredit | None
    image_credit_url: str | None
    is_from_google: bool


class VenueTypeCode(enum.Enum):
    ARTISTIC_COURSE = "Cours et pratique artistiques"
    BOOKSTORE = "Librairie"
    CONCERT_HALL = "Musique - Salle de concerts"
    CREATIVE_ARTS_STORE = "Magasin arts créatifs"
    CULTURAL_CENTRE = "Centre culturel"
    DIGITAL = "Offre numérique"
    DISTRIBUTION_STORE = "Magasin de distribution de produits culturels"
    FESTIVAL = "Festival"
    GAMES = "Jeux / Jeux vidéos"
    LIBRARY = "Bibliothèque ou médiathèque"
    MOVIE = "Cinéma - Salle de projections"
    MUSEUM = "Musée"
    MUSICAL_INSTRUMENT_STORE = "Musique - Magasin d’instruments"
    OTHER = "Autre"
    PATRIMONY_TOURISM = "Patrimoine et tourisme"
    PERFORMING_ARTS = "Spectacle vivant"
    RECORD_STORE = "Musique - Disquaire"
    SCIENTIFIC_CULTURE = "Culture scientifique"
    TRAVELING_CINEMA = "Cinéma itinérant"
    VISUAL_ARTS = "Arts visuels, arts plastiques et galeries"

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
