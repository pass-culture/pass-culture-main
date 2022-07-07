from datetime import datetime

import pytz

from pcapi import settings
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.offers.models import Offer
from pcapi.models.feature import FeatureToggle


def offer_app_link(offer: CollectiveOffer | Offer) -> str:
    # This link opens the mobile app if installed, the browser app otherwise
    return f"{settings.WEBAPP_V2_URL}/offre/{offer.id}"


def offer_app_redirect_link(offer: Offer) -> str:
    if FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION.is_active():
        return f"{settings.WEBAPP_V2_REDIRECT_URL}/offre/{offer.id}"
    return offer_app_link(offer)


def as_utc_without_timezone(d: datetime) -> datetime:
    return d.astimezone(pytz.utc).replace(tzinfo=None)
