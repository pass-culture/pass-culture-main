import click

from pcapi.core import search
import pcapi.core.educational.api as educational_api
import pcapi.core.offers.api as offers_api
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_venues_in_algolia_from_database
from pcapi.tasks import search_tasks
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("process_offers")
def process_offers():  # type: ignore [no-untyped-def]
    search.index_offers_in_queue(stop_only_when_empty=True)


@blueprint.cli.command("process_offers_by_venue")
def process_offers_by_venue():  # type: ignore [no-untyped-def]
    search.index_offers_of_venues_in_queue()


@blueprint.cli.command("process_offers_from_database")
@click.option("--clear", help="Clear search index", type=bool, default=False)
@click.option("-ep", "--ending-page", help="Ending page for indexing offers", type=int, default=None)
@click.option("-l", "--limit", help="Number of offers per page", type=int, default=10_000)
@click.option("-sp", "--starting-page", help="Starting page for indexing offers", type=int, default=0)
def process_offers_from_database(  # type: ignore [no-untyped-def]
    clear: bool,
    ending_page: int,
    limit: int,
    starting_page: int,
):
    if clear:
        search.unindex_all_offers()
    batch_indexing_offers_in_algolia_from_database(ending_page=ending_page, limit=limit, starting_page=starting_page)


@blueprint.cli.command("process_expired_offers")
@click.option("-a", "--all", help="Bypass the two days limit to delete all expired offers", default=False)
def process_expired_offers(all_offers: bool):  # type: ignore [no-untyped-def]
    offers_api.unindex_expired_offers(process_all_expired=all_offers)


@blueprint.cli.command("process_expired_collective_offers")
@click.option("-a", "--all", help="Bypass the two days limit to delete all expired collective offers", default=False)
def process_expired_collective_offers(all_offers: bool):  # type: ignore [no-untyped-def]
    educational_api.unindex_expired_collective_offers(process_all_expired=all_offers)


@blueprint.cli.command("process_venues_from_database")
@click.option("--clear", help="Clear search index", type=bool, default=False)
@click.option("--batch-size", help="Batch size (Algolia)", type=int, default=10_000)
@click.option("--max-venues", help="Max number of venues (total)", type=int, default=10_000)
def process_venues_from_database(clear: bool, batch_size: int, max_venues: int):  # type: ignore [no-untyped-def]
    if clear:
        search.unindex_all_venues()
    batch_indexing_venues_in_algolia_from_database(algolia_batch_size=batch_size, max_venues=max_venues)


@blueprint.cli.command("reindex_all_offers")
@click.option("--max-id", help="max offer id", type=int)
@click.option("--algolia-batch-size", help="Algolia batch size", type=int, default=1_000)
@click.option("--max-offers-by-task", help="Maximum number of offers for a cloud task", type=int, default=1_000_000)
def reindex_all_offers(max_id: int, algolia_batch_size: int, max_offers_by_task: int) -> None:
    """
    Reindex all offers by creating asynchronous tasks that will each
    handle `max_offers_by_task` offers (max). And each of them will
    reindex by batches of max `algolia_batch_size` items.

    Please note that if `max_offers_by_task` is too small, this will
    create tons of tasks which might create a mess. And if
    `algolia_batch_size` is too big, the search stack usage might be
    suboptimal.
    """
    for start in range(0, max_id, max_offers_by_task):
        payload = search_tasks.IndexOffersRequest(
            start_id=start, batch_size=algolia_batch_size, total=max_offers_by_task
        )
        search_tasks.reindex_offers_batch.delay(payload)
