import click

from pcapi.core import search
from pcapi.core.educational.api.offer import unindex_expired_collective_offers
import pcapi.core.offers.api as offers_api
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_collective_offers_in_algolia_from_database
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_collective_offers_template_in_algolia_from_database
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_venues_in_algolia_from_database
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


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


@blueprint.cli.command("process_collective_offers_from_database")
@click.option("--clear", help="Clear search index", type=bool, default=False)
@click.option("-ep", "--ending-page", help="Ending page for indexing collective offers", type=int, default=None)
@click.option("-l", "--limit", help="Number of offers per page", type=int, default=10_000)
@click.option("-sp", "--starting-page", help="Starting page for indexing collective offers", type=int, default=0)
def process_collective_offers_from_database(  # type: ignore [no-untyped-def]
    clear: bool,
    ending_page: int,
    limit: int,
    starting_page: int,
):
    if clear:
        search.unindex_all_collective_offers(only_non_template=True)
    batch_indexing_collective_offers_in_algolia_from_database(
        ending_page=ending_page, limit=limit, starting_page=starting_page
    )


@blueprint.cli.command("process_collective_offers_template_from_database")
@click.option("--clear", help="Clear search index", type=bool, default=False)
@click.option(
    "-ep",
    "--ending-page",
    help="Ending page for indexing collective offers templates",
    type=int,
    default=None,
)
@click.option("-l", "--limit", help="Number of offers per page", type=int, default=10_000)
@click.option(
    "-sp",
    "--starting-page",
    help="Starting page for indexing collective offer templates",
    type=int,
    default=0,
)
def process_collective_offers_template_from_database(  # type: ignore [no-untyped-def]
    clear: bool,
    ending_page: int,
    limit: int,
    starting_page: int,
):
    if clear:
        search.unindex_all_collective_offers(only_template=True)
    batch_indexing_collective_offers_template_in_algolia_from_database(
        ending_page=ending_page,
        limit=limit,
        starting_page=starting_page,
    )


@blueprint.cli.command("process_expired_offers")
@click.option("-a", "--all", help="Bypass the two days limit to delete all expired offers", default=False)
def process_expired_offers(all_offers: bool):  # type: ignore [no-untyped-def]
    offers_api.unindex_expired_offers(process_all_expired=all_offers)


@blueprint.cli.command("process_expired_collective_offers")
@click.option("-a", "--all", help="Bypass the two days limit to delete all expired collective offers", default=False)
def process_expired_collective_offers(all_offers: bool):  # type: ignore [no-untyped-def]
    unindex_expired_collective_offers(process_all_expired=all_offers)


@blueprint.cli.command("process_venues_from_database")
@click.option("--clear", help="Clear search index", type=bool, default=False)
@click.option("--batch-size", help="Batch size (Algolia)", type=int, default=10_000)
@click.option("--max-venues", help="Max number of venues (total)", type=int, default=10_000)
def process_venues_from_database(clear: bool, batch_size: int, max_venues: int):  # type: ignore [no-untyped-def]
    if clear:
        search.unindex_all_venues()
    batch_indexing_venues_in_algolia_from_database(algolia_batch_size=batch_size, max_venues=max_venues)
