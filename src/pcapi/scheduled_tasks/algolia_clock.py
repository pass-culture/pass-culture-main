# Loading variables should always be the first thing, before any other load
from pcapi.load_environment_variables import load_environment_variables
load_environment_variables()

import os

import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from sqlalchemy import orm

from pcapi.algolia.infrastructure.worker import process_multi_indexing
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.decorators import log_cron, cron_context, cron_require_feature
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer, \
    batch_indexing_offers_in_algolia_by_venue, \
    batch_deleting_expired_offers_in_algolia, batch_processing_offer_ids_in_error
from pcapi.utils.config import REDIS_URL

@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
def index_offers_in_algolia_by_offer(app):
    batch_indexing_offers_in_algolia_by_offer(client=app.redis_client)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
def index_offers_in_algolia_by_venue(app):
    batch_indexing_offers_in_algolia_by_venue(client=app.redis_client)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
def index_offers_in_algolia_by_venue_provider(app):
    process_multi_indexing(client=app.redis_client)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
def delete_expired_offers_in_algolia(app):
    batch_deleting_expired_offers_in_algolia(client=app.redis_client)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
def index_offers_in_error_in_algolia_by_offer(app):
    batch_processing_offer_ids_in_error(client=app.redis_client)


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
    algolia_cron_indexing_offers_in_error_by_offer_frequency = os.environ.get(
        'ALGOLIA_CRON_INDEXING_OFFERS_IN_ERROR_BY_OFFER_FREQUENCY', '10')

    orm.configure_mappers()
    scheduler = BlockingScheduler()

    scheduler.add_job(index_offers_in_algolia_by_offer, 'cron',
                      [app],
                      minute=algolia_cron_indexing_offers_by_offer_frequency)

    scheduler.add_job(index_offers_in_algolia_by_venue_provider, 'cron',
                      [app],
                      minute=algolia_cron_indexing_offers_by_venue_frequency)

    scheduler.add_job(index_offers_in_algolia_by_venue, 'cron',
                      [app],
                      minute=algolia_cron_indexing_offers_by_venue_provider_frequency)

    scheduler.add_job(delete_expired_offers_in_algolia, 'cron',
                      [app],
                      day='*', hour='1')

    scheduler.add_job(index_offers_in_error_in_algolia_by_offer, 'cron',
                      [app],
                      minute=algolia_cron_indexing_offers_in_error_by_offer_frequency)

    scheduler.start()
