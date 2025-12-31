import typing

from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
from pcapi.core.categories.subcategories import Subcategory
from pcapi.core.offers.services import SUBCATEGORY_TO_MODEL
from pcapi.core.offers.services import utils

from . import parse
from . import types


def all_subcategories_are_modeled() -> bool:
    flatten_mappings = {row.subcategory_id for row in utils.stream_flattened_subcategories_models()}
    return flatten_mappings == ALL_SUBCATEGORIES_DICT.keys()


def subcategories_full_status() -> typing.Collection[types.SubcategoryDiffStatus]:
    res = []

    for subcategory in ALL_SUBCATEGORIES_DICT.values():
        diff_status = subcategory_full_status(subcategory)
        res.append(diff_status)

    return res


def subcategory_full_status(subcategory: Subcategory) -> types.SubcategoryDiffStatus:
    model = SUBCATEGORY_TO_MODEL[subcategory.id]

    subcategory_fields = parse.subcategory_fields(subcategory)
    new_model_fields = parse.new_model_fields(model)
    diff = build_diff_status(subcategory.id, subcategory_fields, new_model_fields)

    return types.SubcategoryDiffStatus(
        subcategory_id=subcategory.id,
        subcategory_fields=subcategory_fields,
        new_model_fields=new_model_fields,
        diff=diff,
    )


def build_fields_diff(
    subcategory_fields: set[types.ExtraDataField], extra_data: set[types.ExtraDataField]
) -> types.DiffSummary:
    """Compute a difference summary between `subcategory_fields` and `extra_data`"""
    diff = []

    subcategory_fields_mapping = {f.id: f for f in subcategory_fields}
    extra_data_mapping = {f.id: f for f in extra_data}

    for field_id, f in subcategory_fields_mapping.items():
        extra_data_field = extra_data_mapping.get(field_id)

        if not extra_data_field:
            diff.append(types.ShouldBePresent(f.name))
        elif extra_data_field == f:
            diff.append(types.Same(f.name))
        elif (extra_data_field.id == f.id) and f.optional:
            diff.append(types.ShouldBeOptional(f.name))
        elif (extra_data_field.id == f.id) and not f.optional:
            diff.append(types.ShouldBeMandatory(f.name))

    for field_id, f in extra_data_mapping.items():
        subcategory_field = subcategory_fields_mapping.get(field_id)
        if not subcategory_field:
            diff.append(types.ShouldBeMissing(f.name))

    return diff


def build_diff_status(
    subcategory_id: str, subcategory_fields: set[types.ExtraDataField], extra_data: set[types.ExtraDataField]
) -> types.DiffSummary:
    """Build the full difference status between `subcategory_fields` and `extra_data`"""

    def compute_diff_class(diff):
        cls = types.NoDiff
        for diff_item in diff:
            if type(diff_item) in (types.ShouldBeMissing, types.ShouldBePresent):
                return types.DiffSummary

            if type(diff_item) in (types.ShouldBeOptional, types.ShouldBeMandatory):
                cls = types.OptionalDiff
        return cls

    diff = build_fields_diff(subcategory_fields, extra_data)
    return compute_diff_class(diff)(subcategory_id, diff)
