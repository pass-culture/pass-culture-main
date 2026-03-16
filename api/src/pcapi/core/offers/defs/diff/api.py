import typing

import pcapi.core.offers.defs.parse.types as parse_types
from pcapi.core.categories import subcategories
from pcapi.core.offers.defs import models
from pcapi.core.offers.defs.models import base as base_models

from . import types


def build_fields_diff(
    src_fields: set[parse_types.Field], compared_fields: set[parse_types.Field]
) -> typing.Collection[types.Diff]:
    """Difference summary between `src_fields` and `compared_fields`

    `src_fields` is considered to be the source of truth: the difference
    is computed that way. For example a `ShouldBeOptional` field means
    that it is found inside both sets except that is is optional in
    `src_fields` and mandatory in `compared_fields`.
    """
    diff: list[types.Diff] = []

    compared_fields_mapping = {f.id: f for f in compared_fields}

    for f in src_fields:
        compared = compared_fields_mapping.get(f.id)

        match f.compare(compared):
            case parse_types.FieldCompareKind.EQUAL:
                diff.append(types.Same(f.name))
            case parse_types.FieldCompareKind.SHOULD_BE_PRESENT:
                diff.append(types.ShouldBePresent(f.name))
            case parse_types.FieldCompareKind.SHOULD_BE_OPTIONAL:
                diff.append(types.ShouldBeOptional(f.name))
            case parse_types.FieldCompareKind.SHOULD_BE_MANDATORY:
                diff.append(types.ShouldBeMandatory(f.name))

    unexpected_field_ids = {f.id for f in compared_fields} - {f.id for f in src_fields}
    unexpected_fields = [f for f in compared_fields if f.id in unexpected_field_ids]
    for f in unexpected_fields:
        diff.append(types.ShouldBeMissing(f.name))

    return diff


def build_properties_diff(subcategory: subcategories.Subcategory, model: models.Base) -> types.PropertiesDiff:
    """Compute properties diff between subcategory and model

    The are two properties for now: digital and event.
    -> is the subcategory/model a digital one?
    -> is the subcategory/model one that could be an event?
    """
    typology = model.model_fields["typology"].default
    if typology == base_models.Typology.CANNOT_BE_CREATED:
        return types.PropertiesDiff(kind="same")

    if subcategory.is_digital_deposit and not typology.is_digital:
        return types.PropertiesDiff(kind="should_be_digital")
    elif not subcategory.is_digital_deposit and typology.is_digital:
        return types.PropertiesDiff(kind="should_not_be_digital")

    if subcategory.is_event and not typology.can_be_an_event:
        return types.PropertiesDiff(kind="could_be_an_event")
    elif not subcategory.is_event and typology.can_be_an_event:
        return types.PropertiesDiff(kind="can_not_be_an_event")

    return types.PropertiesDiff(kind="same")
