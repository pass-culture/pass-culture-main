from pcapi.core.offerers.models import Offerer


def retrieve_data_for_new_offerer_validation_email(offerer: Offerer) -> dict:
    return {
        "MJ-TemplateID": 778723,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "offerer_name": offerer.name,
        },
    }
