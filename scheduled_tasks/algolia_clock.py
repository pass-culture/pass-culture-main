import os

import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from sqlalchemy import orm

from models.db import db
from repository.feature_queries import feature_cron_algolia_indexing_offers_by_offer_enabled, \
    feature_cron_algolia_indexing_offers_by_venue_provider_enabled, \
    feature_cron_algolia_indexing_offers_by_venue_enabled, feature_cron_algolia_deleting_expired_offers_enabled
from scheduled_tasks.decorators import log_cron, cron_context
from scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer, \
    batch_indexing_offers_in_algolia_by_venue, \
    batch_indexing_offers_in_algolia_by_venue_provider, batch_deleting_expired_offers_in_algolia
from utils.config import REDIS_URL

ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY = os.environ.get(
    'ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY', '*')
ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY = os.environ.get(
    'ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY', '10')
ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY = os.environ.get(
    'ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY', '10')

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.redis_client = redis.from_url(url=REDIS_URL, decode_responses=True)
db.init_app(app)


@log_cron
@cron_context
def pc_batch_indexing_offers_in_algolia_by_offer(app):
    batch_indexing_offers_in_algolia_by_offer(client=app.redis_client)


@log_cron
@cron_context
def pc_batch_indexing_offers_in_algolia_by_venue(app):
    batch_indexing_offers_in_algolia_by_venue(client=app.redis_client)


@log_cron
@cron_context
def pc_batch_indexing_offers_in_algolia_by_venue_provider(app):
    batch_indexing_offers_in_algolia_by_venue_provider(client=app.redis_client)


@log_cron
@cron_context
def pc_batch_deleting_expired_offers_in_algolia(app):
    batch_deleting_expired_offers_in_algolia(client=app.redis_client)


if __name__ == '__main__':
    orm.configure_mappers()
    scheduler = BlockingScheduler()

    if feature_cron_algolia_indexing_offers_by_offer_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_offer, 'cron',
                          [app],
                          id='algolia_indexing_offers_by_offer',
                          minute=ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY)

    if feature_cron_algolia_indexing_offers_by_venue_provider_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_venue_provider, 'cron',
                          [app],
                          id='algolia_indexing_offers_by_venue_provider',
                          minute=ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY)

    if feature_cron_algolia_indexing_offers_by_venue_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_venue, 'cron',
                          [app],
                          id='algolia_indexing_offers_by_venue',
                          minute=ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY)

    if feature_cron_algolia_deleting_expired_offers_enabled():
        scheduler.add_job(pc_batch_deleting_expired_offers_in_algolia, 'cron',
                          [app],
                          id='algolia_deleting_expired_offers',
                          day='*', hour='1')

    scheduler.start()
