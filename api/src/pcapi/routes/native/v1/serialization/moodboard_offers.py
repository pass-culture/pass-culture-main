from datetime import datetime
import enum

from pcapi.core.categories import subcategories
from pcapi.core.offers import offer_metadata
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.offers.models import Offer, OfferExtraData
from pcapi.core.users.models import ExpenseDomain
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse, OfferResponse, OfferVenueResponse
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


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


class MoodboardOffer(BaseModel):
    @classmethod
    def from_orm(cls, offer: Offer) -> "OfferResponse":
        offer.expense_domains = get_expense_domains(offer)
        offer.isExpired = offer.hasBookingLimitDatetimesPassed
        offer.metadata = offer_metadata.get_metadata_from_offer(offer)

        result = super().from_orm(offer)
        return result

    id: int
    description: str | None
    externalTicketOfficeUrl: str | None
    isReleased: bool
    isDigital: bool
    isDuo: bool
    metadata: offer_metadata.Metadata
    name: str
    subcategoryId: subcategories.SubcategoryIdEnum
    image: OfferImageResponse | None
    venue: OfferVenueResponse
    withdrawalDetails: str | None

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}


class MoodboardOffersResponse(BaseModel):
    offers: list[MoodboardOffer]
