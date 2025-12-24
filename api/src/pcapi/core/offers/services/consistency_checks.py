import typing

import pydantic as pydantic_v2

from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT

from . import SUBCATEGORY_TO_MODEL
from . import utils


def all_subcategories_are_modeled() -> bool:
    flatten_mappings = {row.subcategory_id for row in utils.stream_flattened_subcategories_models()}
    return flatten_mappings == ALL_SUBCATEGORIES_DICT.keys()


def _parse_extra_data(model: pydantic_v2.BaseModel) -> dict:
    def _parse(defs, v):
        match v:
            case {"anyOf": choices}:
                yield from _parse(defs, choices)
            case [*options]:
                for opt in options:
                    yield from _parse(defs, opt)
            case {"$ref": ref}:
                yield from _parse(defs, defs[ref.replace("#/$defs/", "")])
            case {"properties": props}:
                yield from props
            case _:
                pass

    schema = model.model_json_schema()
    defs = schema["$defs"]
    extra_data_properties = schema["properties"].get("extra_data")
    if not extra_data_properties:
        return set()

    return set(_parse(defs, extra_data_properties))


def _format_extra_data_fields(fields: typing.Collection[str]) -> dict[str, str]:
    return {field.lower().replace("_", ""): field for field in fields}


class FieldsCompare:
    kind = "base"

    def __init__(self, subcategory_id: str, fields: dict, extra_data: dict | None = None, diff: set = set()):
        self.subcategory_id = subcategory_id
        self.fields = set(fields.values())
        self.extra_data = set(extra_data.values()) if extra_data else set()
        self.diff = diff

    def __repr__(self):
        return f"{self.__class__.__name__}(subcategory_id={self.subcategory_id}, fields={self.fields}, extra_data={self.extra_data}, diff={self.diff})"


class ExactMatch(FieldsCompare):
    kind = "exact"


class ExtraDataHasMore(FieldsCompare):
    kind = "diff"


class SubcategoryHasMore(FieldsCompare):
    kind = "diff"


class BothHaveMissing(FieldsCompare):
    kind = "diff"


class NoExtraData(FieldsCompare):
    kind = "missing"


def extra_data_are_mapped() -> bool:
    res = []

    for subcategory_name, subcategory in ALL_SUBCATEGORIES_DICT.items():
        model = SUBCATEGORY_TO_MODEL[subcategory.id]

        fields = _format_extra_data_fields(set(subcategory.conditional_fields))
        if fields:
            extra_data = _format_extra_data_fields(_parse_extra_data(model))

            if not extra_data:
                res.append(NoExtraData(subcategory_id=subcategory_name, fields=fields))
                continue

            formatted_fields = set(fields.keys())
            formatted_extra_data = set(extra_data.keys())

            if formatted_fields == formatted_extra_data:
                res.append(ExactMatch(subcategory_id=subcategory_name, fields=fields, extra_data=extra_data))
            elif formatted_fields < formatted_extra_data:
                diff = [extra_data[field] for field in (formatted_extra_data - formatted_fields)]
                res.append(
                    ExtraDataHasMore(subcategory_id=subcategory_name, fields=fields, extra_data=extra_data, diff=diff)
                )
            elif formatted_fields > formatted_extra_data:
                diff = [fields[field] for field in (formatted_fields - formatted_extra_data)]
                res.append(
                    SubcategoryHasMore(subcategory_id=subcategory_name, fields=fields, extra_data=extra_data, diff=diff)
                )
            else:
                diff = [
                    [fields[field] for field in (formatted_fields - formatted_extra_data)],
                    [extra_data[field] for field in (formatted_extra_data - formatted_fields)],
                ]
                res.append(
                    BothHaveMissing(subcategory_id=subcategory_name, fields=fields, extra_data=extra_data, diff=diff)
                )
    return res
