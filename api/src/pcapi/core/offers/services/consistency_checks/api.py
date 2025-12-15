import typing

from pcapi.core.categories import subcategories
from pcapi.core.offers.services import models
from pcapi.core.offers.services import parse
from pcapi.core.offers.services import utils
from pcapi.core.offers.services.diff import api as diff_api
from pcapi.core.offers.services.diff import types as diff_types
from pcapi.core.offers.services.parse import types


def build_subcategories_diff_status() -> typing.Collection[diff_types.SubcategoryDiffStatus]:
    return [
        build_diff_status(utils.MODELS[subcategory.id], subcategory) for subcategory in subcategories.ALL_SUBCATEGORIES
    ]


def build_diff_status(model: models.Base, subcategory: subcategories.Subcategory) -> diff_types.SubcategoryDiffStatus:
    subcategory_fields = build_subcategory_fields(subcategory)
    new_model_fields = parse.build_model_extra_data_fields(model)
    diff = diff_api.build_fields_diff(subcategory_fields, new_model_fields)

    return diff_types.SubcategoryDiffStatus.build(
        subcategory_id=subcategory.id,
        subcategory_fields=subcategory_fields,
        new_model_fields=new_model_fields,
        diff=diff,
    )


def build_subcategory_fields(subcategory: subcategories.Subcategory) -> set[types.Field]:
    """Extract a Subcategory's fields' information

    Notes:
        a field is considered optional if `is_required_in_internal_form`
        is false. The `is_required_in_external_form` is ignored but this
        is a quite arbitrary choice.
    """

    def _parse(name: str, condition: subcategories.FieldCondition) -> types.Field:
        return types.Field.build(name=name, optional=not condition.is_required_in_internal_form)

    return {_parse(name, condition) for name, condition in subcategory.conditional_fields.items()}
