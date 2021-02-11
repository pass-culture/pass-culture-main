from rq.decorators import job

from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.repository.venue_provider_queries import get_venue_provider_by_id
from pcapi.workers import worker
from pcapi.workers.decorators import job_context
from pcapi.workers.decorators import log_job


@job(worker.redis_queue, connection=worker.conn)
@job_context
@log_job
def venue_provider_job(venue_provider_id: int) -> None:
    venue_provider = get_venue_provider_by_id(venue_provider_id)
    synchronize_venue_provider(venue_provider)
