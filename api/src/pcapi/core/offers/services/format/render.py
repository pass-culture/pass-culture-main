import os
from pathlib import Path

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from pcapi.core.offers.services import utils

from . import tools


env = Environment(
    loader=PackageLoader("pcapi.core.offers.services.format", "templates"), autoescape=select_autoescape()
)


# HierarchyCache = dict[str, set[types.Field]]


# @dataclass(frozen=True)
# class Hierarchy:
    # mandatory: set[types.Field]
    # base: set[types.Field]
    # other: set[types.Field]


# class FieldOrigin(enum.Enum):
    # MANDATORY = "mandatory"
    # BASE = "base"
    # INHERITED = "inherited"
    # OWN = "own"

    # def __lt__(self, other: typing.Self) -> bool:
        # cls = type(self)

        # match self:
            # case cls.MANDATORY:
                # return True
            # case cls.BASE:
                # return other in (cls.INHERITED, cls.OWN)
            # case cls.INHERITED:
                # return other is cls.OWN
            # case _:
                # return other == cls.OWN


# @dataclass(frozen=True)
# class FieldWithOrigin(types.Field):
    # origin: FieldOrigin = FieldOrigin.OWN

    # @classmethod
    # def from_field(cls, field: types.Field, origin: FieldOrigin) -> typing.Self:
        # return cls.build(
            # name=field.name,
            # optional=field.optional,
            # components=field.components,
            # origin=origin
        # )


# @dataclass(frozen=True)
# class Properties:
    # required: typing.Collection[types.Field]
    # optional: typing.Collection[types.Field] = field(default_factory=list)


# @dataclass(frozen=True)
# class ModelSchema:
    # subcategory: Subcategory
    # properties: Properties


def to_html(schemas) -> str:
    template = env.get_template("index.tmpl.html")

    base_dir = os.path.dirname(__file__)
    out_path = Path(base_dir) / "templates" / "index.html"

    with open(out_path, mode="w") as f:
        content = template.render(schemas=schemas)
        f.write(content)

    return content


def all_subcategories_to_html() -> str:
    models = [item.model for item in utils.stream_flattened_subcategories_models()]
    schemas = tools.build_schemas(models)
    return to_html(schemas)


# def build_schemas(models: typing.Collection[Base]) -> typing.Collection[types.ModelSchema]:
    # cache = {}
    # schemas = []

    # for model in models:
        # schema, cache = format_model_to_schema(cache, model)
        # schemas.append(schema)

    # return sorted(schemas, key=lambda s: s.subcategory.id)


# def format_model_to_schema(cache: types.HierarchyCache, model: Base) -> (types.ModelSchema, types.HierarchyCache):
    # subcategory_id = typing.get_args(model.model_fields["subcategory_id"].annotation)[0]
    # subcategory = ALL_SUBCATEGORIES_DICT[subcategory_id]

    # parsed_properties = parse.build_model_fields(model)

    # required_fields = [p for p in parsed_properties if not p.optional]
    # optional_fields = [p for p in parsed_properties if p.optional]

    # hierarchy, cache = build_model_hierarchy(cache, model)

    # required = [build_field_with_origin(hierarchy, field) for field in required_fields]
    # optional = [build_field_with_origin(hierarchy, field) for field in optional_fields]

    # schema = types.ModelSchema(
        # subcategory=subcategory,
        # properties=types.Properties(
            # required=sort_fields_with_origin(required),
            # optional=sort_fields_with_origin(optional)
        # )
    # )

    # return schema, cache


# def build_model_hierarchy(cache: types.HierarchyCache, model: Base) -> (types.Hierarchy, types.HierarchyCache):
    # """Build a model's `Hierarchy` object

    # The cache is used to avoid parsing the same parent classes twice
    # (eg. top classes like `Mandatory` or `Base`) and is updated
    # for next calls.
    # """
    # updated_cache = cache | dig_model_hierarchy(cache, model)

    # mandatory = updated_cache.pop("Mandatory")
    # base = updated_cache.pop("Base") - mandatory
    # other = {field for fields in updated_cache.values() for field in fields} - base - mandatory

    # return types.Hierarchy(mandatory=mandatory, base=base, other=other), updated_cache


# def update_global_model_hierarchy_cache(cache: types.HierarchyCache, model: Base) -> types.HierarchyCache:
    # """Update the global cache hierarchy with one model

    # Compute the model's full class hierarchy using already known classes
    # and update the cache with missing classes.
    # """
    # updated_cache = {}

    # # stop recursive calls here: there is no need to go further
    # # the model hierarchy
    # if model is Mandatory:
        # return updated_cache

    # # __bases__ contains the model's parent classes
    # # there should be only one is this context
    # for b in model.__bases__:
        # if b not in cache:
            # updated_cache[b.__name__] = parse.build_model_fields(b)
            # updated_cache.update(fetch_model_hierarchy(cache, b))

    # return updated_cache


# def build_field_with_origin(hierarchy: types.Hierarchy, field: types.Field) -> types.FieldWithOrigin:
    # if field in hierarchy.mandatory:
        # return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.MANDATORY)
    # elif field in hierarchy.base:
        # return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.BASE)
    # elif field in hierarchy.other:
        # return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.INHERITED)
    # return types.FieldWithOrigin.from_field(field, origin=types.FieldOrigin.OWN)


# def sort_fields_with_origin(fields: typing.Collection[types.FieldWithOrigin]) -> typing.Collection[types.FieldWithOrigin]:
    # """First sort by origin, and then sort by name within each group"""
    # sorted_by_origin = sorted(fields, key=lambda f: f.origin)
    # grouped_by_origin = itertools.groupby(sorted_by_origin, key=lambda f: f.origin)

    # nested_fields = [sorted(fields, key=lambda f: f.name) for _, fields in grouped_by_origin]
    # return [field for group in nested_fields for field in group]
