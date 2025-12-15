"""Diff utilities between (new) models and subcategories

This module provides some simple tools to compare what can be compared:
    * a subcategory's conditional fields to a model's extra data;
    * a subcategory's (implicit) typology to a model's one.

Within this module, fields mean:
    > a subcategory's conditional fields
    > a model's extra data.
"""

import typing

import pcapi.core.offers.defs.parse.api as parse_api
import pcapi.core.offers.defs.parse.types as parse_types
from pcapi.core.categories import subcategories
from pcapi.core.offers.defs import models
from pcapi.core.offers.defs.models import typology

from . import types


def build_fields_diff(
    src_fields: set[parse_types.Field], compared_fields: set[parse_types.Field]
) -> typing.Collection[types.FieldDiff]:
    """Difference summary between `src_fields` and `compared_fields`

    `src_fields` is considered to be the source of truth: the difference
    is computed that way. For example a `ShouldBeOptional` field means
    that it is found inside both sets except that is is optional in
    `src_fields` and mandatory in `compared_fields`.
    """
    diff: list[types.FieldDiff] = []

    compared_fields_mapping = {f.id: f for f in compared_fields}

    for source in src_fields:
        other = compared_fields_mapping.get(source.id)

        if not other:
            diff.append(types.ShouldBePresent(source.name))
        elif source == other:
            diff.append(types.Same(source.name))
        elif (source.id == other.id) and source.optional:
            diff.append(types.ShouldBeOptional(source.name))
        else:
            diff.append(types.ShouldBeMandatory(source.name))

    known_field_ids = {sf.id for sf in src_fields}
    diff.extend([types.ShouldBeMissing(f.name) for f in compared_fields if f.id not in known_field_ids])
    return diff


def build_model_and_subcategory_fields_diff_status(
    model: type[models.Base], subcategory: subcategories.Subcategory
) -> types.DiffStatus:
    """Build fields difference between model and subcategory

    Compute the diff between the model's and the subcategory's fields
    with the whole context: diff kind, found fields in both sides...

    The source of truth is the subcategory.
    """
    subcategory_fields = parse_api.build_subcategory_fields(subcategory)
    new_model_fields = parse_api.build_model_extra_data_fields(model)
    diff = build_fields_diff(subcategory_fields, new_model_fields)

    return types.DiffStatus.build(
        subcategory_id=subcategory.id,
        subcategory_fields=subcategory_fields,
        new_model_fields=new_model_fields,
        diff=diff,
    )


def build_typology_diff(subcategory: subcategories.Subcategory, model: type[models.Base]) -> types.TypologyDiff:
    """Compute typology diff between subcategory and model

    The subcategory is the source of truth: a "should_be_digital" diff
    kind means that the subcategory is a digital one but not the input
    model.

    > a subcategory is an event whilst a model is an activity:
    """
    if subcategory.is_selectable and typology.cannot_be_created(model):
        return "should_be_selectable"
    elif not subcategory.is_selectable and not typology.cannot_be_created(model):
        return "should_not_be_selectable"

    if subcategory.is_digital_deposit and not typology.is_digital(model):
        return "should_be_digital"
    elif not subcategory.is_digital_deposit and typology.is_digital(model):
        return "should_not_be_digital"

    # is_activity means: could be an event, but we can't say it is
    # before a concrete offer has stocks defined.
    if subcategory.is_event and not typology.is_activity(model):
        return "should_be_activity"
    elif not subcategory.is_event and typology.is_activity(model):
        return "should_not_be_activity"

    return "same"
