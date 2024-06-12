import logging
import typing

import click

from pcapi import settings
from pcapi.core import search
from pcapi.core.educational.api.offer import unindex_expired_collective_offers_template
import pcapi.core.educational.repository as collective_offers_repository
from pcapi.core.offerers import api as offerers_api
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
from pcapi.core.search import staging_indexation
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.chunks import get_chunks


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("index_offers_in_algolia_by_offer")
@log_cron_with_transaction
def index_offers_in_algolia_by_offer() -> None:
    """Pop offers from indexation queue and reindex them."""
    search.index_offers_in_queue()


@blueprint.cli.command("index_offers_in_algolia_by_venue")
@log_cron_with_transaction
def index_offers_in_algolia_by_venue() -> None:
    """Pop venues from indexation queue and reindex their offers."""
    search.index_offers_of_venues_in_queue()


@blueprint.cli.command("index_collective_offer_templates")
@log_cron_with_transaction
def index_collective_offer_templates() -> None:
    """Pop collective offers template from indexation queue and reindex them."""
    search.index_collective_offers_templates_in_queue()


@blueprint.cli.command("delete_expired_offers_in_algolia")
@log_cron_with_transaction
def delete_expired_offers_in_algolia() -> None:
    """Unindex offers that have expired.

    By default, process offers that have expired within the last 2
    days. For example, if run on Thursday (whatever the time), this
    function handles offers that have expired between Tuesday 00:00
    and Wednesday 23:59 (included)."""
    offers_api.unindex_expired_offers()


@blueprint.cli.command("delete_expired_collective_offers_template_in_algolia")
@log_cron_with_transaction
def delete_expired_collective_offers_template_in_algolia() -> None:
    """Unindex collective offers template that have expired."""
    unindex_expired_collective_offers_template()


@blueprint.cli.command("index_offers_in_error_in_algolia_by_offer")
@log_cron_with_transaction
def index_offers_in_error_in_algolia_by_offer() -> None:
    """Pop offers from the error queue and reindex them."""
    search.index_offers_in_queue(from_error_queue=True)


@blueprint.cli.command("index_collective_offers_templates_in_error")
@log_cron_with_transaction
def index_collective_offers_templates_in_error() -> None:
    """Pop collective offers template from the error queue and reindex them."""
    search.index_collective_offers_templates_in_queue(from_error_queue=True)


@blueprint.cli.command("index_venues")
@log_cron_with_transaction
def index_venues() -> None:
    """Pop venues from indexation queue and reindex them."""
    search.index_venues_in_queue()


@blueprint.cli.command("index_venues_in_error")
@log_cron_with_transaction
def index_venues_in_error() -> None:
    """Pop venues from the error queue and reindex them."""
    search.index_venues_in_queue(from_error_queue=True)


def _partially_index(
    what: str,
    getter: typing.Callable,
    indexation_callback: typing.Callable,
    batch_size: int = 10000,
    starting_page: int = 1,
    last_page: int | None = None,
) -> None:
    page = starting_page
    while True:
        if last_page and page > last_page:
            break
        ids = getter(batch_size=batch_size, page=page)
        if not ids:
            break
        indexation_callback_arguments = [ids]
        if "backend" in indexation_callback.__annotations__:
            indexation_callback_arguments.insert(0, search._get_backend())
        indexation_callback(*indexation_callback_arguments)
        logger.info("Indexed %d %s from page %d", len(ids), what, page)
        page += 1


@blueprint.cli.command("partially_index_offers")
@click.option("--clear", help="Clear search index first", type=bool, default=False)
@click.option("--batch-size", help="Number of offers per page", type=int, default=10_000)
@click.option("--starting-page", help="Starting page (first is 1)", type=int, default=1)
@click.option("--last-page", help="Last page of offers to index", type=int, default=None)
def partially_index_offers(
    clear: bool,
    batch_size: int,
    starting_page: int,
    last_page: int | None,
) -> None:
    if clear:
        search.unindex_all_offers()
    _partially_index(
        what="offers",
        getter=offers_repository.get_paginated_active_offer_ids,
        indexation_callback=search.reindex_offer_ids,
        batch_size=batch_size,
        starting_page=starting_page,
        last_page=last_page,
    )


@blueprint.cli.command("partially_index_collective_offer_templates")
@click.option("--clear", help="Clear search index first", type=bool, default=False)
@click.option("--batch-size", help="Number of templates per page", type=int, default=10_000)
@click.option("--starting-page", help="Starting page (first is 1)", type=int, default=1)
@click.option("--last-page", help="Last page of templates to index", type=int, default=None)
def partially_index_collective_offer_templates(
    clear: bool,
    batch_size: int,
    starting_page: int,
    last_page: int,
) -> None:
    """Index a subset of collective offer templates.

    This function fetches active templates by batch and then only
    reindex templates that are eligible for search. You control the
    first and last pages of the batches (starting from page 1).
    """
    if clear:
        search.unindex_all_collective_offer_templates()
    _partially_index(
        what="collective offer templates",
        getter=collective_offers_repository.get_paginated_active_collective_offer_template_ids,
        indexation_callback=search._reindex_collective_offer_template_ids,
        batch_size=batch_size,
        starting_page=starting_page,
        last_page=last_page,
    )


@blueprint.cli.command("partially_index_venues")
@click.option("--clear", help="Clear search index first", type=bool, default=False)
@click.option("--batch-size", help="Batch size (Algolia)", type=int, default=10_000)
@click.option("--max-venues", help="Max number of venues (total)", type=int, default=10_000)
def partially_index_venues(clear: bool, batch_size: int, max_venues: int) -> None:
    if clear:
        search.unindex_all_venues()
    _reindex_all_venues(batch_size, max_venues)


def _reindex_all_venues(algolia_batch_size: int, max_venues: int) -> None:
    venues = offerers_api.get_venues_by_batch(max_venues)
    for page, venue_chunk in enumerate(get_chunks(venues, algolia_batch_size), start=1):
        venue_ids = [venue.id for venue in venue_chunk]
        search.reindex_venue_ids(venue_ids)
        logger.info("Reindex %d eligible venues from page %d", len(venue_ids), page)


@blueprint.cli.command("update_products_booking_count_and_reindex_offers")
@log_cron_with_transaction
def update_products_booking_count_and_reindex_offers() -> None:
    """
    update last 30 days booking count for all products,
    if the value changes for the product reindex all associated offers.

    This command is needed to have to have last30daysBookings count by EAN in Algolia.
    """
    search.update_products_last_30_days_booking_count()


@blueprint.cli.command("index_offers_staging")
@click.option("--clear", help="Clear search index first", type=bool, default=False)
def index_offers_staging(clear: bool) -> None:
    """Index a subset of offers for staging.
    we do not index by batch because we only have 5000 offers to index
    """
    if not settings.ENABLE_INDEXATION_CHERRY_PICK_FOR_STAGING:
        raise RuntimeError("This script should only be run on staging")
    if clear:
        search.unindex_all_offers()
    offer_ids_to_reindex = staging_indexation.get_relevant_offers_to_index()
    search.reindex_offer_ids(offer_ids_to_reindex)


@blueprint.cli.command("clean_indexation_processing_queues")
@log_cron_with_transaction
def clean_indexation_processing_queues() -> None:
    search.clean_processing_queues()


@blueprint.cli.command("remove_duplicates_from_venue_indexation_queue")
@log_cron_with_transaction
def remove_duplicates_from_venue_indexation_queue() -> None:
    # TODO (lixxday) : remove after cron is removed
    pass
