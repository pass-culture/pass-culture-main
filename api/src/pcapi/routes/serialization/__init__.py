from datetime import datetime
from decimal import Decimal
from math import isfinite


# fmt: off
# isort: off
from pydantic import BaseModel as PydanticBaseModel  # pylint: disable=wrong-pydantic-base-model-import
# isort: on
# fmt: on

from pydantic import errors
from pydantic import validator

from pcapi.routes.serialization.dictifier import as_dict
from pcapi.routes.serialization.serializer import serialize
from pcapi.serialization import utils as serialization_utils


__all__ = ("as_dict", "serialize")
_missing = object()


class BaseModel(PydanticBaseModel):
    @validator("*")
    def do_not_allow_nan(cls, v, field):  # type: ignore [no-untyped-def]
        if field.allow_none and v is None:
            return v

        if field.outer_type_ is float and not isfinite(v):
            raise errors.DecimalIsNotFiniteError()
        return v

    @classmethod
    def build_model(cls, obj: object, **replacements: dict) -> "BaseModel":
        if not cls.__config__.orm_mode:
            raise ValueError("You must have the config attribute orm_mode=True to use build_model")

        kwargs = {}

        for name, model_field in cls.__fields__.items():
            field_type = model_field.type_
            if name in replacements:
                kwargs[name] = replacements[name]
                continue
            value = getattr(obj, name, _missing)
            if not value is _missing:
                # recursive models
                if issubclass(field_type, BaseModel) and not isinstance(value, dict):
                    value = field_type.build_model(value)
                kwargs[name] = value  # type: ignore [assignment]

        return cls(**kwargs)

    class Config:
        @staticmethod
        def schema_extra(schema, model):  # type: ignore [no-untyped-def]
            for prop, value in schema.get("properties", {}).items():
                # retrieve right field from alias or name
                field = [x for x in model.__fields__.values() if x.alias == prop][0]
                if field.allow_none:
                    if "$ref" in value:
                        if issubclass(field.type_, PydanticBaseModel):
                            # add 'title' in schema to have the exact same behaviour as the rest
                            value["title"] = field.type_.__config__.title or field.type_.__name__
                        value["anyOf"] = [{"$ref": value.pop("$ref")}]
                    value["nullable"] = True


class ConfiguredBaseModel(BaseModel):
    class Config:
        alias_generator = serialization_utils.to_camel
        allow_population_by_field_name = True
        orm_mode = True
