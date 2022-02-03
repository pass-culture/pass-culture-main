from typing import Callable
from typing import Optional


def add_security_scheme(route_function: Callable, auth_key: str, scopes: Optional[list[str]] = None) -> None:
    """Declare a sufficient security scheme to access the route.
    The 'auth_key' should correspond to a scheme declared in
    the SpecTree initialization of the route's BluePrint.
    """
    if not hasattr(route_function, "requires_authentication"):
        route_function.requires_authentication = []
    route_function.requires_authentication.append({auth_key: scopes or []})
