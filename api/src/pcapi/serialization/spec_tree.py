from copy import deepcopy
from typing import Any
from typing import Callable

from pydantic.v1 import BaseModel
from spectree import Response
from spectree import SpecTree


def get_model_key(model: type[BaseModel]) -> str:
    return model.__name__


def get_model_schema(model: type[BaseModel]) -> dict:
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

    def _add_model(self, model: type[BaseModel]) -> str:
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
    def generate_spec(self, _naming_strategy: Callable[[type[BaseModel]], str] | None = None) -> dict[str, Any]:
        return super().generate_spec(naming_strategy=get_model_key)
