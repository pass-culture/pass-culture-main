import typing

import pcapi.core.offers.services.parse.types as parse_types

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
