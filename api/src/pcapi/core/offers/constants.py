import abc
import enum
import typing

from pcapi.core.finance.utils import CurrencyEnum


MAX_OFFER_NAME_LENGTH: typing.Final = 90
MAX_OFFER_VIDEO_DESCRIPTION_LENGTH: typing.Final = 150

OFFERS_RECAP_LIMIT: typing.Final = 101
OFFERS_PER_PAGE: typing.Final = 10
OFFERS_LIST_TOTAL_MAX: typing.Final = 99
OFFERS_HOMEPAGE_LIMIT: typing.Final = 3


MAX_STOCK_PRICE_IN_XPF: typing.Final = 23865
MAX_STOCK_PRICE_IN_EUR: typing.Final = 300

MAX_STOCK_PRICE_BY_CURRENCY: typing.Final = {
    CurrencyEnum.EUR: MAX_STOCK_PRICE_IN_EUR,
    CurrencyEnum.XPF: MAX_STOCK_PRICE_IN_XPF,
}

CURRENCY_NAME_MAPPING: typing.Final = {
    CurrencyEnum.EUR: "euros",
    CurrencyEnum.XPF: "francs Pacifique",
}

DEFAULT_PRICE_LABEL = "Tarif unique"


MAX_EXPOSURE_EVENTS: typing.Final = 3


class ExposureEventType(str, enum.Enum):
    HIGHLIGHT = "HIGHLIGHT"
    HEADLINE = "HEADLINE"


class BaseFeatures(enum.StrEnum):
    @property
    @abc.abstractmethod
    def display_title(self) -> str: ...


def verify_display_title(cls: type[BaseFeatures]) -> type[BaseFeatures]:
    for member in cls:
        # Ensure the member is in the `TITLES` dict of `display_title` property
        try:
            member.display_title  # noqa: B018
        except KeyError:
            raise ValueError(f"Missing title for feature {member.name}")
    return cls


@verify_display_title
class AudioAccessbilityFeatures(BaseFeatures):
    SUBTITLE_CCAP = "SUBTITLE_CCAP"
    AUDIO_HI = "AUDIO_HI"
    STSME = "STSME"
    BOUCLE_MAG = "BOUCLE_MAG"
    RENFO_SONORE = "RENFO_SONORE"
    AUDITION = "AUDITION"
    SR_TWAVOX = "SR_TWAVOX"
    SR_CINE_ACCESS = "SR_CINE_ACCESS"
    ST_CINEACCESS = "ST_CINE_ACCESS"
    SR_GRETA = "SR_GRETA"
    ST_GRETA = "ST_GRETA"

    @property
    def display_title(self) -> str:
        TITLES = {
            self.SUBTITLE_CCAP: "Sous-titré CCAP",
            self.AUDIO_HI: "Ecoute Assistée",
            self.STSME: "ST-SME",
            self.BOUCLE_MAG: "Boucle Magnétique",
            self.RENFO_SONORE: "Renforcement sonore",
            self.AUDITION: "Accessible aux personnes en situation de handicap auditif",
            self.SR_TWAVOX: "Son renforcé Twavox/Audio Point",
            self.SR_CINE_ACCESS: "Son renforcé CineAccess",
            self.ST_CINEACCESS: "Sous-titres CineAccess",
            self.SR_GRETA: "Son renforcé Greta",
            self.ST_GRETA: "Sous-titres Greta",
        }
        return TITLES[self]


@verify_display_title
class MentalAccessbilityFeatures(BaseFeatures):
    RELAX = "RELAX"
    COGNITIF = "COGNITIF"

    @property
    def display_title(self) -> str:
        TITLES = {
            self.RELAX: "Ciné Relax",
            self.COGNITIF: "Accessible aux personnes en situation de handicap cognitif",
        }
        return TITLES[self]


@verify_display_title
class MotorAccessbilityFeatures(BaseFeatures):
    PMR = "PMR"
    MOBILITE = "MOBILITE"

    @property
    def display_title(self) -> str:
        TITLES = {
            self.PMR: "Accès PMR",
            self.MOBILITE: "Accessible aux personnes en situation de handicap moteur",
        }
        return TITLES[self]


@verify_display_title
class VisualAccessbilityFeatures(BaseFeatures):
    AUDIO_DESCRIPTION = "AUDIO_DESCRIPTION"
    VAST = "VAST"
    VISION = "VISION"
    ADTWAVOX = "AD_TWAVOX"
    AD_CINE_ACCESS = "AD_CINE_ACCESS"
    AD_GRETA = "AD_GRETA"

    @property
    def display_title(self) -> str:
        TITLES = {
            self.AUDIO_DESCRIPTION: "Audio Description",
            self.VAST: "VAST",
            self.VISION: "Accessible aux personnes en situation de handicap visuel",
            self.ADTWAVOX: "Audio Description Twavox/Audio Point",
            self.AD_CINE_ACCESS: "Audio description CineAccess",
            self.AD_GRETA: "Audio description Greta",
        }
        return TITLES[self]


@verify_display_title
class LanguageFeatures(BaseFeatures):
    VF = "VF"
    VO = "VO"
    VOST = "VOST"
    VFO = "VFO"
    VD = "VD"

    @property
    def display_title(self) -> str:
        TITLES = {
            self.VD: "VD",
            self.VF: "VF",
            self.VFO: "VFO",
            self.VO: "VO",
            self.VOST: "VOST",
        }
        return TITLES[self]


