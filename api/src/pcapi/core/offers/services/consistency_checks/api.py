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
    new_model_fields = parse.build_new_model_extra_data_fields(model)
    diff = build_fields_diff(subcategory_fields, new_model_fields)

    return types.SubcategoryDiffStatus.build(
        subcategory_id=subcategory.id,
        subcategory_fields=subcategory_fields,
        new_model_fields=new_model_fields,
        diff=diff,
    )


def build_fields_diff(
    subcategory_fields: set[types.ExtraDataField], new_model_fields: set[types.ExtraDataField]
    ) -> typing.Collection[types.Diff]:
    """Compute a difference summary between `subcategory_fields` and `new_model_fields`"""
    diff = []

    subcategory_fields_mapping = {f.id: f for f in subcategory_fields}
    new_model_fields_mapping = {f.id: f for f in new_model_fields}

    for field_id, f in subcategory_fields_mapping.items():
        new_model_field = new_model_fields_mapping.get(field_id)

        if not new_model_field:
            diff.append(types.ShouldBePresent(f.name))
        elif new_model_field == f:
            diff.append(types.Same(f.name))
        elif (new_model_field.id == f.id) and f.optional:
            diff.append(types.ShouldBeOptional(f.name))
        elif (new_model_field.id == f.id) and not f.optional:
            diff.append(types.ShouldBeMandatory(f.name))

    for field_id, f in new_model_fields_mapping.items():
        subcategory_field = subcategory_fields_mapping.get(field_id)
        if not subcategory_field:
            diff.append(types.ShouldBeMissing(f.name))

    return diff
