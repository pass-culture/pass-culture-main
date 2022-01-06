from pcapi.core.offers.models import Offer
from pcapi.core.offers.utils import offer_app_link
from pcapi.core.users.models import User


def build_data_for_offer_app_link(user: User, offer: Offer) -> dict:
    return {
        "MJ-TemplateID": 2826195,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "offer_app_link": offer_app_link(offer),
            "user_first_name": user.firstName,
            "offer_name": offer.name,
            "venue_name": offer.venue.name,
        },
    }
