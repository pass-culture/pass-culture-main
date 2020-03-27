import os

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from mailjet_rest import Client
from sqlalchemy import orm

from local_providers.provider_manager import \
    synchronize_data_for_provider, synchronize_venue_providers_for_provider
from models import DiscoveryView, DiscoveryViewV3
from models.db import db
from models.feature import FeatureToggle
from repository.feature_queries import feature_write_dashboard_enabled
from repository.provider_queries import get_provider_by_local_class
from repository.user_queries import find_most_recent_beneficiary_creation_date
from scheduled_tasks.decorators import cron_context, cron_require_feature, \
    log_cron
from scripts.beneficiary import remote_import
from scripts.dashboard.write_dashboard import write_dashboard
from scripts.update_booking_used import \
    update_booking_used_after_stock_occurrence
from utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET


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
@cron_require_feature(FeatureToggle.SYNCHRONIZE_BANK_INFORMATION)
def pc_retrieve_offerers_bank_information(app):
    synchronize_data_for_provider("BankInformationProvider")


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.BENEFICIARIES_IMPORT)
def pc_remote_import_beneficiaries(app):
    import_from_date = find_most_recent_beneficiary_creation_date()
    remote_import.run(import_from_date)


@log_cron
@cron_context
def pc_write_dashboard(app):
    write_dashboard()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.UPDATE_DISCOVERY_VIEW)
def pc_update_recommendations_view(app):
    DiscoveryView.refresh()


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION)
def pc_update_recommendations_view_with_geolocation(app):
    DiscoveryViewV3.refresh()


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')

    discovery_view_refresh_frequency = os.environ.get('RECO_VIEW_REFRESH_FREQUENCY', '*')

    orm.configure_mappers()
    scheduler = BlockingScheduler()

    scheduler.add_job(pc_retrieve_offerers_bank_information, 'cron',
                      [app],
                      day='*')

    scheduler.add_job(synchronize_allocine_stocks, 'cron',
                      [app],
                      day='*', hour='23')

    scheduler.add_job(synchronize_libraires_stocks, 'cron',
                      [app],
                      day='*', hour='22')

    scheduler.add_job(pc_remote_import_beneficiaries, 'cron',
                      [app],
                      day='*')

    if feature_write_dashboard_enabled():
        scheduler.add_job(pc_write_dashboard, 'cron',
                          [app],
                          day='*', hour='4')

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
