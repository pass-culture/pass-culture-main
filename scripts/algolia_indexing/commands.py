from flask import current_app as app

from scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database, \
    batch_deleting_expired_offers_in_algolia, batch_indexing_offers_in_algolia_by_venue, \
    batch_indexing_offers_in_algolia_by_venue_provider, batch_indexing_offers_in_algolia_by_offer


def process_offers():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_offer(client=app.redis_client)


def process_offers_by_venue():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_venue(client=app.redis_client)


def process_offers_by_venue_provider():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_venue_provider(client=app.redis_client)


def process_offers_from_database():
    with app.app_context():
        batch_indexing_offers_in_algolia_from_database(client=app.redis_client)


def process_expired_offers():
    with app.app_context():
        batch_deleting_expired_offers_in_algolia(client=app.redis_client)
