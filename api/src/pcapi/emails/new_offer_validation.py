from pcapi import settings
from pcapi.core.offers.models import Offer
from pcapi.utils.mailing import build_pc_pro_offer_link


def retrieve_data_for_offer_approval_email(offer: Offer) -> dict:
    return {
        "MJ-TemplateID": 2613721,
        "MJ-TemplateLanguage": True,
        "FromEmail": settings.COMPLIANCE_EMAIL_ADDRESS,
        "Vars": {
            "offer_name": offer.name,
            "venue_name": offer.venue.publicName or offer.venue.name,
            "pc_pro_offer_link": build_pc_pro_offer_link(offer),
        },
    }


def retrieve_data_for_offer_rejection_email(offer: Offer) -> dict:
    return {
        "MJ-TemplateID": 2613942,
        "MJ-TemplateLanguage": True,
        "FromEmail": settings.COMPLIANCE_EMAIL_ADDRESS,
        "Vars": {
            "offer_name": offer.name,
            "venue_name": offer.venue.publicName or offer.venue.name,
            "pc_pro_offer_link": build_pc_pro_offer_link(offer),
        },
    }
