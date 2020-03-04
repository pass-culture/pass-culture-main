from flask import current_app as app

from scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database, \
    batch_deleting_expired_offers_in_algolia, batch_indexing_offers_in_algolia_by_venue, \
    batch_indexing_offers_in_algolia_by_venue_provider, batch_indexing_offers_in_algolia_by_offer, \
    _process_venue_provider


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


@app.manager.option('-p',
                    '--provider-id',
                    help='Provider id to be processed')
@app.manager.option('-v',
                    '--venue-id',
                    help='Venue id to be processed')
@app.manager.option('-vp',
                    '--venue-provider-id',
                    help='Venue provider id to be processed')
def process_venue_provider_offers_for_algolia(provider_id: str, venue_id: int, venue_provider_id: int):
    _process_venue_provider(client=app.redis_client,
                            provider_id=provider_id,
                            venue_id=venue_id,
                            venue_provider_id=venue_provider_id)
