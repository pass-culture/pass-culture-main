import enum
import typing

from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base


class VenueTypeCode(enum.Enum):
    ADMINISTRATIVE = "Lieu administratif"
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


class BannerMetaModel(typing.TypedDict, total=False):
    image_credit: base.VenueImageCredit | None
    image_credit_url: str | None
    is_from_google: bool


class VenueAccessibilityModel(BaseModel):
    audioDisability: bool | None
    mentalDisability: bool | None
    motorDisability: bool | None
    visualDisability: bool | None


class VenueResponseGetterDict(base.VenueResponseGetterDict):
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        if key == "venueTypeCode":
            return self._obj.venueTypeCode.name

        if key == "address":
            return self._obj.street

        if key == "accessibility":
            return VenueAccessibilityModel(
                audioDisability=self._obj.audioDisabilityCompliant,
                mentalDisability=self._obj.mentalDisabilityCompliant,
                motorDisability=self._obj.motorDisabilityCompliant,
                visualDisability=self._obj.visualDisabilityCompliant,
            )
        return super().get(key, default)


class VenueResponse(base.BaseVenueResponse):
    id: int
    address: str | None
    accessibility: VenueAccessibilityModel
    venueTypeCode: VenueTypeCodeKey
    bannerMeta: BannerMetaModel | None

    class Config:
        getter_dict = VenueResponseGetterDict
