import logging

import click

from pcapi.core.geography.api import import_iris_from_7z
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("import_iris")
@click.option(
    "--path",
    type=str,
    help="Path to the 7z file from ign containing the iris data",
    required=True,
)
def import_iris(path: str) -> None:
    import_iris_from_7z(path)
