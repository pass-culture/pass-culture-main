import logging
from datetime import datetime

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers.repository import get_venue_by_id
from pcapi.routes.adage_iframe.serialization import offers as serialize_offers
from pcapi.routes.serialization import BaseModel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


def serialize_collective_offer(
    offer: educational_models.CollectiveOffer,
) -> serialize_offers.CollectiveOfferResponseModel:
    offer_venue_id = offer.offerVenue.get("venueId")
    if offer_venue_id:
        offer_venue = get_venue_by_id(offer_venue_id)
    else:
        offer_venue = None

    return serialize_offers.CollectiveOfferResponseModel.build(offer=offer, offerVenue=offer_venue)


def serialize_collective_offer_template(
    offer_template: educational_models.CollectiveOfferTemplate, is_favorite: bool
) -> serialize_offers.CollectiveOfferTemplateResponseModel:
    offer_venue_id = offer_template.offerVenue.get("venueId", None)
    if offer_venue_id:
        offer_venue = get_venue_by_id(offer_venue_id)
    else:
        offer_venue = None

    return serialize_offers.CollectiveOfferTemplateResponseModel.build(
        offer=offer_template, offerVenue=offer_venue, is_favorite=is_favorite
    )


class FavoritesResponseModel(BaseModel):
    favoritesTemplate: list[serialize_offers.CollectiveOfferTemplateResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}
