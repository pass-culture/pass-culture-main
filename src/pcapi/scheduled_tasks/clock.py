from apscheduler.schedulers.blocking import BlockingScheduler

from pcapi import settings
from pcapi.local_providers.fnac.fnac_stocks_provider import synchronize_fnac_venues_stocks
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.feature import FeatureToggle
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.repository.user_queries import find_most_recent_beneficiary_creation_date_for_source
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron
from pcapi.scripts.beneficiary import remote_import
from pcapi.scripts.booking.handle_expired_bookings import handle_expired_bookings
from pcapi.scripts.booking.notify_soon_to_be_expired_bookings import notify_soon_to_be_expired_bookings
from pcapi.scripts.update_booking_used import update_booking_used_after_stock_occurrence


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.UPDATE_BOOKING_USED)
def update_booking_used(app) -> None:
    update_booking_used_after_stock_occurrence()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALLOCINE)
def synchronize_allocine_stocks(app) -> None:
    allocine_stocks_provider_id = get_provider_by_local_class("AllocineStocks").id
    synchronize_venue_providers_for_provider(allocine_stocks_provider_id)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_LIBRAIRES)
def synchronize_libraires_stocks(app) -> None:
    libraires_stocks_provider_id = get_provider_by_local_class("LibrairesStocks").id
    synchronize_venue_providers_for_provider(libraires_stocks_provider_id)


@log_cron
@cron_context
def synchronize_fnac_stocks(app) -> None:
    synchronize_fnac_venues_stocks()


@log_cron
@cron_context
def synchronize_praxiel_stocks(app) -> None:
    praxiel_stocks_provider_id = get_provider_by_local_class("PraxielStocks").id
    synchronize_venue_providers_for_provider(praxiel_stocks_provider_id)


@log_cron
@cron_context
def pc_remote_import_beneficiaries(app) -> None:
    procedure_id = settings.DMS_NEW_ENROLLMENT_PROCEDURE_ID
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id
    )
    remote_import.run(import_from_date)


@log_cron
@cron_context
def pc_handle_expired_bookings(app) -> None:
    handle_expired_bookings()


@log_cron
@cron_context
def pc_notify_soon_to_be_expired_bookings(app) -> None:
    notify_soon_to_be_expired_bookings()


def main():
    from pcapi.flask_app import app

    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(synchronize_allocine_stocks, "cron", [app], day="*", hour="23")

    scheduler.add_job(synchronize_libraires_stocks, "cron", [app], day="*", hour="22")

    scheduler.add_job(synchronize_fnac_stocks, "cron", [app], day="*", hour="1")

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

    scheduler.start()


if __name__ == "__main__":
    main()
