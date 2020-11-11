from pcapi.models import ApiErrors
from pcapi.models.db import Model


def validate(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.isDigital and model.is_offline_only():
        api_errors.add_error(
            "url", f"Une offre de type {model.get_label_from_type_string()} ne peut pas être numérique"
        )

    return api_errors
