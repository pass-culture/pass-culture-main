from copy import deepcopy
from typing import Any
from typing import Callable

from pydantic.v1 import BaseModel
from spectree import Response
from spectree import SpecTree
from spectree import Tag


_AUTHENTICATION_ATTRIBUTE = "requires_authentication"


def get_model_key(model: type[BaseModel]) -> str:
    return model.__name__


def get_model_schema(model: type[BaseModel]) -> dict:
    assert issubclass(model, BaseModel)
    return model.schema(ref_template="#/components/schemas/{model}")


def add_security_scheme(route_function: Callable, auth_key: str, scopes: list[str] | None = None) -> None:
    """
    Declare a sufficient security scheme to access the route.
    Will be used by `ExtendedSpecTree` below to document, in the Open API JSON, the security scheme applied to the endpoint.
    The `auth_key` should correspond to a scheme declared in the SpecTree initialization of the route's BluePrint.
    """
    authentication_param = getattr(route_function, _AUTHENTICATION_ATTRIBUTE, [])
    authentication_param.append({auth_key: scopes or []})
    setattr(route_function, _AUTHENTICATION_ATTRIBUTE, authentication_param)


def build_operation_id(func: Callable) -> str:
    return "".join([*[part.capitalize() for part in func.__name__.split("_")]])


class ExtendedSpecTree(SpecTree):
    def __init__(self, *args: Any, humanize_operation_id: bool = False, tags: list[Tag] | None = None, **kwargs: Any):
        """
        :tags:  An sorted list of tags to structure the swagger and the redoc generated
                by spectree.
        """
        super().__init__(*args, **kwargs)
        self.humanize_operation_id = humanize_operation_id
        self.tags = tags or []

    def _generate_tags_list(self) -> list[dict]:
        return [tag.dict() for tag in self.tags]

    def _generate_spec(self) -> dict:
        spec = super()._generate_spec()
        for route in self.backend.find_routes():
            for method, func in self.backend.parse_func(route):
                if self.backend.bypass(func, method) or self.bypass(func):
                    continue

                path_parameter_descriptions = getattr(func, "path_parameter_descriptions", None)
                path, _ = self.backend.parse_path(route, path_parameter_descriptions)

                if self.humanize_operation_id:
                    spec["paths"][path][method.lower()]["operationId"] = build_operation_id(func)

                # Add security params to spec based on what has been defined using `add_security_scheme`
                security = deepcopy(getattr(func, _AUTHENTICATION_ATTRIBUTE, None))
                if security:
                    spec["paths"][path][method.lower()]["security"] = security

        sorted_tags = self._generate_tags_list()
        if sorted_tags:
            spec["tags"] = sorted_tags

        return spec

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
