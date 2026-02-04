import enum
import logging
import typing
from itertools import islice

import click

import pcapi.core.educational.repository as collective_offers_repository
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
import pcapi.utils.cron as cron_decorators
from pcapi import settings
from pcapi.core import search
from pcapi.core.educational.api.offer import unindex_expired_or_archived_collective_offers_template
from pcapi.core.offerers import api as offerers_api
from pcapi.core.search import staging_indexation
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.chunks import get_chunks


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


class IndexableObjects(enum.Enum):
    ARTISTS = enum.auto()
    COLLECTIVE_OFFER_TEMPLATES = enum.auto()
    OFFERS = enum.auto()
    VENUES = enum.auto()


@blueprint.cli.command("index_offers_in_algolia_by_artist")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_offers_in_algolia_by_artist() -> None:
    """Pop artists from indexation queue and reindex their offers."""
    search.index_offers_of_artists_in_queue()


@blueprint.cli.command("index_offers_in_algolia_by_venue")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_offers_in_algolia_by_venue() -> None:
    """Pop venues from indexation queue and reindex their offers."""
    search.index_offers_of_venues_in_queue()


@blueprint.cli.command("delete_expired_offers_in_algolia")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def delete_expired_offers_in_algolia() -> None:
    """Unindex offers that have expired.

    By default, process offers that have expired within the last 2
    days. For example, if run on Thursday (whatever the time), this
    function handles offers that have expired between Tuesday 00:00
    and Wednesday 23:59 (included)."""
    offers_api.unindex_expired_offers()


@blueprint.cli.command("delete_expired_collective_offers_template_in_algolia")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def delete_expired_collective_offers_template_in_algolia() -> None:
    """Unindex collective offers template that have expired or are archived."""
    unindex_expired_or_archived_collective_offers_template()


@blueprint.cli.command("reindex")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@click.argument("object_type", type=click.Choice(IndexableObjects, case_sensitive=False), required=True)
@click.option("--from_error_queue", is_flag=True, help="Reindex objects from error queue")
def reindex(object_type: IndexableObjects, from_error_queue: bool = False) -> None:
    """Pop object ids from queue and reindex"""
    match object_type:
        case IndexableObjects.ARTISTS:
            search.index_artists_in_queue(from_error_queue=from_error_queue)
        case IndexableObjects.COLLECTIVE_OFFER_TEMPLATES:
            search.index_collective_offers_templates_in_queue(from_error_queue=from_error_queue)
        case IndexableObjects.VENUES:
            search.index_venues_in_queue(from_error_queue=from_error_queue)
        case IndexableObjects.OFFERS:
            search.index_offers_in_queue(from_error_queue=from_error_queue, max_batches_to_process=50)
        case _:
            raise ValueError("Invalid `object_type`")  # should not happen


# TODO (tcoudray-pass, 04/02/26): Remove once the CRON job uses reindex command
@blueprint.cli.command("index_offers_in_algolia_by_offer")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_offers_in_algolia_by_offer() -> None:
    """Pop offers from indexation queue and reindex them."""
    search.index_offers_in_queue(max_batches_to_process=50)


# TODO (tcoudray-pass, 04/02/26): Remove once the CRON job uses reindex command
@blueprint.cli.command("index_collective_offer_templates")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_collective_offer_templates() -> None:
    """Pop collective offers template from indexation queue and reindex them."""
    search.index_collective_offers_templates_in_queue()


# TODO (tcoudray-pass, 04/02/26): Remove once the CRON job uses reindex command
@blueprint.cli.command("index_artists")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_artists() -> None:
    """Pop artists from indexation queue and reindex them."""
    search.index_artists_in_queue()


# TODO (tcoudray-pass, 04/02/26): Remove once the CRON job uses reindex command
@blueprint.cli.command("index_venues")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_venues() -> None:
    """Pop venues from indexation queue and reindex them."""
    search.index_venues_in_queue()


# TODO (tcoudray-pass, 04/02/26): Remove once the CRON job uses reindex command with --from_error_queue flag
@blueprint.cli.command("index_artists_in_error")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_artists_in_error() -> None:
    """Pop artists from the error queue and reindex them."""
    search.index_artists_in_queue(from_error_queue=True)


# TODO (tcoudray-pass, 04/02/26): Remove once the CRON job uses reindex command with --from_error_queue flag
@blueprint.cli.command("index_venues_in_error")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_venues_in_error() -> None:
    """Pop venues from the error queue and reindex them."""
    search.index_venues_in_queue(from_error_queue=True)


# TODO (tcoudray-pass, 04/02/26): Remove once the CRON job uses reindex command with --from_error_queue flag
@blueprint.cli.command("index_collective_offers_templates_in_error")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_collective_offers_templates_in_error() -> None:
    """Pop collective offers template from the error queue and reindex them."""
    search.index_collective_offers_templates_in_queue(from_error_queue=True)


# TODO (tcoudray-pass, 04/02/26): Remove once the CRON job uses reindex command with --from_error_queue flag
@blueprint.cli.command("index_offers_in_error_in_algolia_by_offer")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def index_offers_in_error_in_algolia_by_offer() -> None:
    """Pop offers from the error queue and reindex them."""
    search.index_offers_in_queue(from_error_queue=True)


def _partially_index(
    *,
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
@click.option("--clear", help="Clear search index first", is_flag=True)
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
@click.option("--clear", help="Clear search index first", is_flag=True)
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
@click.option("--clear", help="Clear search index first", is_flag=True)
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
@cron_decorators.log_cron_with_transaction
def update_products_booking_count_and_reindex_offers() -> None:
    """
    update last 30 days booking count for all products,
    if the value changes for the product reindex all associated offers.

    This command is needed to have to have last30daysBookings count by EAN in Algolia.
    """
    search.update_products_last_30_days_booking_count()


@blueprint.cli.command("index_offers_staging")
@click.option("--clear", help="Clear search index first", is_flag=True)
def index_offers_staging(clear: bool) -> None:
    """Index a subset of offers for staging.
    we do not index by batch because we only have 5000 offers to index
    """
    if not settings.ENABLE_INDEXATION_CHERRY_PICK_FOR_STAGING:
        raise RuntimeError("This script should only be run on staging")
    if clear:
        search.unindex_all_offers()

    offer_ids_to_reindex = iter(staging_indexation.get_relevant_offers_to_index())
    while batch := tuple(islice(offer_ids_to_reindex, 1000)):
        search.reindex_offer_ids(batch)


@blueprint.cli.command("clean_indexation_processing_queues")
@cron_decorators.log_cron_with_transaction
def clean_indexation_processing_queues() -> None:
    search.clean_processing_queues()
