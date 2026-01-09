import typing

from . import types


def build_fields_diff(
    subcategory_fields: set[types.Field], new_model_fields: set[types.Field]
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
