import os

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from mailjet_rest import Client
from sqlalchemy import orm

from local_providers.provider_manager import \
    synchronize_data_for_provider, synchronize_venue_providers_for_provider
from models.db import db
from models.beneficiary_import import BeneficiaryImportSources
from models.feature import FeatureToggle
from repository import discovery_view_queries, discovery_view_v3_queries
from repository.feature_queries import feature_write_dashboard_enabled, feature_clean_seen_offers_enabled
from repository.provider_queries import get_provider_by_local_class
from repository.seen_offer_queries import remove_old_seen_offers
from repository.user_queries import find_most_recent_beneficiary_creation_date_for_source
from scheduled_tasks.decorators import cron_context, cron_require_feature, \
    log_cron
from scripts.beneficiary import old_remote_import, remote_import
from scripts.dashboard.write_dashboard import write_dashboard
from scripts.update_booking_used import \
    update_booking_used_after_stock_occurrence
from utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET
from load_environment_variables import load_environment_variables

load_environment_variables()

DEMARCHES_SIMPLIFIEES_OLD_ENROLLMENT_PROCEDURE_ID = os.environ.get('DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID',
                                                                   None)
DEMARCHES_SIMPLIFIEES_NEW_ENROLLMENT_PROCEDURE_ID = os.environ.get('DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2',
                                                                   None)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.UPDATE_BOOKING_USED)
def update_booking_used(app):
    update_booking_used_after_stock_occurrence()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALLOCINE)
def synchronize_allocine_stocks(app):
    allocine_stocks_provider_id = get_provider_by_local_class("AllocineStocks").id
    synchronize_venue_providers_for_provider(allocine_stocks_provider_id)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_LIBRAIRES)
def synchronize_libraires_stocks(app):
    libraires_stocks_provider_id = get_provider_by_local_class("LibrairesStocks").id
    synchronize_venue_providers_for_provider(libraires_stocks_provider_id)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.BENEFICIARIES_IMPORT)
def pc_old_remote_import_beneficiaries(app):
    procedure_id = int(DEMARCHES_SIMPLIFIEES_OLD_ENROLLMENT_PROCEDURE_ID)
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(BeneficiaryImportSources.demarches_simplifiees, procedure_id)
    old_remote_import.run(import_from_date)


@log_cron
@cron_context
def pc_remote_import_beneficiaries(app):
    procedure_id = int(DEMARCHES_SIMPLIFIEES_NEW_ENROLLMENT_PROCEDURE_ID)
    import_from_date = find_most_recent_beneficiary_creation_date_for_source(BeneficiaryImportSources.demarches_simplifiees, procedure_id)
    remote_import.run(import_from_date)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SAVE_SEEN_OFFERS)
def pc_remove_old_seen_offers(app):
    remove_old_seen_offers()


@log_cron
@cron_context
def pc_write_dashboard(app):
    write_dashboard()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.UPDATE_DISCOVERY_VIEW)
def pc_update_recommendations_view(app):
    discovery_view_queries.refresh()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.UPDATE_DISCOVERY_VIEW)
def pc_update_recommendations_view_with_geolocation(app):
    discovery_view_v3_queries.refresh()


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')

    discovery_view_refresh_frequency = os.environ.get('RECO_VIEW_REFRESH_FREQUENCY', '*')
    old_seen_offers_delete_frequency = os.environ.get('SEEN_OFFERS_DELETE_FREQUENCY', '*')

    orm.configure_mappers()
    scheduler = BlockingScheduler()

    scheduler.add_job(synchronize_allocine_stocks, 'cron',
                      [app],
                      day='*', hour='23')

    scheduler.add_job(synchronize_libraires_stocks, 'cron',
                      [app],
                      day='*', hour='22')

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

    scheduler.start()
