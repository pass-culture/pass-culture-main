from typing import Dict

from pcapi.models import Offerer


def retrieve_data_for_pro_user_waiting_offerer_validation_email(offerer: Offerer) -> Dict:
    return {
        "MJ-TemplateID": 778329,
        "MJ-TemplateLanguage": True,
        "Vars": {"nom_structure": offerer.name},
    }
