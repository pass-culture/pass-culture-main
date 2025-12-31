import pydantic as pydantic_v2

from pcapi.core.categories import subcategories

from . import types


def new_model_fields(model: pydantic_v2.BaseModel) -> set[types.ExtraDataField]:
    """Extract a new model's fields' information

    Notes:
        fields are fetched from the json schema which is not a nice and
        readable way to do it. However, it seems to be easiest than
        parsing directly the model typing information.
    """

    def _parse(defs, v):
        # there is no need to build a full parser: only the needed
        # paths and patterns should be covered
        match v:
            case {"anyOf": choices}:
                yield from _parse(defs, choices)
            case [*options]:
                for opt in options:
                    yield from _parse(defs, opt)
            case {"$ref": ref}:
                yield from _parse(defs, defs[ref.replace("#/$defs/", "")])
            case {"properties": props}:
                for name, data in props.items():
                    yield _parse_property(name, data)
            case _:
                pass

    def _parse_property(name, data):
        # same as above
        match data:
            case {"anyOf": choices, "default": default}:
                return types.ExtraDataField.build(name=name, default=default, optional={"type": "null"} in choices)
            case {"anyOf": choices}:
                return types.ExtraDataField.build(name=name, optional={"type": "null"} in choices)
            case {"default": default}:
                return types.ExtraDataField.build(name=name, default=default, optional=False)
            case _:
                return types.ExtraDataField.build(name=name, optional=False)

    schema = model.model_json_schema()
    defs = schema["$defs"]
    extra_data_properties = schema["properties"].get("extra_data")
    if not extra_data_properties:
        return set()

    return set(_parse(defs, extra_data_properties))


def subcategory_fields(subcategory: subcategories.Subcategory) -> set[types.ExtraDataField]:
    """Extract a Subcategory's fields' information

    Notes:
        a field is considered optional is `is_required_in_internal_form`
        is false. The `is_required_in_external_form` is ignored but this
        is a quite arbitrary choice.
    """

    def _parse(name, condition):
        return types.ExtraDataField.build(name=name, optional=not condition.is_required_in_internal_form)

    return {_parse(name, condition) for name, condition in subcategory.conditional_fields.items()}
