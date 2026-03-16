import itertools
import typing

from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
from pcapi.core.offers.defs import parse
from pcapi.core.offers.defs.models.base import Base
from pcapi.core.offers.defs.parse import types as base_types

from . import types


def build_schemas(models: typing.Collection[Base]) -> typing.Collection[types.ModelSchema]:
    cache: types.HierarchyCache = {}
    schemas = []

    for model in models:
        schema, cache = format_model_to_schema(cache, model)
        schemas.append(schema)

    return sorted(schemas, key=lambda s: s.subcategory.id)


def format_model_to_schema(cache: types.HierarchyCache, model: Base) -> tuple[types.ModelSchema, types.HierarchyCache]:
    subcategory_id = typing.get_args(model.model_fields["subcategory_id"].annotation)[0]
    subcategory = ALL_SUBCATEGORIES_DICT[subcategory_id]

    parsed_fields = parse.build_model_fields(model, exclude=("typology",))
    typology = model.model_fields["typology"].default

    required_fields = [p for p in parsed_fields if not p.optional]
    optional_fields = [p for p in parsed_fields if p.optional]

    parent, cache = build_model_parent(cache, model)

    required = [build_field_with_origin(parent, field) for field in required_fields]
    optional = [build_field_with_origin(parent, field) for field in optional_fields]

    schema = types.ModelSchema(
        subcategory=subcategory,
        properties=types.Properties(
            required=sort_fields_with_origin(required),
            optional=sort_fields_with_origin(optional),
            is_digital=typology.is_digital,
            can_be_an_event=typology.can_be_an_event,
        ),
    )

    return schema, cache


def build_model_parent(cache: types.HierarchyCache, model: Base) -> tuple[types.Hierarchy, types.HierarchyCache]:
    """Build a model's `Hierarchy` object

    The cache is used to avoid parsing the same parent classes twice
    (eg. top classes like `Mandatory` or `Base`) and is updated
    for next calls.
    """
    if base := cache.get("Base"):
        return base, cache

    base = parse.build_model_fields(Base)
    cache[Base.__name__] = base
    return base, cache


def build_field_with_origin(hierarchy: types.Hierarchy, field: base_types.Field) -> types.FieldWithOrigin:
    if field in hierarchy:
        return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.BASE)
    return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.OWN)


def sort_fields_with_origin(
    fields: typing.Collection[types.FieldWithOrigin],
) -> typing.Collection[types.FieldWithOrigin]:
    """First sort by origin, and then sort by name within each group"""
    sorted_by_origin = sorted(fields, key=lambda f: f.origin)
    grouped_by_origin = itertools.groupby(sorted_by_origin, key=lambda f: f.origin)

    nested_fields = [sorted(fields, key=lambda f: f.name) for _, fields in grouped_by_origin]
    return [field for group in nested_fields for field in group]
