from datetime import datetime
import logging

from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel


logger = logging.getLogger(__name__)


class LangField(BaseModel):
    en: str | None
    fr: str | None
    it: str | None


class EuropeanOfferResponse(ConfiguredBaseModel):
    # description
    imageAlt: LangField | None
    title: LangField | None
    description: LangField | None
    date: datetime
    imageUrl: str | None
    # order
    currency: str | None
    price: float
    externalUrl: str | None
    # address
    country: str | None
    street: str | None
    city: str | None
    zipcode: str | None
    latitude: float
    longitude: float
