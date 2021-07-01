from pcapi.core.providers import api
from pcapi.repository import venue_queries
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def synchronize_stocks_job(stock_details, venue_id: str) -> None:
    venue = venue_queries.find_by_id(venue_id)
    api.synchronize_stocks(stock_details, venue)
