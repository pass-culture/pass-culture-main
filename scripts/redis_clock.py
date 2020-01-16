import os
import time
from functools import wraps

import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from sqlalchemy import orm

from models.db import db
from repository.feature_queries import feature_cron_algolia_indexing_offers_enabled, \
    feature_cron_algolia_indexing_offers_from_local_providers_enabled, \
    feature_cron_algolia_indexing_offers_by_venue_enabled
from scripts.algolia_indexing.indexing import indexing_offers_in_algolia, batch_indexing_offers_in_algolia_by_venue_ids, \
    indexing_offers_in_algolia_from_local_providers
from scripts.cron_logger.cron_logger import build_cron_log_message
from scripts.cron_logger.cron_status import CronStatus
from utils.config import REDIS_URL
from utils.logger import logger

ALGOLIA_CRON_INDEXING_FREQUENCY = os.environ.get('ALGOLIA_CRON_INDEXING_FREQUENCY', '*')
ALGOLIA_CRON_INDEXING_BY_VENUE_FREQUENCY = os.environ.get('ALGOLIA_CRON_INDEXING_BY_VENUE_FREQUENCY', '*')
ALGOLIA_CRON_INDEXING_OFFERS_FREQUENCY = os.environ.get('ALGOLIA_CRON_INDEXING_FREQUENCY', '*')
ALGOLIA_CRON_INDEXING_OFFERS_FROM_LOCAL_PROVIDERS_FREQUENCY = os.environ.get(
    'ALGOLIA_CRON_INDEXING_OFFERS_FROM_LOCAL_PROVIDERS_FREQUENCY', '10')

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.redis_client = redis.from_url(url=REDIS_URL, decode_responses=True)
db.init_app(app)


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
def pc_indexing_offers_in_algolia():
    with app.app_context():
        indexing_offers_in_algolia(client=app.redis_client)


@log_cron
def pc_batch_indexing_offers_in_algolia_by_venue_ids():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_venue_ids(client=app.redis_client)


@log_cron
def pc_indexing_offers_in_algolia_from_local_providers():
    with app.app_context():
        indexing_offers_in_algolia_from_local_providers(client=app.redis_client)


if __name__ == '__main__':
    orm.configure_mappers()
    scheduler = BlockingScheduler()

    if feature_cron_algolia_indexing_offers_enabled():
        scheduler.add_job(pc_indexing_offers_in_algolia, 'cron',
                          id='algolia_indexing_offers',
                          minute=ALGOLIA_CRON_INDEXING_OFFERS_FREQUENCY)

    if feature_cron_algolia_indexing_offers_from_local_providers_enabled():
        scheduler.add_job(pc_indexing_offers_in_algolia_from_local_providers, 'cron',
                          id='algolia_indexing_offers_from_local_providers',
                          minute=ALGOLIA_CRON_INDEXING_OFFERS_FROM_LOCAL_PROVIDERS_FREQUENCY)

    if feature_cron_algolia_indexing_offers_by_venue_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_venue_ids, 'cron',
                          id='algolia_indexing_offers_by_venue',
                          minute=ALGOLIA_CRON_INDEXING_BY_VENUE_FREQUENCY)

    scheduler.start()
