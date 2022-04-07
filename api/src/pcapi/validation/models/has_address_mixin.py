import re

from pcapi.models import Model
from pcapi.models.api_errors import ApiErrors


POSTAL_CODE_REGEX = r"^\d[AB0-9]\d{3,4}$"


def validate(model: Model, api_errors: ApiErrors) -> ApiErrors:  # type: ignore [valid-type]
    if model.postalCode is not None and not re.match(POSTAL_CODE_REGEX, model.postalCode):  # type: ignore [attr-defined]
        api_errors.add_error("postalCode", "Ce code postal est invalide")

    return api_errors
