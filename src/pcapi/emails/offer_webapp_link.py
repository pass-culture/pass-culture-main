from pcapi import settings
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.utils.human_ids import humanize


def build_data_for_offer_webapp_link(user: User, offer: Offer) -> dict:
    return {
        "MJ-TemplateID": 2826195,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "offer_webapp_link": f"{settings.WEBAPP_URL}/offre/details/{humanize(offer.id)}",
            "user_first_name": user.firstName,
            "offer_name": offer.name,
            "venue_name": offer.venue.name,
        },
    }
