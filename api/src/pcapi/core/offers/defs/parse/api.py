import typing

import pydantic

from pcapi.core.categories import subcategories

from . import types


def build_model_fields(model: type[pydantic.BaseModel]) -> set[types.Field]:
    """Build a set of Fields from model in order to easily compare it with others"""
    return set(parse_model_fields(model.model_fields))


def parse_model_fields(fields: dict[str, pydantic.fields.FieldInfo]) -> typing.Generator[types.Field, None, None]:
    for name, info in fields.items():
        # Some fields' types might be declared as Model1 | Model2 | etc.
        # We will try to fetch meaningful data from it
        union_values = None
        if nested := typing.get_args(info.annotation):
            # ignore all str | None etc. this is not what we are looking for
            union_models = [v for v in nested if hasattr(v, "model_fields")]

            # Some pydantic models will declare a discriminator to help
            # the pydantic parser find which one to use (and avoid
            # trying to parse each model). Let's use this to get the
            # most meaningful representation of this union type.
            if discriminator := getattr(info, "discriminator", None):
                union_values = [
                    typing.get_args(model.model_fields[discriminator].annotation)[0] for model in union_models
                ]
            else:
                # no discriminator?... use the model class name as a
                # default value
                union_values = [m.__name__ for m in union_models]

        # if it looks like a model, it should be a model
        # -> dig and build a (nested) Field with its components
        if hasattr(info.annotation, "model_fields"):
            components = tuple(parse_model_fields(info.annotation.model_fields))  # type: ignore
            yield types.Field.build(name=name, optional=not info.is_required(), components=components)
        elif union_values:
            yield types.Field.build(name=name, optional=not info.is_required(), union_values=tuple(union_values))
        else:
            yield types.Field.build(name=name, optional=not info.is_required())


def build_model_extra_data_fields(model: type[pydantic.BaseModel]) -> set[types.Field]:
    """Compute only the needed `extra_data` field

    When comparing a model with a Subcategory's conditional fields,
    there is no need to normalize the whole model, since only the
    `extra_data` part can be (and will be) used.
    """
    fields = model.model_fields
    extra_data = fields.get("extra_data")
    if not extra_data:
        return set()

    fields = extra_data.annotation.model_fields  # type: ignore
    return set(parse_model_fields(fields))


def build_subcategory_fields(subcategory: subcategories.Subcategory) -> set[types.Field]:
    """Extract a Subcategory's conditional fields' information

    Note:
        a field is considered optional if `is_required_in_internal_form`
        is false. The `is_required_in_external_form` is ignored but this
        is a quite arbitrary choice.
    """

    def _parse(name: str, condition: subcategories.FieldCondition) -> types.Field:
        return types.Field.build(name=name, optional=not condition.is_required_in_internal_form)

    return {_parse(name, condition) for name, condition in subcategory.conditional_fields.items()}
