from typing import Dict

from pcapi.core.offers.models import Offer
from pcapi.utils.mailing import build_pc_pro_offer_link


def retrieve_data_for_new_offer_validation_email(offer: Offer) -> Dict:
    return {
        "MJ-TemplateID": 2613721,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "nom_offre": offer.name,
            "nom_lieu": offer.venue.name,
            "lien_offre_pcpro": build_pc_pro_offer_link(offer),
        },
    }
