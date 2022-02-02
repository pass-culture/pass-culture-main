import click
from flask import Blueprint

from .unstack_batch_cloud_task_queue import unstack_batch_queue


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("unstack_batch_queue")
@click.option("--queue-name", required=True, help="Queue name (not full path)", type=str)
@click.option("--chunk-size", required=False, default=1_000, help="Number of users per request (Batch API)", type=int)
@click.option(
    "--sleep", required=False, default=2.0, help="Number of seconds between each request the the Batch API", type=float
)
def run_unstack_batch_queue(queue_name: str, chunk_size: int, sleep: float) -> None:
    tasks_to_delete, deleted_tasks = unstack_batch_queue(queue_name, chunk_size, sleep)

    missing_tasks = tasks_to_delete - deleted_tasks
    if missing_tasks:
        print(f"unstack_batch_queue: {deleted_tasks} tasks processed and deleted")
    else:
        print(
            f"unstack_batch_queue: {deleted_tasks} tasks processed and deleted"
            f", {len(missing_tasks)} missing ({missing_tasks})"
        )
