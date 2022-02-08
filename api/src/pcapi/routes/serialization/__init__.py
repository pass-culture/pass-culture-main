from math import isfinite

# pylint: disable=wrong-pydantic-base-model-import
from pydantic import BaseModel as PydanticBaseModel
from pydantic import errors
from pydantic import validator

from pcapi.routes.serialization.dictifier import as_dict
from pcapi.routes.serialization.serializer import serialize


__all__ = ("as_dict", "serialize")


class BaseModel(PydanticBaseModel):
    @validator("*")
    def do_not_allow_nan(cls, v, field):  # pylint: disable=no-self-argument
        if field.outer_type_ is float and not isfinite(v):
            raise errors.DecimalIsNotFiniteError()
        return v

    class Config:
        @staticmethod
        def schema_extra(schema, model):
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
