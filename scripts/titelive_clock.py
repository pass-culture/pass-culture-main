import os
import subprocess
import time
from functools import wraps
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
from scripts.cron_logger.cron_logger import build_cron_log_message
from scripts.cron_logger.cron_status import CronStatus
from utils.config import API_ROOT_PATH
from utils.logger import logger

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)

TITELIVE_STOCKS_PROVIDER_NAME = "TiteLiveStocks"


def log_cron(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(build_cron_log_message(name=func.__name__, status=CronStatus.STARTED))

        result = func(*args, **kwargs)

        end_time = time.time()
        duration = end_time - start_time
        logger.info(build_cron_log_message(name=func.__name__, status=CronStatus.ENDED, duration=duration))
        return result

    return wrapper


@log_cron
def pc_synchronize_titelive_things():
    with app.app_context():
        process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                                   + ' --provider TiteLiveThings',
                                   shell=True,
                                   cwd=API_ROOT_PATH)
        output, error = process.communicate()
        logger.info(StringIO(output))
        logger.info(StringIO(error))


@log_cron
def pc_synchronize_titelive_descriptions():
    with app.app_context():
        process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                                   + ' --provider TiteLiveThingDescriptions',
                                   shell=True,
                                   cwd=API_ROOT_PATH)
        output, error = process.communicate()
        logger.info(StringIO(output))
        logger.info(StringIO(error))


@log_cron
def pc_synchronize_titelive_thumbs():
    with app.app_context():
        process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                                   + ' --provider TiteLiveThingThumbs',
                                   shell=True,
                                   cwd=API_ROOT_PATH)
        output, error = process.communicate()
        logger.info(StringIO(output))
        logger.info(StringIO(error))


@log_cron
def pc_synchronize_titelive_stocks():
    with app.app_context():
        with app.app_context():
            titelive_stocks_provider_id = get_provider_by_local_class(TITELIVE_STOCKS_PROVIDER_NAME).id
            update_venues_for_specific_provider(titelive_stocks_provider_id)


if __name__ == '__main__':
    orm.configure_mappers()
    scheduler = BlockingScheduler()

    if feature_cron_synchronize_titelive_things():
        scheduler.add_job(pc_synchronize_titelive_things, 'cron', id='synchronize_titelive_things',
                          day='*', hour='1')

    if feature_cron_synchronize_titelive_descriptions():
        scheduler.add_job(pc_synchronize_titelive_descriptions, 'cron', id='synchronize_titelive_descriptions',
                          day='*', hour='2')

    if feature_cron_synchronize_titelive_thumbs():
        scheduler.add_job(pc_synchronize_titelive_thumbs, 'cron', id='synchronize_titelive_thumbs',
                          day='*', hour='3')

    if feature_cron_synchronize_titelive_stocks():
        scheduler.add_job(pc_synchronize_titelive_stocks, 'cron', id='synchronize_titelive_stocks',
                          day='*', hour='6')

    scheduler.start()
