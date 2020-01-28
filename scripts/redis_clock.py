import os
import time
from functools import wraps

import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from sqlalchemy import orm

from models.db import db
from repository.feature_queries import feature_cron_algolia_indexing_offers_by_offer_enabled, \
    feature_cron_algolia_indexing_offers_by_venue_provider_enabled, \
    feature_cron_algolia_indexing_offers_by_venue_enabled, feature_cron_algolia_deleting_expired_offers_enabled
from scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer, \
    batch_indexing_offers_in_algolia_by_venue, \
    batch_indexing_offers_in_algolia_by_venue_provider, batch_deleting_expired_offers_in_algolia
from scripts.cron_logger.cron_logger import build_cron_log_message
from scripts.cron_logger.cron_status import CronStatus
from utils.config import REDIS_URL
from utils.logger import logger

ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY = os.environ.get(
    'ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY', '*')
ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY = os.environ.get(
    'ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY', '10')
ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY = os.environ.get(
    'ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY', '10')
ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY = os.environ.get(
    'ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY', '10')

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
def pc_batch_indexing_offers_in_algolia_by_offer():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_offer(client=app.redis_client)


@log_cron
def pc_batch_indexing_offers_in_algolia_by_venue():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_venue(client=app.redis_client)


@log_cron
def pc_batch_indexing_offers_in_algolia_by_venue_provider():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_venue_provider(client=app.redis_client)


@log_cron
def pc_batch_deleting_expired_offers_in_algolia():
    with app.app_context():
        batch_deleting_expired_offers_in_algolia()


if __name__ == '__main__':
    orm.configure_mappers()
    scheduler = BlockingScheduler()

    if feature_cron_algolia_indexing_offers_by_offer_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_offer, 'cron',
                          id='algolia_indexing_offers_by_offer',
                          minute=ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY)

    if feature_cron_algolia_indexing_offers_by_venue_provider_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_venue_provider, 'cron',
                          id='algolia_indexing_offers_by_venue_provider',
                          minute=ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY)

    if feature_cron_algolia_indexing_offers_by_venue_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_venue, 'cron',
                          id='algolia_indexing_offers_by_venue',
                          minute=ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY)

    if feature_cron_algolia_deleting_expired_offers_enabled():
        scheduler.add_job(pc_batch_deleting_expired_offers_in_algolia, 'cron',
                          id='algolia_deleting_expired_offers',
                          day='*',
                          hour='1')

    scheduler.start()
