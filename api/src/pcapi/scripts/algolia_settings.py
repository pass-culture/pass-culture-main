import json
import logging
import os

from algoliasearch.search_client import SearchClient
from algoliasearch.search_index import SearchIndex
import click

from pcapi import settings as pcapi_settings
from pcapi.utils.blueprint import Blueprint


ALGOLIA_SETTINGS_DIR = os.path.abspath(
    os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
        )
    )
)  # pass-culture-main/api/src/pcapi
ALGOLIA_SETTINGS_DEFAULT_FILE = os.path.join(ALGOLIA_SETTINGS_DIR, "algolia_settings.json")
LOGGER = logging.getLogger(__name__)


blueprint = Blueprint(__name__, __name__)


def _ensure_settings_dir_exists() -> None:
    os.makedirs(ALGOLIA_SETTINGS_DIR, exist_ok=True)


def _get_index_client(index_name: str) -> SearchIndex:
    _ensure_settings_dir_exists()
    client = SearchClient.create(
        app_id=pcapi_settings.ALGOLIA_APPLICATION_ID,
        api_key=pcapi_settings.ALGOLIA_API_KEY,
    )
    index = client.init_index(index_name)
    return index


def _display_dry_warning(dry: bool) -> None:
    if dry:
        click.echo(" ".join(["/!\\"] * 16))
        click.echo("/!\\ DRY RUN (use --dry-run=false to actually apply effects) /!\\")
        click.echo(" ".join(["/!\\"] * 16))


def _get_settings(index: SearchIndex, dry: bool = True) -> list[str]:
    outputs = []

    if dry:
        outputs.append(f"settings of index {index.name} will be fetched from Algolia")
        outputs.append(f"settings of index {index.name} will be displayed")

    else:
        settings = index.get_settings()
        outputs.append(json.dumps(settings, indent=4))

    return outputs


def _set_settings(index: SearchIndex, path: str, dry: bool = True) -> list[str]:
    outputs = []

    outputs.extend(_get_settings(index, dry=dry))

    if dry:
        outputs.append(f"settings wil be read from {path}")
        outputs.append(f"settings will be applied to {index.name} Algolia index")

    else:
        with open(path, "r", encoding="utf-8") as fp:
            settings = json.load(fp)
        index.set_settings(settings)

    return outputs


@blueprint.cli.group("algolia_settings")
@click.argument("index", type=str)
@click.option(
    "--dry-run",
    help="default: true -> won't really apply modification until this options is set to false",
    type=bool,
    default=True,
)
@click.pass_context
def algolia_settings_command(ctx: click.Context, index: str, dry_run: bool) -> None:
    ctx.ensure_object(dict)

    ctx.obj["index"] = _get_index_client(index)
    ctx.obj["dry_run"] = dry_run

    _display_dry_warning(dry_run)


@algolia_settings_command.command("get")
@click.pass_context
def get_settings(ctx: click.Context) -> None:
    index = ctx.obj["index"]
    dry = ctx.obj["dry_run"]

    click.echo("\n".join(_get_settings(index, dry)))


@algolia_settings_command.command("set")
@click.option(
    "--path",
    help="the path of a file to be used as input",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    default=ALGOLIA_SETTINGS_DEFAULT_FILE,
)
@click.pass_context
def set_settings(ctx: click.Context, path: str) -> None:
    index = ctx.obj["index"]
    dry = ctx.obj["dry_run"]

    click.echo("\n".join(_set_settings(index, path, dry)))
