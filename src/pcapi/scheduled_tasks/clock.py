# Loading variables should always be the first thing, before any other load
from pcapi.load_environment_variables import load_environment_variables
load_environment_variables()

import os

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from mailjet_rest import Client
from sqlalchemy import orm

from pcapi.local_providers.provider_manager import \
    synchronize_venue_providers_for_provider
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import discovery_view_queries, discovery_view_v3_queries, feature_queries
from pcapi.repository.feature_queries import feature_write_dashboard_enabled, feature_clean_seen_offers_enabled
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.repository.seen_offer_queries import remove_old_seen_offers
from pcapi.repository.user_queries import find_most_recent_beneficiary_creation_date_for_source
from pcapi.scheduled_tasks.decorators import cron_context, cron_require_feature, \
    log_cron
from pcapi.scheduled_tasks import utils
from pcapi.scripts.beneficiary import old_remote_import, remote_import
from pcapi.scripts.dashboard.write_dashboard import write_dashboard
from pcapi.scripts.update_booking_used import \
    update_booking_used_after_stock_occurrence
from pcapi.utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET

DEMARCHES_SIMPLIFIEES_OLD_ENROLLMENT_PROCEDURE_ID = os.environ.get('DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID',
                                                                   None)
DEMARCHES_SIMPLIFIEES_NEW_ENROLLMENT_PROCEDURE_ID = os.environ.get('DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2',
                                                                   None)


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
    fnac_stocks_provider_id = get_provider_by_local_class("FnacStocks").id
    synchronize_venue_providers_for_provider(fnac_stocks_provider_id)

@log_cron
@cron_context
def synchronize_praxiel_stocks(app) -> None:
    praxiel_stocks_provider_id = get_provider_by_local_class("PraxielStocks").id
    synchronize_venue_providers_for_provider(praxiel_stocks_provider_id)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.BENEFICIARIES_IMPORT)
def pc_old_remote_import_beneficiaries(app) -> None:
    procedure_id = int(DEMARCHES_SIMPLIFIEES_OLD_ENROLLMENT_PROCEDURE_ID)
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id)
    old_remote_import.run(import_from_date)


@log_cron
@cron_context
def pc_remote_import_beneficiaries(app) -> None:
    procedure_id = int(DEMARCHES_SIMPLIFIEES_NEW_ENROLLMENT_PROCEDURE_ID)
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(
        BeneficiaryImportSources.demarches_simplifiees, procedure_id)
    remote_import.run(import_from_date)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SAVE_SEEN_OFFERS)
def pc_remove_old_seen_offers(app) -> None:
    remove_old_seen_offers()


@log_cron
@cron_context
def pc_write_dashboard(app) -> None:
    write_dashboard()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.UPDATE_DISCOVERY_VIEW)
def pc_update_recommendations_view(app) -> None:
    if not feature_queries.is_active(FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION):
        discovery_view_queries.refresh()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.UPDATE_DISCOVERY_VIEW)
def pc_update_recommendations_view_with_geolocation(app) -> None:
    if feature_queries.is_active(FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION):
        discovery_view_v3_queries.refresh()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.CLEAN_DISCOVERY_VIEW)
def pc_clean_discovery_views(app) -> None:
    if feature_queries.is_active(FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION):
        discovery_view_v3_queries.clean(app)
    else:
        discovery_view_queries.clean(app)


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')

    discovery_view_refresh_frequency = os.environ.get('RECO_VIEW_REFRESH_FREQUENCY', '*')
    old_seen_offers_delete_frequency = os.environ.get('SEEN_OFFERS_DELETE_FREQUENCY', '*')
    clean_discovery_frequency = os.environ.get('CLEAN_DISCOVERY_FREQUENCY', '*')

    orm.configure_mappers()
    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(synchronize_allocine_stocks, 'cron',
                      [app],
                      day='*', hour='23')

    scheduler.add_job(synchronize_libraires_stocks, 'cron',
                      [app],
                      day='*', hour='22')

    scheduler.add_job(synchronize_fnac_stocks, 'cron',
                      [app],
                      day='*', hour='1')

    scheduler.add_job(synchronize_praxiel_stocks, 'cron',
                      [app],
                      day='*', hour='0')

    scheduler.add_job(pc_old_remote_import_beneficiaries, 'cron',
                      [app],
                      day='*')

    scheduler.add_job(pc_remote_import_beneficiaries, 'cron',
                      [app],
                      day='*')

    if feature_write_dashboard_enabled():
        scheduler.add_job(pc_write_dashboard, 'cron',
                          [app],
                          day='*', hour='4')

    if feature_clean_seen_offers_enabled():
        scheduler.add_job(pc_remove_old_seen_offers, 'cron',
                          [app],
                          day=old_seen_offers_delete_frequency)

    scheduler.add_job(update_booking_used, 'cron',
                      [app],
                      day='*', hour='0')

    scheduler.add_job(pc_update_recommendations_view, 'cron',
                      [app],
                      minute=discovery_view_refresh_frequency)

    scheduler.add_job(pc_update_recommendations_view_with_geolocation, 'cron',
                      [app],
                      minute=discovery_view_refresh_frequency)

    scheduler.add_job(pc_clean_discovery_views, 'cron',
                      [app],
                      hour=clean_discovery_frequency)

    scheduler.start()
