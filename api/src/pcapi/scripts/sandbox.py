import click
import sqlalchemy as sa
from sqlalchemy import exc as sa_exc

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
@click.option("-rd", "--restore-dump", help="Restore the industrial sandbox from its dump", default="false")
@click.option("-ud", "--update-dump", help="Run the industrial sandbox scripts, then update its dump", default="false")
def sandbox(
    name: tuple[str],
    clean: str,
    clean_bucket: str,
    index: str,
    step_to_skip: tuple[str],
    restore_dump: str,
    update_dump: str,
) -> None:
    if settings.CAN_RUN_SANDBOX:
        if not sa.inspect(db.engine).has_table("alembic_version"):
            raise click.ClickException(
                "The database has no schema: run `alembic upgrade pre@head && alembic upgrade post@head` first"
            )
        with_clean = clean == "true"
        with_clean_bucket = clean_bucket == "true"
        with_indexing = index == "true"
        with_restore_dump = restore_dump == "true"
        with_update_dump = update_dump == "true"
        is_full_industrial_sandbox = name == ("industrial",) and not step_to_skip and with_clean
        if with_restore_dump and with_update_dump:
            raise click.UsageError("--restore-dump and --update-dump cannot be used together")
        if (with_restore_dump or with_update_dump) and not is_full_industrial_sandbox:
            raise click.UsageError(
                "--restore-dump and --update-dump only apply to `-n industrial`, with all its steps and cleaning"
            )

        if with_restore_dump:
            try:
                restore_industrial_sandbox(with_clean_bucket, with_indexing)
            except (dump.DumpError, sa_exc.SQLAlchemyError) as error:
                raise click.ClickException(
                    f"Could not restore the industrial sandbox dump: {str(error).splitlines()[0]}\n"
                    "The dumped tables may have been emptied: run the command without `--restore-dump true`"
                    " to seed the sandbox with its scripts."
                )
        else:
            save_sandbox(name, with_clean, with_clean_bucket, with_indexing, step_to_skip)

        if with_update_dump:
            try:
                dump.write_dump(settings.SANDBOX_POSTGRES_CONTAINER, db.engine.url.render_as_string())
            except dump.DumpError as error:
                raise click.ClickException(f"Could not update the industrial sandbox dump: {error}")
    else:
        print("Sandbox is disabled on this environment")
