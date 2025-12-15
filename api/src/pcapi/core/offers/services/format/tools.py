import itertools
import typing

from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
from pcapi.core.offers.services import parse
from pcapi.core.offers.services.models.base import Base
from pcapi.core.offers.services.models.base import Mandatory

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

    parsed_properties = parse.build_model_fields(model)

    required_fields = [p for p in parsed_properties if not p.optional]
    optional_fields = [p for p in parsed_properties if p.optional]

    hierarchy, cache = build_model_hierarchy(cache, model)

    required = [build_field_with_origin(hierarchy, field) for field in required_fields]
    optional = [build_field_with_origin(hierarchy, field) for field in optional_fields]

    schema = types.ModelSchema(
        subcategory=subcategory,
        properties=types.Properties(
            required=sort_fields_with_origin(required), optional=sort_fields_with_origin(optional)
        ),
    )

    return schema, cache


def build_model_hierarchy(cache: types.HierarchyCache, model: Base) -> tuple[types.Hierarchy, types.HierarchyCache]:
    """Build a model's `Hierarchy` object

    The cache is used to avoid parsing the same parent classes twice
    (eg. top classes like `Mandatory` or `Base`) and is updated
    for next calls.
    """
    updated_cache = cache | update_global_model_hierarchy_cache(cache, model)

    mandatory = updated_cache.pop("Mandatory")
    base = updated_cache.pop("Base") - mandatory
    other = {field for fields in updated_cache.values() for field in fields} - base - mandatory

    return types.Hierarchy(mandatory=mandatory, base=base, other=other), updated_cache


def update_global_model_hierarchy_cache(cache: types.HierarchyCache, model: Base) -> types.HierarchyCache:
    """Update the global cache hierarchy with one model

    Compute the model's full class hierarchy using already known classes
    and update the cache with missing classes.
    """
    updated_cache: types.HierarchyCache = {}

    # stop recursive calls here: there is no need to go further
    # the model hierarchy
    if model is Mandatory:
        return updated_cache

    # __bases__ contains the model's parent classes
    # there should be only one is this context
    for b in getattr(model, "__bases__", []):
        if b not in cache:
            updated_cache[b.__name__] = parse.build_model_fields(b)
            updated_cache.update(update_global_model_hierarchy_cache(cache, b))

    return updated_cache


def build_field_with_origin(hierarchy: types.Hierarchy, field: types.Field) -> types.FieldWithOrigin:
    if field in hierarchy.mandatory:
        return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.MANDATORY)
    elif field in hierarchy.base:
        return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.BASE)
    elif field in hierarchy.other:
        return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.INHERITED)
    return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.OWN)


def sort_fields_with_origin(
    fields: typing.Collection[types.FieldWithOrigin],
) -> typing.Collection[types.FieldWithOrigin]:
    """First sort by origin, and then sort by name within each group"""
    sorted_by_origin = sorted(fields, key=lambda f: f.origin)
    grouped_by_origin = itertools.groupby(sorted_by_origin, key=lambda f: f.origin)

    nested_fields = [sorted(fields, key=lambda f: f.name) for _, fields in grouped_by_origin]
    return [field for group in nested_fields for field in group]
