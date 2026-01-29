import logging
from copy import deepcopy
from typing import Any
from typing import Callable

from pydantic import BaseModel as BaseModelV2
from pydantic.v1 import BaseModel
from spectree import Response
from spectree import SpecTree
from spectree import Tag

from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)

_AUTHENTICATION_ATTRIBUTE = "requires_authentication"
_FEATURE_FLAG_ATTRIBUTE = "feature_flag"


def get_model_key(model: type[BaseModel] | type[BaseModelV2]) -> str:
    return model.__name__


def get_nested_key(_: str, child: str) -> str:
    return child


def add_security_scheme(route_function: Callable, auth_key: str, scopes: list[str] | None = None) -> None:
    """
    Declare a sufficient security scheme to access the route.
    Will be used by `ExtendedSpecTree` below to document, in the Open API JSON, the security scheme applied to the endpoint.
    The `auth_key` should correspond to a scheme declared in the SpecTree initialization of the route's BluePrint.
    """
    authentication_param = getattr(route_function, _AUTHENTICATION_ATTRIBUTE, [])
    authentication_param.append({auth_key: scopes or []})
    setattr(route_function, _AUTHENTICATION_ATTRIBUTE, authentication_param)


def add_feature_flag(route_function: Callable, feature_flag: FeatureToggle) -> None:
    setattr(route_function, _FEATURE_FLAG_ATTRIBUTE, feature_flag)


def build_operation_id(func: Callable) -> str:
    return "".join([*[part.capitalize() for part in func.__name__.split("_")]])


class ExtendedSpecTree(SpecTree):
    def __init__(self, *args: Any, humanize_operation_id: bool = False, tags: list[Tag] | None = None, **kwargs: Any):
        """
        :tags:  An sorted list of tags to structure the swagger and the redoc generated
                by spectree.
        """
        super().__init__(
            *args, **{"naming_strategy": get_model_key, "nested_naming_strategy": get_nested_key, **kwargs}
        )
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

                route_feature_flag = getattr(func, _FEATURE_FLAG_ATTRIBUTE, None)

                if route_feature_flag and not route_feature_flag.is_active():
                    # the route (path + method) is removed from documentation
                    spec["paths"][path].pop(method.lower())
                    continue

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

    def _get_model_definitions(self) -> dict[str, Any]:
        """
        Return the result from SpecTree._get_model_definitions
        Raise an error if we see the same model key twice with different values
        """
        definitions = {}
        errors = []

        # inspired from SpecTree._get_model_definitions
        for name, schema in self.models.items():
            for def_key in ["definitions", "$defs"]:
                if def_key in schema:
                    for key, value in schema[def_key].items():
                        composed_key = self.nested_naming_strategy(name, key)

                        if composed_key not in definitions:
                            definitions[composed_key] = value
                        elif value != definitions[composed_key]:
                            if _is_same_enum(definitions[composed_key], value):
                                definitions[composed_key] = value
                            else:
                                errors.append(composed_key)

        if errors:
            raise ValueError(
                f"Some models appeared multiple times in the definitions with different values: {','.join(errors)}"
            )

        return super()._get_model_definitions()


# TODO (jcicurel-pass, 2026-02-02): Remove when migration to pydantic V1 is over
def _is_same_enum(current_definition: dict, incoming_definition: dict) -> bool:
    # if an enum is used both in a pydantic v1 and v2 model, it will generate two different definitions for the same schema key
    # if the enum values are the same, we can assume the definitions are equivalent
    # the only differences will be on schema fields like "description"
    return (
        "enum" in current_definition
        and "enum" in incoming_definition
        and current_definition["enum"] == incoming_definition["enum"]
    )


class ExtendResponse(Response):
    def generate_spec(self, _naming_strategy: Callable[[type[BaseModel]], str] | None = None) -> dict[str, Any]:
        return super().generate_spec(naming_strategy=get_model_key)
