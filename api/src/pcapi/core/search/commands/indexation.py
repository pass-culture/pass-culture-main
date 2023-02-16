import logging
import typing

import click

from pcapi.core import search
from pcapi.core.educational.api.offer import unindex_expired_collective_offers
import pcapi.core.educational.repository as collective_offers_repository
from pcapi.core.offerers import api as offerers_api
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.chunks import get_chunks


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("index_offers_in_algolia_by_offer")
@log_cron_with_transaction
def index_offers_in_algolia_by_offer():  # type: ignore [no-untyped-def]
    """Pop offers from indexation queue and reindex them."""
    search.index_offers_in_queue()


@blueprint.cli.command("index_offers_in_algolia_by_venue")
@log_cron_with_transaction
def index_offers_in_algolia_by_venue():  # type: ignore [no-untyped-def]
    """Pop venues from indexation queue and reindex their offers."""
    search.index_offers_of_venues_in_queue()


@blueprint.cli.command("index_collective_offers")
@log_cron_with_transaction
def index_collective_offers():  # type: ignore [no-untyped-def]
    """Pop collective offers from indexation queue and reindex them."""
    search.index_collective_offers_in_queue()


@blueprint.cli.command("index_collective_offer_templates")
@log_cron_with_transaction
def index_collective_offer_templates():  # type: ignore [no-untyped-def]
    """Pop collective offers template from indexation queue and reindex them."""
    search.index_collective_offers_templates_in_queue()


@blueprint.cli.command("delete_expired_offers_in_algolia")
@log_cron_with_transaction
def delete_expired_offers_in_algolia():  # type: ignore [no-untyped-def]
    """Unindex offers that have expired.

    By default, process offers that have expired within the last 2
    days. For example, if run on Thursday (whatever the time), this
    function handles offers that have expired between Tuesday 00:00
    and Wednesday 23:59 (included)."""
    offers_api.unindex_expired_offers()


@blueprint.cli.command("delete_expired_collective_offers_in_algolia")
@log_cron_with_transaction
def delete_expired_collective_offers_in_algolia():  # type: ignore [no-untyped-def]
    """Unindex collective offers that have expired.

    By default, process collective offers that have expired within the last 2
    days. For example, if run on Thursday (whatever the time), this
    function handles collective offers that have expired between Tuesday 00:00
    and Wednesday 23:59 (included)."""
    unindex_expired_collective_offers()


@blueprint.cli.command("index_offers_in_error_in_algolia_by_offer")
@log_cron_with_transaction
def index_offers_in_error_in_algolia_by_offer():  # type: ignore [no-untyped-def]
    """Pop offers from the error queue and reindex them."""
    search.index_offers_in_queue(from_error_queue=True)


@blueprint.cli.command("index_collective_offers_in_error")
@log_cron_with_transaction
def index_collective_offers_in_error():  # type: ignore [no-untyped-def]
    """Pop collective offers from the error queue and reindex them."""
    search.index_collective_offers_in_queue(from_error_queue=True)


@blueprint.cli.command("index_collective_offers_templates_in_error")
@log_cron_with_transaction
def index_collective_offers_templates_in_error():  # type: ignore [no-untyped-def]
    """Pop collective offers template from the error queue and reindex them."""
    search.index_collective_offers_templates_in_queue(from_error_queue=True)


@blueprint.cli.command("index_venues")
@log_cron_with_transaction
def index_venues():  # type: ignore [no-untyped-def]
    """Pop venues from indexation queue and reindex them."""
    search.index_venues_in_queue()


@blueprint.cli.command("index_venues_in_error")
@log_cron_with_transaction
def index_venues_in_error():  # type: ignore [no-untyped-def]
    """Pop venues from the error queue and reindex them."""
    search.index_venues_in_queue(from_error_queue=True)


