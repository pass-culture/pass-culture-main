import click

from pcapi import settings
from pcapi.sandboxes.scripts.save_sandbox import save_sandbox
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("sandbox")
@click.option("-n", "--name", help="Sandbox name", default="classic")
@click.option("-c", "--clean", help="Clean database first", default="true")
@click.option("-cb", "--clean-bucket", help="Clean mediation bucket", default="false")
def sandbox(name: str, clean: str, clean_bucket: str) -> None:
    if settings.CAN_RUN_SANDBOX:
        with_clean = clean == "true"
        with_clean_bucket = clean_bucket == "true"
        save_sandbox(name, with_clean, with_clean_bucket)
    else:
        print("Sandbox is disabled on this environment")
