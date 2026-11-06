import click

from pcapi import settings
from pcapi.models import db
from pcapi.sandboxes import dump
from pcapi.sandboxes.scripts.save_sandbox import restore_industrial_sandbox
from pcapi.sandboxes.scripts.save_sandbox import save_sandbox
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("sandbox")
@click.option("-n", "--name", help="Sandbox name", default=["classic"], multiple=True)
@click.option("-c", "--clean", help="Clean database first", default="true")
@click.option("-cb", "--clean-bucket", help="Clean mediation bucket", default="false")
@click.option("-ix", "--index", help="Index all offers, venues and artists", default="true")
@click.option("-sts", "--step-to-skip", help="Name of function to skip. Can provide multiple values", multiple=True)
@click.option("-nd", "--no-dump", help="Run the industrial sandbox scripts, not its dump", default="false")
@click.option("-ud", "--update-dump", help="Run the industrial sandbox scripts, then update its dump", default="false")
def sandbox(
    name: tuple[str],
    clean: str,
    clean_bucket: str,
    index: str,
    step_to_skip: tuple[str],
    no_dump: str,
    update_dump: str,
) -> None:
    if settings.CAN_RUN_SANDBOX:
        with_clean = clean == "true"
        with_clean_bucket = clean_bucket == "true"
        with_indexing = index == "true"
        is_full_industrial_sandbox = name == ("industrial",) and not step_to_skip and with_clean
        if update_dump == "true":
            if not is_full_industrial_sandbox:
                raise click.UsageError("--update-dump only applies to `-n industrial`, with all its steps and cleaning")
            save_sandbox(name, with_clean, with_clean_bucket, with_indexing)
            try:
                dump.write_dump(settings.SANDBOX_POSTGRES_CONTAINER, db.engine.url.render_as_string())
            except dump.DumpError as error:
                raise click.ClickException(f"Could not update the industrial sandbox dump: {error}")
        elif not (
            is_full_industrial_sandbox
            and no_dump != "true"
            and restore_industrial_sandbox(with_clean_bucket, with_indexing)
        ):
            save_sandbox(name, with_clean, with_clean_bucket, with_indexing, step_to_skip)
    else:
        print("Sandbox is disabled on this environment")
