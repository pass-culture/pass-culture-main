from pcapi.models import UserOfferer
from pcapi.repository.offerer_queries import find_first_by_user_offerer_id


def retrieve_data_for_offerer_attachment_validation_email(user_offerer: UserOfferer) -> dict:
    offerer = find_first_by_user_offerer_id(user_offerer.id)
    return {
        "MJ-TemplateID": 778756,
        "MJ-TemplateLanguage": True,
        "Vars": {"nom_structure": offerer.name},
    }
