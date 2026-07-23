import itertools
import typing

from pcapi.core.offers.defs import utils
from pcapi.core.offers.defs.models import typology
from pcapi.core.offers.defs.models.base import Base
from pcapi.core.offers.defs.parse import api as parse_api
from pcapi.core.offers.defs.parse import types as base_types

from . import types


def build_schemas(models: typing.Collection[type[Base]]) -> typing.Collection[types.ModelSchema]:
    schemas = []
    base_model = parse_api.build_model_fields(Base)

    for model in models:
        schema = format_model_to_schema(base_model, model)
        schemas.append(schema)

    return sorted(schemas, key=lambda s: s.subcategory.id)


def format_model_to_schema(base_model: set[base_types.Field], model: type[Base]) -> types.ModelSchema:
    """Build a full schema from a model

    Extract required and optional properties, fetch subcategory and
    typology.

    > base_model is the `Base` that all models inherit from. It is used
    to find out if a model's field has been inherited or not (the
    display might not always be the same).
    """
    parsed_fields = parse_api.build_model_fields(model)

    required_fields = [p for p in parsed_fields if not p.optional]
    required = [build_field_with_origin(base_model, field) for field in required_fields]

    optional_fields = [p for p in parsed_fields if p.optional]
    optional = [build_field_with_origin(base_model, field) for field in optional_fields]

    return types.ModelSchema(
        subcategory=utils.extract_subcategory(model),
        properties=types.Properties(
            required=sort_fields_with_origin(required),
            optional=sort_fields_with_origin(optional),
            typology=typology.get_typology(model),
        ),
    )


def build_field_with_origin(base_model: set[base_types.Field], field: base_types.Field) -> types.FieldWithOrigin:
    """Does this input field come from the `Base` model?"""
    if field in base_model:
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
