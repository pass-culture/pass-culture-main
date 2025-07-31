import logging

import click

import pcapi.core.offers.api as offers_api
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)

blueprint = Blueprint(__name__, __name__)


# Deprecated. Remove when we have a new cron job calling `reindex_recently_published_offers`
@blueprint.cli.command("activate_future_offers")
@log_cron_with_transaction
def activate_future_offers() -> None:
    offers_api.reindex_recently_published_offers()


@blueprint.cli.command("reindex_recently_published_offers")
@log_cron_with_transaction
def reindex_recently_published_offers() -> None:
    offers_api.reindex_recently_published_offers()


@blueprint.cli.command("send_future_offer_reminders")
@log_cron_with_transaction
def send_future_offer_reminders() -> None:
    offers_api.send_future_offer_reminders()


@blueprint.cli.command("set_upper_timespan_of_inactive_headline_offers")
@log_cron_with_transaction
def set_upper_timespan_of_inactive_headline_offers() -> None:
    offers_api.set_upper_timespan_of_inactive_headline_offers()


@blueprint.cli.command("delete_unbookable_unbooked_old_offers")
@click.argument("min_offer_id", required=False, type=int, default=0)
@click.argument("max_offer_id", required=False, type=int, default=None)
@click.argument("query_batch_size", required=False, type=int, default=5_000)
@click.argument("filter_batch_size", required=False, type=int, default=2_500)
@click.argument("delete_batch_size", required=False, type=int, default=32)
@log_cron_with_transaction
def delete_unbookable_unbooked_old_offers(
    min_offer_id: int, max_offer_id: int | None, query_batch_size: int, filter_batch_size: int, delete_batch_size: int
) -> None:
    if FeatureToggle.ENABLE_OFFERS_AUTO_CLEANUP.is_active():
        offers_api.delete_unbookable_unbooked_old_offers(
            min_id=min_offer_id,
            max_id=max_offer_id,
            query_batch_size=query_batch_size,
            filter_batch_size=filter_batch_size,
            delete_batch_size=delete_batch_size,
        )
    else:
        logger.info(
            "Feature '%s' is not active. Skipping offer cleanup.", FeatureToggle.ENABLE_OFFERS_AUTO_CLEANUP.name
        )


@blueprint.cli.command("check_product_counts_consistency")
@click.argument("batch_size", required=False, type=int, default=10_000)
def check_product_counts_consistency(batch_size: int) -> None:
    product_ids = offers_api.fetch_inconsistent_products(batch_size)

    if product_ids:
        logger.error("Inconsistent product counts found", extra={"product_ids": product_ids})
