from typing import Iterable

import click

from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id
from pcapi.scripts.offerer.generate_and_save_api_key_for_offerer import generate_and_save_api_key_for_offerer
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("delete_offerer")
@click.option("--offerer-id", required=True, help="Id of the offerer to cascade delete", type=int)
def delete_offerer(offerer_id: int) -> None:
    delete_cascade_offerer_by_id(offerer_id)


@blueprint.cli.command("delete_venue")
@click.option("--venue-id", required=True, help="Id of the venue to cascade delete", type=int)
def delete_venue(venue_id: int) -> None:
    delete_cascade_venue_by_id(venue_id)


@blueprint.cli.command("generate_and_save_api_key")
@click.argument("sirens", nargs=-1, type=str, required=True)
def generate_and_save_api_key(sirens: Iterable[str]) -> None:
    generate_and_save_api_key_for_offerer(sirens)
