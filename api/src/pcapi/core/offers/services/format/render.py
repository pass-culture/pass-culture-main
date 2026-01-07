import enum
import itertools
import os
import typing
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
from pcapi.core.categories.subcategories import Subcategory
from pcapi.core.offers.services.consistency_checks import parse
from pcapi.core.offers.services.consistency_checks import types
from pcapi.core.offers.services.models.base import Base
from pcapi.core.offers.services.models.base import Mandatory


env = Environment(
    loader=PackageLoader("pcapi.core.offers.services.format", "templates"), autoescape=select_autoescape()
)


HierarchyCache = dict[str, set[types.Field]]


@dataclass(frozen=True)
class Hierarchy:
    mandatory: set[types.Field]
    base: set[types.Field]
    other: set[types.Field]


class FieldOrigin(enum.Enum):
    MANDATORY = "mandatory"
    BASE = "base"
    INHERITED = "inherited"
    OWN = "own"

    def __lt__(self, other: typing.Self) -> bool:
        cls = type(self)

        match self:
            case cls.MANDATORY:
                return True
            case cls.BASE:
                return other in (cls.INHERITED, cls.OWN)
            case cls.INHERITED:
                return other is cls.OWN
            case _:
                return other == cls.OWN


@dataclass(frozen=True)
class FieldWithOrigin(types.Field):
    origin: FieldOrigin = FieldOrigin.OWN

    @classmethod
    def from_field(cls, field: types.Field, origin: FieldOrigin) -> typing.Self:
        return cls(name=field.name, optional=field.optional, components=field.components, origin=origin)


@dataclass(frozen=True)
class Properties:
    required: typing.Collection[types.Field]
    optional: typing.Collection[types.Field] = field(default_factory=list)


@dataclass(frozen=True)
class ModelSchema:
    subcategory: Subcategory
    properties: Properties


def extract_defs_from_schemas(schemas: typing.Collection[ModelSchema]) -> typing.Collection[ModelSchema]:
    def _extract(schemas: typing.Collection[ModelSchema]) -> typing.Generator[types.OrField]:
        seen = set()

        for schema in schemas:
            for required_field in schema.properties.required:
                for component in required_field.components:
                    if isinstance(component, types.OrField):
                        if component.name not in seen:
                            seen.add(component.name)
                            yield component

    return list(_extract(schemas))


def to_html(schemas, defs) -> str:
    template = env.get_template("index.tmpl.html")

    base_dir = os.path.dirname(__file__)
    out_path = Path(base_dir) / "templates" / "index.html"

    with open(out_path, mode="w") as f:
        content = template.render(schemas=schemas, defs=defs)
        f.write(content)

    return content


def format_model_to_schema(cache: HierarchyCache, model: Base) -> (ModelSchema, HierarchyCache):
    subcategory_id = typing.get_args(model.model_fields["subcategory_id"].annotation)[0]
    subcategory = ALL_SUBCATEGORIES_DICT[subcategory_id]

    parsed_properties = parse.model_full(model)

    required_fields = [p for p in parsed_properties if not p.optional]
    optional_fields = [p for p in parsed_properties if p.optional]

    hierarchy, cache = build_model_hierarchy(cache, model)

    required = sort_fields_with_origin([build_field_with_origin(hierarchy, field) for field in required_fields])
    optional = sort_fields_with_origin([build_field_with_origin(hierarchy, field) for field in optional_fields])

    return ModelSchema(subcategory=subcategory, properties=Properties(required=required, optional=optional)), cache


def build_schemas(models: typing.Collection[Base]) -> typing.Collection[ModelSchema]:
    cache = {}
    schemas = []

    for model in models:
        schema, cache = format_model_to_schema(cache, model)
        schemas.append(schema)

    return sorted(schemas, key=lambda s: s.subcategory.id)


def fetch_model_hierarchy(cache: HierarchyCache, model: Base) -> HierarchyCache:
    res = {}

    # safety check in case function is called for Mandatory
    # although it should not
    if model is Mandatory:
        return res

    for b in model.__bases__:
        if b not in cache:
            res[b.__name__] = parse.model_full(b)
            res.update(fetch_model_hierarchy(cache, b))
        if b is Mandatory:
            break

    return res


def build_model_hierarchy(cache: HierarchyCache, model: Base) -> (Hierarchy, HierarchyCache):
    updated_cache = cache | fetch_model_hierarchy(cache, model)

    mandatory = updated_cache.pop("Mandatory")
    base = updated_cache.pop("Base") - mandatory
    other = {field for fields in updated_cache.values() for field in fields} - base - mandatory

    return Hierarchy(mandatory=mandatory, base=base, other=other), updated_cache


def build_field_with_origin(hierarchy: Hierarchy, field: types.Field) -> FieldWithOrigin:
    if field in hierarchy.mandatory:
        return FieldWithOrigin.from_field(field, origin=FieldOrigin.MANDATORY)
    elif field in hierarchy.base:
        return FieldWithOrigin.from_field(field, origin=FieldOrigin.BASE)
    elif field in hierarchy.other:
        return FieldWithOrigin.from_field(field, origin=FieldOrigin.INHERITED)
    return FieldWithOrigin.from_field(field, origin=FieldOrigin.OWN)


def sort_fields_with_origin(fields: typing.Collection[FieldWithOrigin]) -> typing.Collection[FieldWithOrigin]:
    sorted_by_origin = sorted(fields, key=lambda f: f.origin)
    grouped_by_origin = itertools.groupby(sorted_by_origin, key=lambda f: f.origin)

    nested_fields = [sorted(fields, key=lambda f: f.name) for _, fields in grouped_by_origin]
    return [field for group in nested_fields for field in group]
