from pcapi.core.offers.models import Offer
from pcapi.utils.human_ids import humanize
from pcapi.utils.urls import get_webapp_url


def offer_webapp_link(offer: Offer) -> str:
    return f"{get_webapp_url()}/offre/details/{humanize(offer.id)}"
