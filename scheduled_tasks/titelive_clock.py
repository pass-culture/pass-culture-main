import os
import subprocess
from io import StringIO

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from sqlalchemy import orm

from local_providers.venue_provider_worker import update_venues_for_specific_provider
from models.db import db
from repository.feature_queries import feature_cron_synchronize_titelive_things, \
    feature_cron_synchronize_titelive_descriptions, \
    feature_cron_synchronize_titelive_thumbs, feature_cron_synchronize_titelive_stocks
from repository.provider_queries import get_provider_by_local_class
from scheduled_tasks.decorators import log_cron, cron_context
from utils.config import API_ROOT_PATH
from utils.logger import logger


@log_cron
@cron_context
def pc_synchronize_titelive_things(app):
    process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                               + ' --provider TiteLiveThings',
                               shell=True,
                               cwd=API_ROOT_PATH)
    output, error = process.communicate()
    logger.info(StringIO(output))
    logger.info(StringIO(error))


@log_cron
@cron_context
def pc_synchronize_titelive_descriptions(app):
    process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                               + ' --provider TiteLiveThingDescriptions',
                               shell=True,
                               cwd=API_ROOT_PATH)
    output, error = process.communicate()
    logger.info(StringIO(output))
    logger.info(StringIO(error))


@log_cron
@cron_context
def pc_synchronize_titelive_thumbs(app):
    process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                               + ' --provider TiteLiveThingThumbs',
                               shell=True,
                               cwd=API_ROOT_PATH)
    output, error = process.communicate()
    logger.info(StringIO(output))
    logger.info(StringIO(error))


@log_cron
@cron_context
def pc_synchronize_titelive_stocks(app):
    titelive_stocks_provider_id = get_provider_by_local_class("TiteLiveStocks").id
    update_venues_for_specific_provider(titelive_stocks_provider_id)


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    orm.configure_mappers()
    scheduler = BlockingScheduler()

    if feature_cron_synchronize_titelive_things():
        scheduler.add_job(pc_synchronize_titelive_things, 'cron',
                          [app],
                          day='*', hour='1')

    if feature_cron_synchronize_titelive_descriptions():
        scheduler.add_job(pc_synchronize_titelive_descriptions, 'cron',
                          [app],
                          day='*', hour='2')

    if feature_cron_synchronize_titelive_thumbs():
        scheduler.add_job(pc_synchronize_titelive_thumbs, 'cron',
                          [app],
                          day='*', hour='3')

    if feature_cron_synchronize_titelive_stocks():
        scheduler.add_job(pc_synchronize_titelive_stocks, 'cron',
                          [app],
                          day='*', hour='6')

    scheduler.start()
