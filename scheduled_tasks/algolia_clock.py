import os

import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from sqlalchemy import orm

from algolia.infrastructure.algolia_worker import process_multi_indexing
from models.db import db
from repository.feature_queries import feature_cron_algolia_indexing_offers_by_offer_enabled, \
    feature_cron_algolia_indexing_offers_by_venue_provider_enabled, \
    feature_cron_algolia_indexing_offers_by_venue_enabled, feature_cron_algolia_deleting_expired_offers_enabled
from scheduled_tasks.decorators import log_cron, cron_context
from scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer, \
    batch_indexing_offers_in_algolia_by_venue, \
    batch_indexing_offers_in_algolia_by_venue_provider, batch_deleting_expired_offers_in_algolia
from utils.config import REDIS_URL


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
def pc_batch_indexing_offers_in_algolia_by_venue_provider():
    with app.app_context():
        process_multi_indexing(client=app.redis_client)


@log_cron
@cron_context
def pc_batch_deleting_expired_offers_in_algolia(app):
    batch_deleting_expired_offers_in_algolia(client=app.redis_client)


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.redis_client = redis.from_url(url=REDIS_URL, decode_responses=True)
    db.init_app(app)

    algolia_cron_indexing_offers_by_offer_frequency = os.environ.get(
        'ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY', '*')
    algolia_cron_indexing_offers_by_venue_frequency = os.environ.get(
        'ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY', '10')
    algolia_cron_indexing_offers_by_venue_provider_frequency = os.environ.get(
        'ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY', '10')

    orm.configure_mappers()
    scheduler = BlockingScheduler()

    if feature_cron_algolia_indexing_offers_by_offer_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_offer, 'cron',
                          [app],
                          minute=algolia_cron_indexing_offers_by_offer_frequency)

    if feature_cron_algolia_indexing_offers_by_venue_provider_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_venue_provider, 'cron',
                          [app],
                          minute=algolia_cron_indexing_offers_by_venue_frequency)

    if feature_cron_algolia_indexing_offers_by_venue_enabled():
        scheduler.add_job(pc_batch_indexing_offers_in_algolia_by_venue, 'cron',
                          [app],
                          minute=algolia_cron_indexing_offers_by_venue_provider_frequency)

    if feature_cron_algolia_deleting_expired_offers_enabled():
        scheduler.add_job(pc_batch_deleting_expired_offers_in_algolia, 'cron',
                          [app],
                          day='*', hour='1')

    scheduler.start()
