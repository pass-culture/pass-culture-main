import click

from pcapi import settings
from pcapi.sandboxes.scripts.save_sandbox import save_sandbox
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("sandbox")
@click.option("-n", "--name", help="Sandbox name", default=["classic"], multiple=True)
@click.option("-c", "--clean", help="Clean database first", default="true")
@click.option("-cb", "--clean-bucket", help="Clean mediation bucket", default="false")
@click.option("-iao", "--index-all-offers", help="Index all offers", default="true")
@click.option(
    "-sts",
    "--step-to-skip",
    help="Name of function to skip. Can provide multiple values. Cannot be used with --step-to-run",
    multiple=True,
)
@click.option(
    "-str",
    "--step-to-run",
    help="Name of function to run. Can provide multiple values. Cannot be used with --step-to-skip",
    multiple=True,
)
def sandbox(
    name: tuple[str],
    clean: str,
    clean_bucket: str,
    index_all_offers: str,
    step_to_skip: tuple[str],
    step_to_run: tuple[str],
) -> None:
    if settings.CAN_RUN_SANDBOX:
        with_clean = clean == "true"
        with_clean_bucket = clean_bucket == "true"
        with_index_all_offers = index_all_offers == "true"
        save_sandbox(name, with_clean, with_clean_bucket, with_index_all_offers, step_to_skip, step_to_run)
    else:
        print("Sandbox is disabled on this environment")
