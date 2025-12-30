from dataclasses import dataclass
import typing

import pydantic as pydantic_v2

from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT

from . import SUBCATEGORY_TO_MODEL
from . import utils


def all_subcategories_are_modeled() -> bool:
    flatten_mappings = {row.subcategory_id for row in utils.stream_flattened_subcategories_models()}
    return flatten_mappings == ALL_SUBCATEGORIES_DICT.keys()


@dataclass
class ExtraDataField:
    name: str
    mandatory: bool
    default: typing.Any


def _parse_extra_data(model: pydantic_v2.BaseModel) -> dict:
    def _parse(defs, v):
        match v:
            case {"anyOf": choices}:
                breakpoint()
                yield from _parse(defs, choices)
            case [*options]:
                breakpoint()
                for opt in options:
                    yield from _parse(defs, opt)
            case {"$ref": ref}:
                breakpoint()
                yield from _parse(defs, defs[ref.replace("#/$defs/", "")])
            case {"properties": props}:
                breakpoint()
                yield from props
            case x:
                print(x)
                breakpoint()
                pass

    # def _parse_properties(defs, v):
        # match v:
            # case {""}

    schema = model.model_json_schema()
    defs = schema["$defs"]
    extra_data_properties = schema["properties"].get("extra_data")
    if not extra_data_properties:
        return set()

    return set(_parse(defs, extra_data_properties))


def _format_extra_data_fields(fields: typing.Collection[str]) -> dict[str, str]:
    return {field.lower().replace("_", ""): field for field in fields}


class Fields:
    def __init__(self, mandatory: set, optional: set):
        self.mandatory = mandatory
        self.mandatory_mapper = _format_extra_data_fields(mandatory)
        self.mandatory_formatted = set(self.mapper.keys()) if self.mapper else set()

        self.optional = optional
        self.optional_mapper = _format_extra_data_fields(optional)
        self.optional_formatted = set(self.mapper.keys()) if self.mapper else set()

    def is_empty(self) -> bool:
        return (len(self.mandatory) == 0 + len(self.optional)) == 0

    def __eq__(self, other: typing.Self) -> bool:
        return (
            (self.mandatory_formatted == other.mandatory_formatted)
            and (self.optional_formatted == other.optional_formatted)
        )

    def __lt__(self, other: typing.Self) -> bool:
        return (
            (self.mandatory_formatted < other.mandatory_formatted)
            or (self.optional_formatted < other.optional_formatted)
        )

    def __gt__(self, other: typing.Self) -> bool:
        return (
            (self.mandatory_formatted > other.mandatory_formatted)
            or (self.optional_formatted > other.optional_formatted)
        )

    def __getitem__(self, k: str) -> str:
        return self.mandatory_mapper[k]

    def __sub__(self, other: typing.Self) -> typing.Self:
        return type(self)(
            {self.mandatory_mapper[m] for m in (self.mandatory_formatted - other.mandatory_formatted)},
            {self.optional_formatted[o] for o in (self.optional_formatted - other.optional_formatted)},
        )

    def __repr__(self) -> str:
        return f"Fields({self.mandatory}, {self.optional})"



class FieldsCompare:
    kind = "base"

    def __init__(self, subcategory_id: str, fields: dict, extra_data: dict | None = None):
        self.subcategory_id = subcategory_id
        self.fields = fields
        self.extra_data = extra_data if extra_data else set()

        self.set_diff()

    def set_diff(self):
        return set()

    def print_with_diff(self) -> str:
        return f"{self.__class__.__name__}(subcategory_id={self.subcategory_id}, diff={self.diff}"


    def __lt__(self, other: "FieldsCompare") -> bool:
        """Enable arbitrary sorting between FieldsCompare classes

        ExactMatch > ExtraDataHasMore > SubcategoryHasMore > BothHaveMissing
        """
        return type(other) is not type(self)

    def __repr__(self):
        return f"{self.__class__.__name__}(subcategory_id={self.subcategory_id}, fields={self.fields}, extra_data={self.extra_data}"


class ExactMatch(FieldsCompare):
    kind = "exact"


class ExtraDataHasMore(FieldsCompare):
    kind = "diff"

    def set_diff(self):
        self.diff = [self.extra_data[field] for field in (self.extra_data - self.fields)]

    def __lt__(self, other: "FieldsCompare") -> bool:
        return type(other) is ExactMatch


class SubcategoryHasMore(FieldsCompare):
    kind = "diff"

    def set_diff(self) -> None:
        self.diff = [self.fields[field] for field in (self.fields - self.extra_data)]

    def __lt__(self, other: "FieldsCompare") -> bool:
        return type(other) in (ExactMatch, ExtraDataHasMore)


class BothHaveMissing(FieldsCompare):
    kind = "diff"

    def set_diff(self) -> None:
        self.diff = {
            "fields": [self.fields[field] for field in (self.fields - self.extra_data)],
            "extra_data": [self.extra_data[field] for field in (self.extra_data - self.fields)],
        }

    def __lt__(self, other: "FieldsCompare") -> bool:
        return type(other) in (ExactMatch, ExtraDataHasMore, SubcategoryHasMore)


def extra_data_are_mapped() -> bool:
    res = []

    for subcategory_name, subcategory in ALL_SUBCATEGORIES_DICT.items():
        model = SUBCATEGORY_TO_MODEL[subcategory.id]

        extra_data = Fields(_parse_extra_data(model), set())
        fields = Fields(set(subcategory.conditional_fields), set())

        if fields == extra_data:
            res.append(ExactMatch(subcategory_name, fields=fields, extra_data=extra_data))
        elif fields < extra_data:
            res.append(ExtraDataHasMore(subcategory_name, fields=fields, extra_data=extra_data))
        elif fields > extra_data:
            res.append(SubcategoryHasMore(subcategory_name, fields=fields, extra_data=extra_data))
        else:
            res.append(BothHaveMissing(subcategory_name, fields=fields, extra_data=extra_data))

    return res
