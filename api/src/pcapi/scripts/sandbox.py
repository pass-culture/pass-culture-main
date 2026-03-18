import click

from pcapi import settings
from pcapi.sandboxes.scripts.save_sandbox import save_sandbox
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("sandbox")
@click.option("-n", "--name", help="Sandbox name", default=["classic"], multiple=True)
@click.option("-c", "--clean", help="Clean database first", default="true")
@click.option("-cb", "--clean-bucket", help="Clean mediation bucket", default="false")
@click.option("-ix", "--index", help="Index all offers, venues and artists", default="true")
@click.option("-sts", "--step-to-skip", help="Name of function to skip. Can provide multiple values", multiple=True)
def sandbox(name: tuple[str], clean: str, clean_bucket: str, index: str, step_to_skip: tuple[str]) -> None:
    if settings.CAN_RUN_SANDBOX:
        with_clean = clean == "true"
        with_clean_bucket = clean_bucket == "true"
        with_indexing = index == "true"
        save_sandbox(name, with_clean, with_clean_bucket, with_indexing, step_to_skip)
    else:
        print("Sandbox is disabled on this environment")
