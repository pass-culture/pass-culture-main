from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Reason
from pcapi.core.users.models import User
from pcapi.utils.mailing import build_pc_pro_offer_link


def build_offer_report_data(user: User, offer: Offer, reason: str, custom_reason: str) -> dict:
    reason = Reason.get_meta(reason).title
    if custom_reason:
        reason = f"[{reason}] {custom_reason}"

    return {
        "MJ-TemplateID": 3020502,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "user_id": user.id,
            "offer_id": offer.id,
            "offer_name": offer.name,
            "reason": reason,
            "offer_url": build_pc_pro_offer_link(offer),
        },
    }
