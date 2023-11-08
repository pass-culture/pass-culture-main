import click

from pcapi import settings
from pcapi.sandboxes.scripts.save_sandbox import save_sandbox
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("sandbox")
@click.option("-n", "--name", help="Sandbox name", default="classic")
@click.option("-c", "--clean", help="Clean database first", default="true")
def sandbox(name: str, clean: str) -> None:
    if settings.CAN_RUN_SANDBOX:
        with_clean = clean == "true"
        save_sandbox(name, with_clean)
    else:
        print("Sandbox is disabled on this environment")
