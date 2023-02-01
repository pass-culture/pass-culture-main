import enum
import json
import logging
import os
import pathlib

from algoliasearch.search_client import SearchClient
from algoliasearch.search_index import SearchIndex
import click

import pcapi
from pcapi import settings
from pcapi.utils.blueprint import Blueprint


ALGOLIA_SETTINGS_DIR = pathlib.Path(pcapi.__path__[0])
LOGGER = logging.getLogger(__name__)


blueprint = Blueprint(__name__, __name__)


class AlgoliaIndexError(Exception):
    pass


class IndexTypes(enum.Enum):
    offers = settings.ALGOLIA_OFFERS_INDEX_NAME
    collective_offers = settings.ALGOLIA_COLLECTIVE_OFFERS_INDEX_NAME
    venues = settings.ALGOLIA_VENUES_INDEX_NAME


def _get_index_default_file(index_type: IndexTypes) -> str:
    return os.path.join(ALGOLIA_SETTINGS_DIR, f"algolia_settings_{index_type.name.lower()}.json")


def _get_index_client(index_type: IndexTypes) -> SearchIndex:
    client = SearchClient.create(
        app_id=settings.ALGOLIA_APPLICATION_ID,
        api_key=settings.ALGOLIA_API_KEY,
    )
    index = client.init_index(index_type.value)
    return index


def _display_dry_warning(dry: bool) -> None:
    if dry:
        click.echo(" ".join(["/!\\"] * 16))
        click.echo("/!\\ DRY RUN (use --dry-run=false to actually apply effects) /!\\")
        click.echo(" ".join(["/!\\"] * 16))


def _get_settings(index: SearchIndex, dry: bool = False) -> list[str]:
    outputs = []

    if dry:
        outputs.append(f"settings of index {index.name} will be fetched from Algolia")
        outputs.append(f"settings of index {index.name} will be displayed")

    else:
        index_settings = index.get_settings()
        outputs.append(json.dumps(index_settings, indent=4))

    return outputs


def _set_settings(index: SearchIndex, path: str, dry: bool = True) -> list[str]:
    outputs = []

    outputs.extend(_get_settings(index, dry=dry))

    if dry:
        outputs.append(f"settings wil be read from {path}")
        outputs.append(f"settings will be applied to {index.name} Algolia index")

    else:
        with open(path, "r", encoding="utf-8") as fp:
            index_settings = json.load(fp)
        index.set_settings(index_settings)

    return outputs


@blueprint.cli.command("get_algolia_settings")
@click.argument("index_type_name", type=click.Choice([it.name for it in IndexTypes], case_sensitive=False))
def get_settings(index_type_name: str) -> None:
    try:
        index_type: IndexTypes = IndexTypes[index_type_name]
    except KeyError as err:
        raise AlgoliaIndexError(f"unknown index type '{index_type_name}'") from err

    index = _get_index_client(index_type)
    click.echo("\n".join(_get_settings(index)))


@blueprint.cli.command("set_algolia_settings")
@click.argument("index_type_name", type=click.Choice([it.name for it in IndexTypes], case_sensitive=False))
@click.option(
    "--path",
    help="the path of a file to be used as input",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    default=None,
)
@click.option(
    "--dry-run",
    help="default: true -> won't really apply modification until this options is set to false",
    type=bool,
    default=True,
)
def set_settings(index_type_name: str, path: str, dry_run: bool = True) -> None:
    try:
        index_type: IndexTypes = IndexTypes[index_type_name]
    except KeyError as err:
        raise AlgoliaIndexError(f"unknown index type '{index_type_name}'") from err

    index = _get_index_client(index_type)
    path = path or _get_index_default_file(index_type)
    _display_dry_warning(dry_run)
    click.echo("\n".join(_set_settings(index, path, dry_run)))
