from pcapi.routes.native.v1.serialization.offers import OfferResponse

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
import enum


class Temporality(enum.Enum):
    TODAY = "today"


class Mood(enum.Enum):
    FESTIVE = "festive"


class Theme(enum.Enum):
    ADVENTURE = "adventure"


class MoodboardOffersRequest(BaseModel):
    class Config:
        alias_generator = to_camel

    temporality: Temporality
    mood: Mood
    theme: Theme


class MoodboardOffersResponse(BaseModel):
    offers: list[OfferResponse]
