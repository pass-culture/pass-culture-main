import logging

import click
import sqlalchemy.orm as sa_orm

import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
import pcapi.utils.cron as cron_decorators
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)

blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("reindex_recently_published_offers")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def reindex_recently_published_offers() -> None:
    offers_api.reindex_recently_published_offers()


@blueprint.cli.command("send_future_offer_reminders")
@cron_decorators.log_cron_with_transaction
def send_future_offer_reminders() -> None:
    offers_api.send_future_offer_reminders()


@blueprint.cli.command("set_upper_timespan_of_inactive_headline_offers")
@cron_decorators.log_cron_with_transaction
def set_upper_timespan_of_inactive_headline_offers() -> None:
    offers_api.set_upper_timespan_of_inactive_headline_offers()


@blueprint.cli.command("delete_unbookable_unbooked_old_offers")
@click.argument("min_offer_id", required=False, type=int, default=None)
@click.argument("max_offer_id", required=False, type=int, default=None)
@click.argument("query_batch_size", required=False, type=int, default=5_000)
@click.argument("filter_batch_size", required=False, type=int, default=2_500)
@click.argument("delete_batch_size", required=False, type=int, default=32)
@cron_decorators.log_cron_with_transaction
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


@blueprint.cli.command("update_product_counts")
@click.argument("batch_size", required=False, type=int, default=10_000)
def update_product_counts(batch_size: int) -> None:
    offers_api.update_product_counts(batch_size)


@blueprint.cli.command("check_stock_quantity_consistency")
@cron_decorators.log_cron_with_transaction
def check_stock_quantity_consistency() -> None:
    inconsistent_stocks = offers_repository.check_stock_consistency()
    if inconsistent_stocks:
        logger.error("Found inconsistent stocks: %s", ", ".join([str(stock_id) for stock_id in inconsistent_stocks]))


@blueprint.cli.command("send_email_reminder_7_days_before_event")
@cron_decorators.log_cron_with_transaction
def send_email_reminder_7_days_before_event() -> None:
    """Triggers email to be sent for events happening in 7 days"""
    stocks = offers_repository.find_event_stocks_happening_in_x_days(7).options(
        sa_orm.joinedload(Stock.offer).joinedload(Offer.venue)
    )
    for stock in stocks:
        transactional_mails.send_reminder_7_days_before_event_to_pro(stock)


@blueprint.cli.command("send_email_reminder_offer_creation_j5")
@cron_decorators.log_cron_with_transaction
def send_email_reminder_offer_creation_j5_to_pro() -> None:
    """Triggers email reminder to pro 5 days after venue creation if no offer is created"""
    venues = offerers_repository.find_venues_of_offerers_with_no_offer_and_at_least_one_physical_venue_and_validated_x_days_ago(
        5
    )
    for venue_id, venue_booking_email in venues:
        try:
            transactional_mails.send_reminder_offer_creation_j5_to_pro(venue_booking_email)
        except Exception:
            logger.exception(
                "Could not send email reminder offer creation j+5 to pro",
                extra={
                    "venue.id": venue_id,
                },
            )


@blueprint.cli.command("send_email_reminder_offer_creation_j10")
@cron_decorators.log_cron_with_transaction
def send_email_reminder_offer_creation_j10_to_pro() -> None:
    """Triggers email reminder to pro 10 days after venue creation if no offer is created"""
    venues = offerers_repository.find_venues_of_offerers_with_no_offer_and_at_least_one_physical_venue_and_validated_x_days_ago(
        10
    )
    for venue_id, venue_booking_email in venues:
        try:
            transactional_mails.send_reminder_offer_creation_j10_to_pro(venue_booking_email)
        except Exception:
            logger.exception(
                "Could not send email reminder offer creation j+10 to pro",
                extra={
                    "venue.id": venue_id,
                },
            )
