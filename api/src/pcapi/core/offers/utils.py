from pcapi import settings
from pcapi.core.offers.models import Offer
from pcapi.models.feature import FeatureToggle
from pcapi.utils.human_ids import humanize
from pcapi.utils.urls import generate_firebase_dynamic_link


def offer_webapp_link(offer: Offer) -> str:
    if FeatureToggle.WEBAPP_V2_ENABLED.is_active():
        return generate_firebase_dynamic_link(path=f"offre/{offer.id}", params=None)
    return f"{settings.WEBAPP_URL}/offre/details/{humanize(offer.id)}"
