from typing import Callable
from typing import Optional

from spectree import SpecTree


def add_security_scheme(route_function: Callable, auth_key: str, scopes: Optional[list[str]] = None) -> None:
    """Declare a sufficient security scheme to access the route.
    The 'auth_key' should correspond to a scheme declared in
    the SpecTree initialization of the route's BluePrint.
    """
    if not hasattr(route_function, "requires_authentication"):
        route_function.requires_authentication = []
    route_function.requires_authentication.append({auth_key: scopes or []})


def build_operation_id(method, path, func):
    path_parts = path.split("/")
    module = path_parts[1] if path_parts[1].lower() not in ["v1", "v2"] else path_parts[2]
    return "".join([method.lower(), module.capitalize(), *[part.capitalize() for part in func.__name__.split("_")]])


class ExtendedSpecTree(SpecTree):
    def __init__(self, *args, humanize_operation_id=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.humanize_operation_id = humanize_operation_id

    def _generate_spec(self) -> dict:
        spec = super()._generate_spec()
        if self.humanize_operation_id:
            for route in self.backend.find_routes():
                for method, func in self.backend.parse_func(route):
                    if self.backend.bypass(func, method) or self.bypass(func):
                        continue
                    path_parameter_descriptions = getattr(func, "path_parameter_descriptions", None)
                    path, _parameters = self.backend.parse_path(route, path_parameter_descriptions)
                    spec["paths"][path][method.lower()]["operationId"] = build_operation_id(method, path, func)
        return spec
