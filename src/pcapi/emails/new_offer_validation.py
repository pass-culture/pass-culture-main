from typing import Dict

from pcapi.core.offers.models import Offer
from pcapi.utils.mailing import build_pc_pro_offer_link


def retrieve_data_for_offer_approval_email(offer: Offer) -> Dict:
    return {
        "MJ-TemplateID": 2613721,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "offer_name": offer.name,
            "venue_name": offer.venue.publicName if offer.venue.publicName else offer.venue.name,
            "pc_pro_offer_link": build_pc_pro_offer_link(offer),
        },
    }
