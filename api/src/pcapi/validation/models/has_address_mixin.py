import pcapi.utils.postal_code as postal_code_utils
from pcapi.models.api_errors import ApiErrors
from pcapi.models.has_address_mixin import HasAddressMixin


def validate(obj: HasAddressMixin, api_errors: ApiErrors) -> ApiErrors:
    if obj.postalCode is not None and not postal_code_utils.POSTAL_CODE_REGEX.match(obj.postalCode):
        api_errors.add_error("postalCode", "Ce code postal est invalide")

    return api_errors