@verify_display_title
class SpecialEventFeatures(BaseFeatures):
    PLEIN_AIR = "PLEIN_AIR"
    DRIVE_IN = "DRIVE_IN"
    CINE_CONCERT = "CINE_CONCERT"
    AVANT_PREMIERE = "AVANT_PREMIERE"
    AVANT_PREMIERE_EQUIPE = "AVANT_PREMIERE_EQUIPE"
    CINE_DEBAT = "CINE_DEBAT"
    DERNIERE_PROJECTION = "DERNIERE_PROJECTION"
    SEANCE_UNIQUE = "SEANCE_UNIQUE"
    PREMIERE_PROJECTION = "PREMIERE_PROJECTION"
    RENCONTRE = "RENCONTRE"
    REPLAY = "REPLAY"
    LIVE = "LIVE"
    ATELIER = "ATELIER"
    ANIMATION_15_25 = "ANIMATION_15_25"
    PUBLIC_ADAPTE = "PUBLIC_ADAPTE"
    CINE_CLUB = "CINE_CLUB"
    FESTIVAL = "FESTIVAL"
    CINE_RELAX = "CINE_RELAX"

    @property
    def display_title(self) -> str:
        TITLES = {
            self.PLEIN_AIR: "Plein air",
            self.DRIVE_IN: "Drive-in",
            self.CINE_CONCERT: "Ciné-concert",
            self.AVANT_PREMIERE: "Avant-première",
            self.AVANT_PREMIERE_EQUIPE: "Avant-première équipe",
            self.CINE_DEBAT: "Ciné-débat",
            self.DERNIERE_PROJECTION: "Dernière projection",
            self.SEANCE_UNIQUE: "Séance unique",
            self.PREMIERE_PROJECTION: "Première projection",
            self.RENCONTRE: "Rencontre",
            self.REPLAY: "Rediffusion",
            self.LIVE: "En Direct",
            self.ATELIER: "Ciné-atelier",
            self.ANIMATION_15_25: "Animation 15-25",
            self.PUBLIC_ADAPTE: "Public adapté",
            self.CINE_CLUB: "Ciné-Club",
            self.FESTIVAL: "Festival",
            self.CINE_RELAX: "Ciné Relax",
        }
        return TITLES[self]


@verify_display_title
class AudioFeatures(BaseFeatures):
    ATMOS = "ATMOS"
    SON_IMMERSIF = "SON_IMMERSIF"
    AURO_3D = "AURO_3D"
    DSTX = "DSTX"
    MONO = "MONO"
    DOLBY_31 = "DOLBY_31"
    DOLBY_51 = "DOLBY_51"
    DOLBY_71 = "DOLBY_71"

    @property
    def display_title(self) -> str:
        TITLES = {
            self.ATMOS: "Dolby Atmos",
            self.SON_IMMERSIF: "Son Immersif",
            self.AURO_3D: "Auro-3D",
            self.DSTX: "DTS:X",
            self.MONO: "Mono",
            self.DOLBY_31: "Dolby 3.1",
            self.DOLBY_51: "Dolby 5.1",
            self.DOLBY_71: "Dolby 7.1",
        }
        return TITLES[self]


@verify_display_title
class VideoFeatures(BaseFeatures):
    FOUR_DX = "4DX"
    FOUR_DX_3D = "4DX_3D"
    IMAX = "IMAX"
    IMAX_3D = "IMAX_3D"
    SCREEN_X = "SCREEN_X"
    DOLBY_VISION = "DOLBY_VISION"
    DOLBY_VISION_3D = "DOLBY_VISION_3D"
    TWO_D = "2D"
    THREE_D = "3D"
    FOUR_K = "4K"
    ODYSEE = "ODYSEE"
    SPHERA = "SPHERA"
    HFR = "HFR"
    ICE = "ICE"
    ONYX = "ONYX"
    SEVENTY_MM = "70MM"
    OMNIMAX = "OMNIMAX"
    LASER = "LASER"
    MX_4D = "MX_4D"
    MX_4D_3D = "MX_4D_3D"

    @property
    def display_title(self) -> str:
        TITLES = {
            self.FOUR_DX: "4DX",
            self.FOUR_DX_3D: "4DX 3D",
            self.IMAX: "IMAX",
            self.IMAX_3D: "IMAX3D",
            self.SCREEN_X: "ScreenX",
            self.DOLBY_VISION: "DolbyVision",
            self.DOLBY_VISION_3D: "DolbyVision 3D",
            self.TWO_D: "2D",
            self.THREE_D: "3D",
            self.FOUR_K: "4K",
            self.ODYSEE: "Odyssée",
            self.SPHERA: "Sphera",
            self.HFR: "HFR",
            self.ICE: "ICE",
            self.ONYX: "Onyx",
            self.SEVENTY_MM: "70mm",
            self.OMNIMAX: "Omnimax",
            self.LASER: "Laser",
            self.MX_4D: "MX4D",
            self.MX_4D_3D: "MX4D 3D",
        }
        return TITLES[self]


class OfferAccessibilityEnum(enum.StrEnum):
    LARGE_PRINT = "LARGE_PRINT"


class CreationMode(enum.StrEnum):
    MANUAL = "manual"
    IMPORTED = "imported"