# FIXME (dbaty, 2022-02-16): `limit` may be understood as the number
# of items to index, but it's not. It should be called `batch_size`.
# Also, `ending_page` is not too clear: it's not the last page, the
# function does not process that page. The function would perhaps be
# clearer if `starting_page` started at 1 and the ending condition was
# changed to actually include the "last" page (which would be named
# that way), or the function could take a number of pages to process.
def _partially_index(
    what: str,
    getter: typing.Callable,
    indexation_callback: typing.Callable,
    starting_page: int = 0,
    ending_page: int | None = None,
    limit: int = 10000,
) -> None:
    backend = search._get_backend()
    page = starting_page
    while True:
        if ending_page and ending_page == page:
            break
        ids = getter(limit=limit, page=page)
        if not ids:
            break
        indexation_callback_arguments = [ids]
        if "backend" in indexation_callback.__annotations__:
            indexation_callback_arguments.insert(0, backend)
        indexation_callback(*indexation_callback_arguments)
        logger.info("Indexed %d %s from page %d", len(ids), what, page)
        page += 1


@blueprint.cli.command("process_offers_from_database")
@click.option("--clear", help="Clear search index first", type=bool, default=False)
@click.option("-ep", "--ending-page", help="Ending page", type=int, default=None)
@click.option("-l", "--limit", help="Number of offers per page", type=int, default=10_000)
@click.option("-sp", "--starting-page", help="Starting page (first is 0)", type=int, default=0)
def process_offers_from_database(
    clear: bool,
    ending_page: int | None,
    limit: int,
    starting_page: int,
) -> None:
    if clear:
        search.unindex_all_offers()
    _partially_index(
        what="offers",
        getter=offers_repository.get_paginated_active_offer_ids,
        indexation_callback=search.reindex_offer_ids,
        starting_page=starting_page,
        ending_page=ending_page,
        limit=limit,
    )


@blueprint.cli.command("process_collective_offers_from_database")
@click.option("--clear", help="Clear search index first", type=bool, default=False)
@click.option("-ep", "--ending-page", help="Ending page", type=int, default=None)
@click.option("-l", "--limit", help="Number of offers per page", type=int, default=10_000)
@click.option("-sp", "--starting-page", help="Starting page (first is 0)", type=int, default=0)
def process_collective_offers_from_database(
    clear: bool,
    ending_page: int,
    limit: int,
    starting_page: int,
) -> None:
    if clear:
        search.unindex_all_collective_offers(only_non_template=True)
    _partially_index(
        what="collective offers",
        getter=collective_offers_repository.get_paginated_active_collective_offer_ids,
        indexation_callback=search._reindex_collective_offer_ids,
        starting_page=starting_page,
        ending_page=ending_page,
        limit=limit,
    )


@blueprint.cli.command("process_collective_offers_template_from_database")
@click.option("--clear", help="Clear search index first", type=bool, default=False)
@click.option("-ep", "--ending-page", help="Ending page", type=int, default=None)
@click.option("-l", "--limit", help="Number of templates per page", type=int, default=10_000)
@click.option("-sp", "--starting-page", help="Starting page (first is 0)", type=int, default=0)
def process_collective_offers_template_from_database(
    clear: bool,
    ending_page: int,
    limit: int,
    starting_page: int,
) -> None:
    if clear:
        search.unindex_all_collective_offers(only_template=True)
    _partially_index(
        what="collective offer templates",
        getter=collective_offers_repository.get_paginated_active_collective_offer_template_ids,
        indexation_callback=search._reindex_collective_offer_template_ids,
        starting_page=starting_page,
        ending_page=ending_page,
        limit=limit,
    )


@blueprint.cli.command("process_venues_from_database")
@click.option("--clear", help="Clear search index first", type=bool, default=False)
@click.option("--batch-size", help="Batch size (Algolia)", type=int, default=10_000)
@click.option("--max-venues", help="Max number of venues (total)", type=int, default=10_000)
def process_venues_from_database(clear: bool, batch_size: int, max_venues: int) -> None:
    if clear:
        search.unindex_all_venues()
    _reindex_all_eligible_venues(batch_size, max_venues)


def _reindex_all_eligible_venues(algolia_batch_size: int, max_venues: int) -> None:
    venues = offerers_api.get_eligible_for_search_venues(max_venues)
    for page, venue_chunk in enumerate(get_chunks(venues, algolia_batch_size), start=1):
        venue_ids = [venue.id for venue in venue_chunk]
        search.reindex_venue_ids(venue_ids)
        logger.info("Reindex %d eligible venues from page %d", len(venue_ids), page)
