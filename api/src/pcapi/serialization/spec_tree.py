from typing import Optional

from spectree import Response as SpectreeResponse
from spectree.utils import parse_code


def add_security_scheme(route_function, auth_key: str, scopes: Optional[list[str]] = None):
    """Declare a sufficient security scheme to access the route.
    The 'auth_key' should correspond to a scheme declared in
    the SpecTree initialization of the route's BluePrint.
    """
    if not hasattr(route_function, "requires_authentication"):
        route_function.requires_authentication = []
    route_function.requires_authentication.append({auth_key: scopes or []})


class ExtendedResponse(SpectreeResponse):
    def __init__(
        self,
        *codes,
        code_descriptions=None,
        **code_models,
    ):
        self.code_descriptions = code_descriptions or {}
        super().__init__(*codes, **code_models)

    def generate_spec(self) -> dict:
        """
        extend the spec to add custom descriptions of error codes
        """
        responses = super().generate_spec()

        all_codes = set(self.codes) | self.code_models.keys()
        for code in all_codes:
            description = self.code_descriptions.get(code)
            if description:
                responses[parse_code(code)]["description"] = description

        return responses
