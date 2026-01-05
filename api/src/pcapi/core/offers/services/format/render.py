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


env = Environment(
    loader=PackageLoader("pcapi.core.offers.services.format", "templates"), autoescape=select_autoescape()
)


@dataclass
class Properties:
    required: typing.Collection[types.Field]
    optional: typing.Collection[types.Field] = field(default_factory=list)


@dataclass
class ModelSchema:
    subcategory: Subcategory
    properties: typing.Collection[types.Field]


def to_html(schemas) -> str:
    template = env.get_template("index.tmpl.html")

    base_dir = os.path.dirname(__file__)
    out_path = Path(base_dir) / "templates" / "index.html"

    with open(out_path, mode="w") as f:
        content = template.render(schemas=schemas)
        f.write(content)

    return content


def format_model(model: Base) -> ModelSchema:
    subcategory_id = typing.get_args(model.model_fields["subcategory_id"].annotation)[0]
    subcategory = ALL_SUBCATEGORIES_DICT[subcategory_id]

    props = parse.model_full(model)
    properties = Properties(required=[p for p in props if not p.optional], optional=[p for p in props if not p.optional])

    return ModelSchema(subcategory=subcategory, properties=properties)


def format_models(models: typing.Collection[Base]) -> typing.Collection[ModelSchema]:
    schemas = [format_model(model) for model in models]
    return sorted(schemas, key=lambda s: s.subcategory.pro_label)

