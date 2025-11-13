import difflib
import enum
import json
import logging
import os
import pathlib

import click

import pcapi
import pcapi.core.search.backends.algolia as algolia_backend
from pcapi import settings
from pcapi.utils.blueprint import Blueprint


ALGOLIA_SETTINGS_DIR = pathlib.Path(pcapi.__path__[0])
LOGGER = logging.getLogger(__name__)


blueprint = Blueprint(__name__, __name__)


class AlgoliaIndexError(Exception):
    pass


class IndexType(enum.Enum):
    artists = settings.ALGOLIA_ARTISTS_INDEX_NAME
    offers = settings.ALGOLIA_OFFERS_INDEX_NAME
    collective_offers = settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME
    venues = settings.ALGOLIA_VENUES_INDEX_NAME


def _get_index_default_file(index_type: IndexType) -> str:
    return os.path.join(ALGOLIA_SETTINGS_DIR, f"algolia_settings_{index_type.name.lower()}.json")


def _get_dict_diff(old: dict, new: dict) -> str:
    old_lines = json.dumps(old, indent=2, sort_keys=True).splitlines()
    new_lines = json.dumps(new, indent=2, sort_keys=True).splitlines()
    diff = "\n".join(difflib.unified_diff(old_lines, new_lines))
    return diff


def _get_settings(index: IndexType, not_dry: bool = True) -> list[str]:
    outputs = []

    if not_dry:
        backend = algolia_backend.AlgoliaBackend()
        index_settings = backend.get_settings(index.value)
        outputs.append(json.dumps(index_settings, indent=4))
    else:
        outputs.append(f"settings of index {index.value} will be fetched from Algolia")
        outputs.append(f"settings of index {index.value} will be displayed")

    return outputs


def _set_settings(index: IndexType, path: str, apply: bool = True) -> list[str]:
    backend = algolia_backend.AlgoliaBackend()
    outputs = []

    old_settings = backend.get_settings(index.value)
    with open(path, "r", encoding="utf-8") as fp:
        new_settings = json.load(fp)

    # we define "replicas" in some files but we want to apply the setting only on an index which already has replicas
    # e.g in testing or integration there is currently no replicas
    if "replicas" not in old_settings and "replicas" in new_settings:
        del new_settings["replicas"]

    diff = _get_dict_diff(old_settings, new_settings)
    outputs.append(diff)

    if apply:
        backend.set_settings(index.value, new_settings)

    return outputs


@blueprint.cli.command("get_algolia_settings")
@click.argument("index_type_name", type=click.Choice([it.name for it in IndexType], case_sensitive=False))
def get_settings(index_type_name: str) -> None:
    try:
        index_type: IndexType = IndexType[index_type_name]
    except KeyError as err:
        raise AlgoliaIndexError(f"unknown index type '{index_type_name}'") from err

    click.echo("\n".join(_get_settings(index_type)))


@blueprint.cli.command("set_algolia_settings")
@click.argument("index_type_name", type=click.Choice([it.name for it in IndexType], case_sensitive=False))
@click.option(
    "--path",
    help="the path of a file to be used as input",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    default=None,
)
@click.option("--apply", is_flag=True, default=False, help="apply the settings changes")
def set_settings(index_type_name: str, path: str, apply: bool = False) -> None:
    try:
        index_type: IndexType = IndexType[index_type_name]
    except KeyError as err:
        raise AlgoliaIndexError(f"unknown index type '{index_type_name}'") from err

    path = path or _get_index_default_file(index_type)
    if not apply:
        click.echo(" ".join(["/!\\"] * 16))
        click.echo("/!\\ DRY RUN (use --not-dry to actually apply effects) /!\\")
        click.echo(" ".join(["/!\\"] * 16))
        click.echo(f"settings will be read from {path}")
        click.echo(f"settings will be applied to {index_type.value} Algolia index")
    click.echo("\n".join(_set_settings(index_type, path, apply)))
