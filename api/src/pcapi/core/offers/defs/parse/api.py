import typing

import pydantic

from . import types


def parse_model_fields(fields: dict[str, pydantic.fields.FieldInfo]) -> typing.Generator[types.Field, None, None]:
    for name, info in fields.items():
        # if it looks like a model, it should be a model
        # -> dig and build a Field with its components
        if hasattr(info.annotation, "model_fields"):
            components = tuple(parse_model_fields(info.annotation.model_fields))  # type: ignore
            yield types.Field.build(name=name, optional=not info.is_required(), components=components)
        else:
            yield types.Field.build(name=name, optional=not info.is_required())


def build_model_fields(model: pydantic.BaseModel, exclude: typing.Collection[str] | None = None) -> set[types.Field]:
    """Build a set of Fields from model in order to easily compare it with others"""
    if exclude:
        return {f for f in parse_model_fields(model.model_fields) if f.name not in exclude}
    return set(parse_model_fields(model.model_fields))


def build_model_extra_data_fields(model: pydantic.BaseModel) -> set[types.Field]:
    fields = model.model_fields
    extra_data = fields.get("extra_data")
    if not extra_data:
        return set()

    fields = extra_data.annotation.model_fields  # type: ignore
    return set(parse_model_fields(fields))
