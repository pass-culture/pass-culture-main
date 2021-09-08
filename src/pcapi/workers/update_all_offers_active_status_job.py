import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def update_all_offers_active_status_job(filters: dict, is_active: bool) -> None:
    query = offers_repository.get_offers_by_filters(
        user_id=filters["user_id"],
        user_is_admin=filters["is_user_admin"],
        offerer_id=filters["offerer_id"],
        status=filters["status"],
        venue_id=filters["venue_id"],
        category_id=filters["category_id"],
        name_keywords_or_isbn=filters["name_or_isbn"],
        creation_mode=filters["creation_mode"],
        period_beginning_date=filters["period_beginning_date"],
        period_ending_date=filters["period_ending_date"],
    )
    offers_api.batch_update_offers(query, {"isActive": is_active})
