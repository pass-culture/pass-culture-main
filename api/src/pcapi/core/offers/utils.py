from datetime import datetime

import pytz

from pcapi.core.offers.models import Offer
from pcapi.utils.urls import generate_firebase_dynamic_link


def offer_webapp_link(offer: Offer) -> str:
    return generate_firebase_dynamic_link(path=f"offre/{offer.id}", params=None)


def as_utc_without_timezone(d: datetime) -> datetime:
    return d.astimezone(pytz.utc).replace(tzinfo=None)
