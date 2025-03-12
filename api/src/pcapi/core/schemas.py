from math import isfinite

import pydantic.v1 as pydantic_v1


class SchemasBaseModel(pydantic_v1.BaseModel):
    @pydantic_v1.validator("*")
    def do_not_allow_nan(cls, v, field):  # type: ignore[no-untyped-def]
        if field.allow_none and v is None:
            return v

        if field.outer_type_ is float and not isfinite(v):
            raise pydantic_v1.errors.DecimalIsNotFiniteError()
        return v
