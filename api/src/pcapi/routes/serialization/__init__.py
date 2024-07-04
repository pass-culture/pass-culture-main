import datetime
from math import isfinite

import pydantic.v1 as pydantic_v1

from pcapi.serialization import utils as serialization_utils
from pcapi.utils.date import format_into_utc_date


class BaseModel(pydantic_v1.BaseModel):
    @pydantic_v1.validator("*")
    def do_not_allow_nan(cls, v, field):  # type: ignore[no-untyped-def]
        if field.allow_none and v is None:
            return v

        if field.outer_type_ is float and not isfinite(v):
            raise pydantic_v1.errors.DecimalIsNotFiniteError()
        return v

    class Config:
        @staticmethod
        def schema_extra(schema, model):  # type: ignore[no-untyped-def]
            for prop, value in schema.get("properties", {}).items():
                # retrieve right field from alias or name
                field = [x for x in model.__fields__.values() if x.alias == prop][0]
                if field.allow_none:
                    if "$ref" in value:
                        if issubclass(field.type_, pydantic_v1.BaseModel):
                            # add 'title' in schema to have the exact same behaviour as the rest
                            value["title"] = field.type_.__config__.title or field.type_.__name__
                        value["anyOf"] = [{"$ref": value.pop("$ref")}]
                    value["nullable"] = True


class ConfiguredBaseModel(BaseModel):
    class Config:
        alias_generator = serialization_utils.to_camel
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime.datetime: format_into_utc_date}
