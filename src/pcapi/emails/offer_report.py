from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Reason
from pcapi.core.users.models import User


def build_offer_report_data(user: User, offer: Offer, reason: str) -> dict:
    return {
        "MJ-TemplateID": 3020502,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "user_id": user.id,
            "offer_id": offer.id,
            "offer_name": offer.name,
            "reason": Reason.get_meta(reason).title,
        },
    }
