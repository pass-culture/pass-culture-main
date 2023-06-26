from typing import Iterable

import click

from pcapi.scripts.offerer.generate_and_save_api_key_for_offerer import generate_and_save_api_key_for_offerer
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("generate_and_save_api_key")
@click.argument("sirens", nargs=-1, type=str, required=True)
def generate_and_save_api_key(sirens: Iterable[str]) -> None:
    generate_and_save_api_key_for_offerer(sirens)
