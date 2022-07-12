from copy import deepcopy
from typing import Any
from typing import Callable
from typing import Dict

from pydantic import BaseModel  # pylint: disable=wrong-pydantic-base-model-import
from spectree import Response
from spectree import SpecTree
from spectree.utils import parse_code


def get_model_key(model):  # type: ignore [no-untyped-def]
    return model.__name__


def get_model_schema(model):  # type: ignore [no-untyped-def]
    assert issubclass(model, BaseModel)
    return model.schema(
        ref_template=f"#/components/schemas/{{model}}"  # pylint: disable=f-string-without-interpolation
    )


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
    def __init__(self, *args, humanize_operation_id=False, **kwargs):  # type: ignore [no-untyped-def]
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
        return spec

    def _add_model(self, model) -> str:  # type: ignore [no-untyped-def]
        model_key = get_model_key(model=model)
        self.models[model_key] = deepcopy(get_model_schema(model=model))

        return model_key

    def _get_model_definitions(self):  # type: ignore [no-untyped-def]

        definitions = {}
        for _name, schema in self.models.items():
            if "definitions" in schema:
                for key, value in schema["definitions"].items():
                    definitions[key] = value
                del schema["definitions"]

        return definitions


class ExtendResponse(Response):
    def generate_spec(self) -> Dict[str, Any]:
        responses: Dict[str, Any] = {}
        for code in self.codes:
            responses[parse_code(code)] = {"description": self.get_code_description(code)}
        for code, model in self.code_models.items():
            model_name = get_model_key(model=model)
            responses[parse_code(code)] = {
                "description": self.get_code_description(code),
                "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{model_name}"}}},
            }
        return responses
