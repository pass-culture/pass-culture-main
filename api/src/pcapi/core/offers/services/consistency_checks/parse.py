import typing

import pydantic as pydantic_v2

from pcapi.core.categories import subcategories
from pcapi.core.offers.services import models

from . import types


AnyField = types.Field | types.ExtraDataField
AnyComponents = tuple[types.Field] | tuple[types.ExtraDataField]
AnyRefs = tuple[types.Field] | tuple[types.ExtraDataField]
AnyFieldsGenerator = typing.Generator[types.Field, None, None] | typing.Generator[types.ExtraDataField, None, None]


def build_components(defs: dict, ref: str) -> AnyComponents:
    props = defs[ref.replace("#/$defs/", "")].get("properties")
    return tuple(parse_properties(defs, props))


def parse_choices(defs: dict, refs: list[dict]) -> tuple[types.OrField]:
    match refs:
        case [{"$ref": ref}]:
            definition = defs[ref.replace("#/$defs/", "")]
            props = definition.get("properties")
            name = definition.get("title")
            components = tuple(parse_properties(defs, props))
            return tuple([types.OrField(name=name, components=components)])
        case [{"$ref": ref}, *rest]:
            definition = defs[ref.replace("#/$defs/", "")]
            props = definition.get("properties")
            name = definition.get("title")
            components = tuple(parse_properties(defs, props))
            return tuple([types.OrField(name=name, components=components)]) + parse_choices(defs, rest)
        case _:
            return tuple()


def parse_properties(defs: dict, properties: dict, field_cls: typing.Type[AnyField]) -> AnyFieldsGenerator:
    for name, data in properties.items() if properties else []:
        match data:
            case {"$ref": ref}:
                yield field_cls.build(name=name, components=build_components(defs, ref))
            case {"anyOf": [{"$ref": ref}, {"type": "null"}]}:
                yield field_cls.build(name=name, optional=True, components=build_components(defs, ref))
            case {"anyOf": choices}:
                components = parse_choices(defs, choices)
                yield field_cls.build(name=name, optional={"type": "null"} in choices, components=components)
            case _:
                yield field_cls.build(name=name)


def build_model_fields(model: models.base.Base) -> typing.Collection[types.Field]:
    schema = model.model_json_schema()
    defs = schema["$defs"]
    properties = schema["properties"]
    if not properties:
        return set()

    return set(parse_properties(defs, properties, field_cls=types.Field))


def build_new_model_extra_data_fields(model: models.base.Base) -> set[types.ExtraDataField]:
    schema = model.model_json_schema()
    defs = schema["$defs"]
    extra_data_properties = schema["properties"].get("extra_data")
    if not extra_data_properties:
        return set()

    return set(parse_properties(defs, extra_data_properties, field_cls=types.ExtraDataField))


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
            case {"anyOf": choices}:
                return types.ExtraDataField.build(name=name, optional={"type": "null"} in choices)
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
