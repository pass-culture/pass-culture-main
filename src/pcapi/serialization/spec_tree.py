from typing import Optional

from spectree import SpecTree


def add_security_scheme(route_function, auth_key: str, scopes: Optional[list[str]] = None):
    """Declare a sufficient security scheme to access the route.
    The 'auth_key' should correspond to a scheme declared in
    the ExtendedSpecTree initialization of the route's BluePrint.
    """
    if not hasattr(route_function, "requires_authentication"):
        route_function.requires_authentication = []
    route_function.requires_authentication.append({auth_key: scopes or []})


class ExtendedSpecTree(SpecTree):
    def __init__(self, *args, security_schemes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.security_schemes = security_schemes

    def _generate_spec(self) -> dict:
        schema = super()._generate_spec()
        schema["components"]["securitySchemes"] = self.security_schemes

        # Find routes that are protected by authentication
        # We may drop this whenever Spectree supports authentication
        for route in self.backend.find_routes():
            path, _parameters = self.backend.parse_path(route)
            if path not in schema["paths"]:
                continue
            for method, func in self.backend.parse_func(route):
                if method.lower() not in schema["paths"][path]:
                    continue
                if self.backend.bypass(func, method) or self.bypass(func):
                    continue

                if getattr(func, "requires_authentication", None):
                    schema["paths"][path][method.lower()]["security"] = func.requires_authentication

        return schema
