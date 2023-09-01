import logging

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers.repository import get_venue_by_id
from pcapi.routes.adage_iframe.serialization import offers as serialize_offers
from pcapi.routes.serialization import BaseModel


logger = logging.getLogger(__name__)


def serialize_collective_offer_response_model(
    offer: educational_models.CollectiveOffer, uai: str
) -> serialize_offers.CollectiveOfferResponseModel:
    offer_venue_id = offer.offerVenue.get("venueId")
    if offer_venue_id:
        offer_venue = get_venue_by_id(offer_venue_id)
    else:
        offer_venue = None
    return serialize_offers.CollectiveOfferResponseModel.from_orm(offer=offer, offerVenue=offer_venue, uai=uai)


def serialize_collective_offer_template_response_model(
    offer: educational_models.CollectiveOfferTemplate,
) -> serialize_offers.CollectiveOfferTemplateResponseModel:
    offer_venue_id = offer.offerVenue.get("venueId", None)
    if offer_venue_id:
        offer_venue = get_venue_by_id(offer_venue_id)
    else:
        offer_venue = None
    return serialize_offers.CollectiveOfferTemplateResponseModel.from_orm(offer=offer, offerVenue=offer_venue)


class FavoritesResponseModel(BaseModel):
    favoritesOffer: list[serialize_offers.CollectiveOfferResponseModel]
    favoritesTemplate: list[serialize_offers.CollectiveOfferTemplateResponseModel]
