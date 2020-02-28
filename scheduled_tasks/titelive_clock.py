import os
import subprocess
from io import StringIO

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from sqlalchemy import orm

from local_providers.venue_provider_worker import update_venues_for_specific_provider
from models.db import db
from models.feature import FeatureToggle
from repository.provider_queries import get_provider_by_local_class
from scheduled_tasks.decorators import log_cron, cron_context, cron_require_feature
from utils.config import API_ROOT_PATH
from utils.logger import logger


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS)
def synchronize_titelive_things(app):
    process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                               + ' --provider TiteLiveThings',
                               shell=True,
                               cwd=API_ROOT_PATH)
    output, error = process.communicate()
    logger.info(StringIO(output))
    logger.info(StringIO(error))


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION)
def synchronize_titelive_thing_descriptions(app):
    process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                               + ' --provider TiteLiveThingDescriptions',
                               shell=True,
                               cwd=API_ROOT_PATH)
    output, error = process.communicate()
    logger.info(StringIO(output))
    logger.info(StringIO(error))


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS)
def synchronize_titelive_thing_thumbs(app):
    process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                               + ' --provider TiteLiveThingThumbs',
                               shell=True,
                               cwd=API_ROOT_PATH)
    output, error = process.communicate()
    logger.info(StringIO(output))
    logger.info(StringIO(error))


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
                      day='*', hour='6')

    scheduler.start()
