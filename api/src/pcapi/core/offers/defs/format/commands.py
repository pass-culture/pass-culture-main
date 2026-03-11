from pcapi.utils.blueprint import Blueprint

from . import render


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("export_new_offers_defs_to_html")
def export_new_offers_defs_to_html() -> None:
    render.all_subcategories_to_html()
