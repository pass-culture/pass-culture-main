from rq.decorators import job

from pcapi.core.providers import api
from pcapi.repository import venue_queries
from pcapi.workers import worker
from pcapi.workers.decorators import job_context
from pcapi.workers.decorators import log_job


@job(worker.low_queue, connection=worker.conn)
@job_context
@log_job
def synchronize_stocks_job(stock_details, venue_id: str) -> None:
    venue = venue_queries.find_by_id(venue_id)
    api.synchronize_stocks(stock_details, venue)
