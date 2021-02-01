from typing import Dict

from pcapi.models import UserOfferer
from pcapi.repository.offerer_queries import find_first_by_user_offerer_id


def retrieve_data_for_offerer_ongoing_attachment_email(user_offerer: UserOfferer) -> Dict:
    offerer = find_first_by_user_offerer_id(user_offerer.id)

    return {
        "MJ-TemplateID": 778749,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "nom_structure": offerer.name,
        },
    }
