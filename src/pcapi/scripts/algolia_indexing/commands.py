import logging

from flask import current_app as app

from pcapi.core import search
import pcapi.core.offers.api as offers_api
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_from_database


logger = logging.getLogger(__name__)


@app.manager.command
def process_offers():
    with app.app_context():
        search.index_offers_in_queue(stop_only_when_empty=True)


@app.manager.command
def process_offers_by_venue():
    with app.app_context():
        search.index_offers_of_venues_in_queue()


@app.manager.option("--clear", help="Clear search index", type=bool)
@app.manager.option("-ep", "--ending-page", help="Ending page for indexing offers", type=int)
@app.manager.option("-l", "--limit", help="Number of offers per page", type=int)
@app.manager.option("-sp", "--starting-page", help="Starting page for indexing offers", type=int)
def process_offers_from_database(
    clear: bool = False,
    ending_page: int = None,
    limit: int = 10000,
    starting_page: int = 0,
):
    with app.app_context():
        if clear:
            search.unindex_all_offers()
        batch_indexing_offers_in_algolia_from_database(
            ending_page=ending_page, limit=limit, starting_page=starting_page
        )


@app.manager.option(
    "-a", "--all", action="store_true", dest="all_offers", help="Bypass the two days limit to delete all expired offers"
)
def process_expired_offers(all_offers: bool = False):
    with app.app_context():
        offers_api.unindex_expired_offers(process_all_expired=all_offers)
