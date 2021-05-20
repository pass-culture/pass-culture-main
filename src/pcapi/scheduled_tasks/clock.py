"""
    isort:skip_file
"""
from datetime import date
from datetime import timedelta
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask

# FIXME (xordoquy, 2021-03-01): this is to prevent circular imports when importing pcapi.core.users.api
import pcapi.models  # pylint: disable=unused-import
from pcapi import settings
from pcapi.core.logging import install_logging
from pcapi.core.offers.repository import check_stock_consistency
from pcapi.core.offers.repository import delete_past_draft_offer
from pcapi.core.offers.repository import find_tomorrow_event_stock_ids
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users import api as users_api
from pcapi.core.users.repository import get_newly_eligible_users
from pcapi.domain.user_emails import send_newly_eligible_user_email
from pcapi.local_providers.provider_api import provider_api_stocks
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.feature import FeatureToggle
from pcapi.repository.user_queries import find_most_recent_beneficiary_creation_date_for_source
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron
from pcapi.scripts.beneficiary import remote_import
from pcapi.scripts.booking.handle_expired_bookings import handle_expired_bookings
from pcapi.scripts.booking.notify_soon_to_be_expired_bookings import notify_soon_to_be_expired_bookings
from pcapi.scripts.update_booking_used import update_booking_used_after_stock_occurrence
from pcapi.workers.push_notification_job import send_tomorrow_stock_notification


install_logging()

logger = logging.getLogger(__name__)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.UPDATE_BOOKING_USED)
def update_booking_used(app: Flask) -> None:
    update_booking_used_after_stock_occurrence()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALLOCINE)
def synchronize_allocine_stocks(app: Flask) -> None:
    allocine_stocks_provider_id = get_provider_by_local_class("AllocineStocks").id
    synchronize_venue_providers_for_provider(allocine_stocks_provider_id)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_LIBRAIRES)
def synchronize_libraires_stocks(app: Flask) -> None:
    libraires_stocks_provider = get_provider_by_local_class("LibrairesStocks")
    if libraires_stocks_provider:
        synchronize_venue_providers_for_provider(libraires_stocks_provider.id)


@log_cron
@cron_context
def synchronize_provider_api(app: Flask) -> None:
    fnac_stocks_provider = get_provider_by_local_class("FnacStocks")
    if fnac_stocks_provider:
        synchronize_venue_providers_for_provider(fnac_stocks_provider.id)

    provider_api_stocks.synchronize_stocks()


@log_cron
@cron_context
def synchronize_praxiel_stocks(app: Flask) -> None:
    praxiel_stocks_provider = get_provider_by_local_class("PraxielStocks")
    if praxiel_stocks_provider:
        synchronize_venue_providers_for_provider(praxiel_stocks_provider.id)


@log_cron
@cron_context
def pc_remote_import_beneficiaries(app: Flask) -> None:
    procedure_id = settings.DMS_NEW_ENROLLMENT_PROCEDURE_ID
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id
    )
    remote_import.run(import_from_date)


@log_cron
@cron_context
def pc_handle_expired_bookings(app: Flask) -> None:
    handle_expired_bookings()


@log_cron
@cron_context
def pc_notify_soon_to_be_expired_bookings(app: Flask) -> None:
    notify_soon_to_be_expired_bookings()


@log_cron
@cron_context
def pc_notify_newly_eligible_users(app: Flask) -> None:
    yesterday = date.today() - timedelta(days=1)
    for user in get_newly_eligible_users(yesterday):
        send_newly_eligible_user_email(user)


@log_cron
@cron_context
def pc_clean_expired_tokens(app: Flask) -> None:
    users_api.delete_expired_tokens()


@log_cron
@cron_context
def pc_check_stock_quantity_consistency(app: Flask) -> None:
    inconsistent_stocks = check_stock_consistency()
    if inconsistent_stocks:
        logger.error("Found inconsistent stocks: %s", ", ".join([str(stock_id) for stock_id in inconsistent_stocks]))


@log_cron
@cron_context
def pc_send_tomorrow_events_notifications(app: Flask) -> None:
    stock_ids = find_tomorrow_event_stock_ids()
    for stock_id in stock_ids:
        send_tomorrow_stock_notification.delay(stock_id)


@log_cron
@cron_context
def pc_clean_past_draft_offers(app: Flask) -> None:
    delete_past_draft_offer()


def main() -> None:
    from pcapi.flask_app import app

    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(synchronize_allocine_stocks, "cron", [app], day="*", hour="23")

    scheduler.add_job(synchronize_libraires_stocks, "cron", [app], day="*", hour="22")

    scheduler.add_job(synchronize_provider_api, "cron", [app], day="*", hour="1")

    scheduler.add_job(synchronize_praxiel_stocks, "cron", [app], day="*", hour="0")

    scheduler.add_job(pc_remote_import_beneficiaries, "cron", [app], day="*")

    scheduler.add_job(update_booking_used, "cron", [app], day="*", hour="0")

    scheduler.add_job(
        pc_handle_expired_bookings,
        "cron",
        [app],
        day="*",
        hour="5",
    )

    scheduler.add_job(
        pc_notify_soon_to_be_expired_bookings,
        "cron",
        [app],
        day="*",
        hour="5",
        minute="30",
    )

    scheduler.add_job(pc_notify_newly_eligible_users, "cron", [app], day="*", hour="3")

    scheduler.add_job(pc_clean_expired_tokens, "cron", [app], day="*", hour="2")

    scheduler.add_job(pc_check_stock_quantity_consistency, "cron", [app], day="*", hour="1")

    scheduler.add_job(pc_send_tomorrow_events_notifications, "cron", [app], day="*", hour="16")

    scheduler.add_job(pc_clean_past_draft_offers, "cron", [app], day="*", hour="20")

    scheduler.start()


if __name__ == "__main__":
    main()
