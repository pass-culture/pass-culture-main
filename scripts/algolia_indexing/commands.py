from flask import current_app as app

from algolia.infrastructure.api import clear_index
from connectors.redis import delete_all_indexed_offers
from scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database, \
    batch_deleting_expired_offers_in_algolia, batch_indexing_offers_in_algolia_by_venue, \
    batch_indexing_offers_in_algolia_by_venue_provider, batch_indexing_offers_in_algolia_by_offer, \
    _process_venue_provider


@app.manager.command
def process_offers():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_offer(client=app.redis_client)


@app.manager.command
def process_offers_by_venue():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_venue(client=app.redis_client)


@app.manager.command
def process_offers_by_venue_provider():
    with app.app_context():
        batch_indexing_offers_in_algolia_by_venue_provider(client=app.redis_client)


@app.manager.option('-ca',
                    '--clear-algolia',
                    help='Clear algolia index before indexing offers',
                    type=bool)
@app.manager.option('-cr',
                    '--clear-redis',
                    help='Clear redis indexed offers before indexing offers',
                    type=bool)
@app.manager.option('-ep',
                    '--ending-page',
                    help='Ending page for indexing offers',
                    type=int)
@app.manager.option('-l',
                    '--limit',
                    help='Number of offers per page',
                    type=int)
@app.manager.option('-sp',
                    '--starting-page',
                    help='Starting page for indexing offers',
                    type=int)
def process_offers_from_database(clear_algolia: bool = False,
                                 clear_redis: bool = False,
                                 ending_page: int = None,
                                 limit: int = 10000,
                                 starting_page: int = 0):
    with app.app_context():
        if clear_algolia:
            clear_index()
        if clear_redis:
            delete_all_indexed_offers(client=app.redis_client)
        batch_indexing_offers_in_algolia_from_database(client=app.redis_client,
                                                       ending_page=ending_page,
                                                       limit=limit,
                                                       starting_page=starting_page)


@app.manager.command
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
