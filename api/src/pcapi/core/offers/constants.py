import enum
import typing

from pcapi.core.finance.utils import CurrencyEnum


MAX_OFFER_NAME_LENGTH: typing.Final = 90
MAX_OFFER_VIDEO_DESCRIPTION_LENGTH: typing.Final = 150

OFFERS_RECAP_LIMIT: typing.Final = 101
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


class AudioAccessbilityFeatures(enum.StrEnum):
    SUBTITLE_CCAP = "SUBTITLE_CCAP"
    AUDIO_HI = "AUDIO_HI"
    STSME = "STSME"
    BOUCLE_MAG = "BOUCLE_MAG"
    RENFO_SONORE = "RENFO_SONORE"
    AUDITION = "AUDITION"


class MentalAccessbilityFeatures(enum.StrEnum):
    RELAX = "RELAX"
    COGNITIF = "COGNITIF"


class MotorAccessbilityFeatures(enum.StrEnum):
    PMR = "PMR"
    MOBILITE = "MOBILITE"


class VisualAccessbilityFeatures(enum.StrEnum):
    AD_GRETA = "AD_GRETA"
    AUDIO_DESCRIPTION = "AUDIO_DESCRIPTION"
    VAST = "VAST"
    VISION = "VISION"


class LanguageFeatures(enum.StrEnum):
    VF = "VF"
    VO = "VO"


class SpecialEventFeatures(enum.StrEnum):
    PLEIN_AIR = "PLEIN_AIR"
    DRIVE_IN = "DRIVE_IN"
    CINE_CONCERT = "CINE_CONCERT"
    AVANT_PREMIERE = "AVANT_PREMIERE"
    AVANT_PREMIERE_EQUIPE = "AVANT_PREMIERE_EQUIPE"
    CINE_DEBAT = "CINE_DEBAT"
    DERNIERE_DIFFUSION = "DERNIERE_DIFFUSION"
    SEANCE_UNIQUE = "SEANCE_UNIQUE"
    PREMIERE_DIFFUSION = "PREMIERE_DIFFUSION"
    RENCONTRE = "RENCONTRE"
    REPLAY = "REPLAY"
    LIVE = "LIVE"
    ATELIER = "ATELIER"
    ANIMATION_15_25 = "ANIMATION_15_25"
    PUBLIC_ADAPTE = "PUBLIC_ADAPTE"
    CINE_CLUB = "CINE_CLUB"
    FESTIVAL = "FESTIVAL"
    CINE_RELAX = "CINE_RELAX"


class AudioFeatures(enum.StrEnum):
    SEVEN_1 = "71"
    ATMOS = "ATMOS"
    SON_IMMERSIF = "SON_IMMERSIF"
    AURO_3D = "AURO_3D"
    DSTX = "DSTX"
    MONO = "MONO"
    DOLBY_31 = "DOLBY_31"
    DOLBY_51 = "DOLBY_51"
    DOLBY_71 = "DOLBY_71"


class VideoFeatures(enum.StrEnum):
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
    ONYX = "ONYX"
    SEVENTY_MM = "70MM"
    OMNIMAX = "OMNIMAX"
    IMMERSIF = "IMMERSIF"
    LASER = "LASER"
    MX_4D = "MX_4D"
    MX_4D_3D = "MX_4D_3D"
