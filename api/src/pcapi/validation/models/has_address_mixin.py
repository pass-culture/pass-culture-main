from pcapi.models import Model
from pcapi.models.api_errors import ApiErrors
import pcapi.utils.postal_code as postal_code_utils


def validate(model: Model, api_errors: ApiErrors) -> ApiErrors:  # type: ignore [valid-type]
    if model.postalCode is not None and not postal_code_utils.POSTAL_CODE_REGEX.match(model.postalCode):  # type: ignore [attr-defined]
        api_errors.add_error("postalCode", "Ce code postal est invalide")

    return api_errors
