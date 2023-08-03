from copy import deepcopy
from typing import Any
from typing import Callable
from typing import Dict
from typing import Type

from pydantic import BaseModel  # pylint: disable=wrong-pydantic-base-model-import
from spectree import Response
from spectree import SpecTree

from pcapi import settings


def get_model_key(model: Type[BaseModel]) -> str:
    return model.__name__


def get_model_schema(model: Type[BaseModel]) -> dict:
    assert issubclass(model, BaseModel)
    return model.schema(ref_template="#/components/schemas/{model}")


def add_security_scheme(route_function: Callable, auth_key: str, scopes: list[str] | None = None) -> None:
    """Declare a sufficient security scheme to access the route.
    The 'auth_key' should correspond to a scheme declared in
    the SpecTree initialization of the route's BluePrint.
    """
    if not hasattr(route_function, "requires_authentication"):
        route_function.requires_authentication = []  # type: ignore [attr-defined]
    route_function.requires_authentication.append({auth_key: scopes or []})  # type: ignore [attr-defined]


def build_operation_id(func: Callable) -> str:
    return "".join([*[part.capitalize() for part in func.__name__.split("_")]])


class ExtendedSpecTree(SpecTree):
    def __init__(self, *args: Any, humanize_operation_id: bool = False, **kwargs: Any):
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
                    spec["paths"][path][method.lower()]["operationId"] = build_operation_id(func)
                    spec["servers"] = [{"url": settings.API_URL}]
        return spec

    def _add_model(self, model: Type[BaseModel]) -> str:
        model_key = get_model_key(model=model)
        self.models[model_key] = deepcopy(get_model_schema(model=model))

        return model_key

    def _get_model_definitions(self) -> dict:
        definitions = {}
        for _name, schema in self.models.items():
            if "definitions" in schema:
                for key, value in schema["definitions"].items():
                    definitions[key] = value
                del schema["definitions"]

        return definitions


class ExtendResponse(Response):
    def generate_spec(self, _naming_strategy: Callable[[Type[BaseModel]], str] = None) -> Dict[str, Any]:
        return super().generate_spec(naming_strategy=get_model_key)
