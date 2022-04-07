from pcapi.models import Model
from pcapi.models.api_errors import ApiErrors


def validate(model: Model, api_errors: ApiErrors) -> ApiErrors:  # type: ignore [valid-type]
    if model.isDigital and model.is_offline_only:  # type: ignore [attr-defined]
        api_errors.add_error("url", f"Un produit de sous-catégorie {model.subcategoryId} ne peut pas être numérique")  # type: ignore [attr-defined]

    return api_errors
