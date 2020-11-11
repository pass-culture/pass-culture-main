from flask import current_app as app

from pcapi.algolia.infrastructure.api import clear_index
from pcapi.connectors.redis import delete_all_indexed_offers
from pcapi.scripts.algolia_indexing.indexing import _process_venue_provider
from pcapi.scripts.algolia_indexing.indexing import batch_deleting_expired_offers_in_algolia
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_venue
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_venue_provider
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database


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


@app.manager.option("-ca", "--clear-algolia", help="Clear algolia index before indexing offers", type=bool)
@app.manager.option("-cr", "--clear-redis", help="Clear redis indexed offers before indexing offers", type=bool)
@app.manager.option("-ep", "--ending-page", help="Ending page for indexing offers", type=int)
@app.manager.option("-l", "--limit", help="Number of offers per page", type=int)
@app.manager.option("-sp", "--starting-page", help="Starting page for indexing offers", type=int)
def process_offers_from_database(
    clear_algolia: bool = False,
    clear_redis: bool = False,
    ending_page: int = None,
    limit: int = 10000,
    starting_page: int = 0,
):
    with app.app_context():
        if clear_algolia:
            clear_index()
        if clear_redis:
            delete_all_indexed_offers(client=app.redis_client)
        batch_indexing_offers_in_algolia_from_database(
            client=app.redis_client, ending_page=ending_page, limit=limit, starting_page=starting_page
        )


@app.manager.option(
    "-a", "--all", action="store_true", dest="all_offers", help="Bypass the two days limit to delete all expired offers"
)
def process_expired_offers(all_offers: bool = False):
    with app.app_context():
        batch_deleting_expired_offers_in_algolia(client=app.redis_client, process_all_expired=all_offers)


@app.manager.option("-p", "--provider-id", help="Provider id to be processed")
@app.manager.option("-v", "--venue-id", help="Venue id to be processed")
@app.manager.option("-vp", "--venue-provider-id", help="Venue provider id to be processed")
def process_venue_provider_offers_for_algolia(provider_id: str, venue_id: int, venue_provider_id: int):
    _process_venue_provider(
        client=app.redis_client, provider_id=provider_id, venue_id=venue_id, venue_provider_id=venue_provider_id
    )
