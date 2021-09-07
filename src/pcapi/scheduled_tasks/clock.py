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
import pcapi.core.bookings.api as bookings_api
from pcapi.core.logging import install_logging
from pcapi.core.offers.repository import check_stock_consistency
from pcapi.core.offers.repository import delete_past_draft_offers
from pcapi.core.offers.repository import find_tomorrow_event_stock_ids
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users import api as users_api
from pcapi.core.users.repository import get_newly_eligible_users
from pcapi.domain.user_emails import send_newly_eligible_user_email, send_withdrawal_terms_to_newly_validated_offerer
from pcapi.local_providers.provider_api import provider_api_stocks
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.feature import FeatureToggle
from pcapi.models.db import db
from pcapi.repository.offerer_queries import get_offerers_by_date_validated
from pcapi.repository.user_queries import find_most_recent_beneficiary_creation_date_for_source
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron
from pcapi.scripts.beneficiary import remote_import, remote_tag_has_completed
from pcapi.scripts.booking.handle_expired_bookings import handle_expired_bookings
from pcapi.scripts.booking.notify_soon_to_be_expired_bookings import notify_soon_to_be_expired_individual_bookings
from pcapi.workers.push_notification_job import send_tomorrow_stock_notification


install_logging()

logger = logging.getLogger(__name__)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.UPDATE_BOOKING_USED)
def update_booking_used(app: Flask) -> None:
    bookings_api.auto_mark_as_used_after_event()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALLOCINE)
def synchronize_allocine_stocks(app: Flask) -> None:
    allocine_stocks_provider_id = get_provider_by_local_class("AllocineStocks").id
    synchronize_venue_providers_for_provider(allocine_stocks_provider_id)


@log_cron
@cron_context
def synchronize_provider_api(app: Flask) -> None:
    provider_api_stocks.synchronize_stocks()


# FIXME (asaunier, 2021-05-25): This clock must be removed once every application from procedure
#  defined in DMS_NEW_ENROLLMENT_PROCEDURE_ID has been treated
@log_cron
@cron_context
def pc_remote_import_beneficiaries(app: Flask) -> None:
    procedure_id = settings.DMS_NEW_ENROLLMENT_PROCEDURE_ID
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id
    )
    remote_import.run(procedure_id)
    remote_tag_has_completed.run(import_from_date, procedure_id)


# FIXME (xordoquy, 2021-06-16): This clock must be removed once every application from procedure
#  defined in 44623 has been treated
@log_cron
@cron_context
def pc_remote_import_beneficiaries_from_old_dms(app: Flask) -> None:
    if not settings.IS_PROD:
        return
    procedure_id = 44623
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id
    )
    remote_import.run(procedure_id)
    remote_tag_has_completed.run(import_from_date, procedure_id)


@log_cron
@cron_context
def pc_import_beneficiaries_from_dms(app: Flask) -> None:
    procedure_id = settings.DMS_ENROLLMENT_PROCEDURE_ID_AFTER_GENERAL_OPENING
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id
    )
    remote_import.run(procedure_id, use_graphql_api=FeatureToggle.ENABLE_DMS_GRAPHQL_API.is_active())
    remote_tag_has_completed.run(import_from_date, procedure_id)


@log_cron
@cron_context
def pc_handle_expired_bookings(app: Flask) -> None:
    handle_expired_bookings()


@log_cron
@cron_context
def pc_notify_soon_to_be_expired_individual_bookings(app: Flask) -> None:
    notify_soon_to_be_expired_individual_bookings()


@log_cron
@cron_context
def pc_notify_newly_eligible_users(app: Flask) -> None:
    if not settings.IS_PROD and not settings.IS_TESTING:
        return
    yesterday = date.today() - timedelta(days=1)
    for user in get_newly_eligible_users(yesterday):
        send_newly_eligible_user_email(user)


@log_cron
@cron_context
def pc_clean_expired_tokens(app: Flask) -> None:
    users_api.delete_expired_tokens()
    db.session.commit()


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
    delete_past_draft_offers()


@log_cron
@cron_context
def pc_send_withdrawal_terms_to_offerers_validated_yesterday(app: Flask) -> None:
    yesterday = date.today() - timedelta(days=1)
    offerers_validated_yesterday = get_offerers_by_date_validated(yesterday)
    for offerer in offerers_validated_yesterday:
        send_withdrawal_terms_to_newly_validated_offerer(offerer)


def main() -> None:
    from pcapi.flask_app import app

    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(synchronize_allocine_stocks, "cron", [app], day="*", hour="23")

    scheduler.add_job(synchronize_provider_api, "cron", [app], day="*", hour="1")

    scheduler.add_job(pc_remote_import_beneficiaries, "cron", [app], hour="*")

    scheduler.add_job(pc_remote_import_beneficiaries_from_old_dms, "cron", [app], day="*", hour="20")

    scheduler.add_job(pc_import_beneficiaries_from_dms, "cron", [app], hour="*")

    scheduler.add_job(update_booking_used, "cron", [app], day="*", hour="0")

    scheduler.add_job(
        pc_handle_expired_bookings,
        "cron",
        [app],
        day="*",
        hour="5",
    )

    scheduler.add_job(
        pc_notify_soon_to_be_expired_individual_bookings,
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

    scheduler.add_job(pc_send_withdrawal_terms_to_offerers_validated_yesterday, "cron", [app], day="*", hour="6")

    scheduler.start()


if __name__ == "__main__":
    main()
