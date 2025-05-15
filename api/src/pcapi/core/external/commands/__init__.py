import click

from pcapi.utils.blueprint import Blueprint

from .update_brevo_batch_attributes import update_brevo_and_batch_loop
from .update_brevo_pro_attributes import update_brevo_pro_attributes


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("update_brevo_and_batch_users")
@click.option("--chunk-size", type=int, default=500, help="number of users to update in one query")
@click.option("--min-id", type=int, default=0, help="minimum user id")
@click.option("--max-id", type=int, default=0, help="maximum user id")
@click.option("--sync-brevo", is_flag=True, help="synchronize Brevo")
@click.option("--sync-batch", is_flag=True, help="synchronize Batch")
def update_brevo_and_batch_users(chunk_size: int, min_id: int, max_id: int, sync_brevo: bool, sync_batch: bool) -> None:
    update_brevo_and_batch_loop(chunk_size, min_id, max_id, sync_brevo, sync_batch)


@blueprint.cli.command("update_brevo_pro")
@click.option("--start-index", type=int, default=0, help="start index for resume (emails sorted alphabetically)")
def update_brevo_pro(start_index: int) -> None:
    update_brevo_pro_attributes(start_index=start_index)
