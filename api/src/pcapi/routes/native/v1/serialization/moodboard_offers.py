from pcapi.routes.native.v1.serialization.offers import OfferResponse

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
import enum


class Temporality(enum.Enum):
    TODAY = "today"
    CURRENT_WEEK = "current_week"
    EVERYDAY = "everyday"


class Mood(enum.Enum):
    FESTIVE = "festive"
    CHILL = "chill"
    LOVE = "love"
    ADVENTURE = "adventure"


class Theme(enum.Enum):
    ADVENTURE = "adventure"
    CLASSIC = "classic"
    CREATIVE = "creative"
    DARK_MODE = "dark_mode"
    FUN = "fun"
    MYSTERY = "mystery"
    NERD = "nerd"
    ROMANCE = "romance"
    SCARY = "scary"
    SUMMER_VIBE = "summer_vibe"
    


class MoodboardOffersRequest(BaseModel):
    class Config:
        alias_generator = to_camel

    temporality: Temporality
    mood: Mood
    theme: Theme


class MoodboardOffersResponse(BaseModel):
    offers: list[OfferResponse]
