from datetime import datetime

import pytz

from pcapi import settings
from pcapi.core.offers.models import Offer


def offer_app_link(offer: Offer) -> str:
    # This link opens the mobile app if installed, the browser app otherwise
    return f"{settings.WEBAPP_V2_URL}/offre/{offer.id}"


def offer_app_redirect_link(offer: Offer) -> str:
    return f"{settings.WEBAPP_V2_REDIRECT_URL}/offre/{offer.id}"


def as_utc_without_timezone(d: datetime) -> datetime:
    return d.astimezone(pytz.utc).replace(tzinfo=None)
