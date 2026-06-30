from pathlib import Path

import click

from pcapi.utils.blueprint import Blueprint

from . import render


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("export_new_offers_defs_to_html")
@click.argument("path", required=False, type=str, default=None)
def export_new_offers_defs_to_html(path: str | None = None) -> None:
    dst = Path(path) if path else None
    render.all_subcategories_to_html(dst)
