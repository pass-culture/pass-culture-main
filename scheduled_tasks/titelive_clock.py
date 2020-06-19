import os

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from sqlalchemy import orm

from local_providers.provider_manager import synchronize_data_for_provider
from local_providers.venue_provider_worker import update_venues_for_specific_provider
from models.db import db
from models.feature import FeatureToggle
from repository.provider_queries import get_provider_by_local_class
from scheduled_tasks.decorators import log_cron, cron_context, cron_require_feature
from load_environment_configuration_variables import load_environment_configuration_variables

load_environment_configuration_variables()

@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS)
def synchronize_titelive_things(app):
    synchronize_data_for_provider("TiteLiveThings")


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION)
def synchronize_titelive_thing_descriptions(app):
    synchronize_data_for_provider("TiteLiveThingDescriptions")


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS)
def synchronize_titelive_thing_thumbs(app):
    synchronize_data_for_provider("TiteLiveThingThumbs")


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE)
def synchronize_titelive_stocks(app):
    titelive_stocks_provider_id = get_provider_by_local_class("TiteLiveStocks").id
    update_venues_for_specific_provider(titelive_stocks_provider_id)


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    orm.configure_mappers()
    scheduler = BlockingScheduler()

    scheduler.add_job(synchronize_titelive_things, 'cron',
                      [app],
                      day='*', hour='1')

    scheduler.add_job(synchronize_titelive_thing_descriptions, 'cron',
                      [app],
                      day='*', hour='2')

    scheduler.add_job(synchronize_titelive_thing_thumbs, 'cron',
                      [app],
                      day='*', hour='3')

    scheduler.add_job(synchronize_titelive_stocks, 'cron',
                      [app],
                      day='*', hour='2', minute='30')

    scheduler.start()
