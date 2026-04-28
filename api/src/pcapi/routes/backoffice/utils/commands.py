import logging

import click

from pcapi.routes.backoffice.utils import static as static_utils
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("compile", help="Compile static resources for backoffice")
@click.argument(
    "module",
    type=click.Choice(("css", "js", "all"), case_sensitive=False),
    required=True,
)
def compile(module: str) -> None:
    if module in ("all", "css"):
        static_utils.preprocess_scss()
        static_utils.generate_bundle(static_utils.CSS_FILES, static_utils.CSS_BUNDLE)
    if module in ("all", "js"):
        static_utils.generate_bundle(static_utils.JS_FILES, static_utils.JS_BUNDLE)
