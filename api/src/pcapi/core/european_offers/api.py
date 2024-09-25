from datetime import datetime

from pcapi.connectors import openai
from pcapi.core.european_offers import models
from pcapi.models import db
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel


class LangField(BaseModel):
    en: str | None
    fr: str | None
    it: str | None
    pt: str | None


class EuropeanOfferData(ConfiguredBaseModel):
    # description
    imageAlt: LangField | None
    title: LangField | None
    description: LangField | None
    date: datetime | None
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
    # openAI translation
    autoTranslate: bool | None


def create_offer(offerData: EuropeanOfferData) -> models.EuropeanOffer:
    data = offerData.dict()
    auto_translate = data.pop("autoTranslate")
    offer = models.EuropeanOffer(**data)
    if auto_translate:
        translated_title = openai.translate(offerData.title.pt)
        translated_description = openai.translate(offerData.description.pt)
        translated_image_alt = openai.translate(offerData.imageAlt.pt)

        offer.title = translated_title
        offer.description = translated_description
        offer.imageAlt = translated_image_alt

    db.session.add(offer)
    return offer
