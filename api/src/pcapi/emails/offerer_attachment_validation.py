from pcapi.core.offerers.models import Offerer


def retrieve_data_for_offerer_attachment_validation_email(offerer: Offerer) -> dict:
    return {
        "MJ-TemplateID": 778756,
        "MJ-TemplateLanguage": True,
        "Vars": {"nom_structure": offerer.name},
    }
