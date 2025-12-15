import os
import typing
from pathlib import Path

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from pcapi.core.offers.services import utils

from . import tools
from . import types


env = Environment(
    loader=PackageLoader("pcapi.core.offers.services.format", "templates"), autoescape=select_autoescape()
)


def to_html(schemas: typing.Collection[types.ModelSchema]) -> str:
    template = env.get_template("index.tmpl.html")

    base_dir = os.path.dirname(__file__)
    out_path = Path(base_dir) / "templates" / "index.html"

    with open(out_path, mode="w") as f:
        content = template.render(schemas=schemas)
        f.write(content)

    return content


def all_subcategories_to_html() -> str:
    schemas = tools.build_schemas(utils.MODELS.values())
    return to_html(schemas)
