import os
import typing
from pathlib import Path

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from pcapi.core.offers.defs import utils

from . import tools
from . import types


env = Environment(loader=PackageLoader("pcapi.core.offers.defs.format", "templates"), autoescape=select_autoescape())


def to_html(schemas: typing.Collection[types.ModelSchema], dst: Path | None = None) -> str:
    template = env.get_template("index.tmpl.html")

    if not dst:
        base_dir = os.path.dirname(__file__)
        dst = Path(base_dir) / "templates" / "index.html"

    with open(dst, mode="w") as f:
        content = template.render(schemas=schemas)
        f.write(content)

    return content


def all_subcategories_to_html(dst: Path | None = None) -> str:
    schemas = tools.build_schemas(utils.MODELS.values())
    return to_html(schemas, dst)
