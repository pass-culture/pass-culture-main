from rq.decorators import job

import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
from pcapi.workers import worker
from pcapi.workers.decorators import job_context
from pcapi.workers.decorators import log_job


@job(worker.low_queue, connection=worker.conn)
@job_context
@log_job
def update_all_offers_active_status_job(filters: dict, is_active: bool) -> None:
    query = offers_repository.get_offers_by_filters(
        user_id=filters["user_id"],
        user_is_admin=filters["is_user_admin"],
        offerer_id=filters["offerer_id"],
        status=filters["status"],
        venue_id=filters["venue_id"],
        type_id=filters["type_id"],
        name_keywords=filters["name"],
        creation_mode=filters["creation_mode"],
        period_beginning_date=filters["period_beginning_date"],
        period_ending_date=filters["period_ending_date"],
    )
    offers_api.update_offers_active_status(query, is_active)
