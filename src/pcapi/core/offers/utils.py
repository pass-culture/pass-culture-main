from pcapi import settings
from pcapi.core.offers.models import Offer
from pcapi.utils.human_ids import humanize


def offer_webapp_link(offer: Offer) -> str:
    return f"{settings.WEBAPP_URL}/offre/details/{humanize(offer.id)}"
