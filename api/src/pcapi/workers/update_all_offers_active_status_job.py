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
    collective_offer_query = offers_repository.get_collective_offers_by_filters(
        user_id=filters["user_id"],
        user_is_admin=filters["is_user_admin"],
        offerer_id=filters["offerer_id"],
        status=filters["status"],
        venue_id=filters["venue_id"],
        category_id=filters["category_id"],
        name_keywords=filters["name_or_isbn"],
        period_beginning_date=filters["period_beginning_date"],
        period_ending_date=filters["period_ending_date"],
    )
    collective_offer_template_query = offers_repository.get_collective_offers_template_by_filters(
        user_id=filters["user_id"],
        user_is_admin=filters["is_user_admin"],
        offerer_id=filters["offerer_id"],
        status=filters["status"],
        venue_id=filters["venue_id"],
        category_id=filters["category_id"],
        name_keywords=filters["name_or_isbn"],
        period_beginning_date=filters["period_beginning_date"],
        period_ending_date=filters["period_ending_date"],
    )
    offers_api.batch_update_offers(query, {"isActive": is_active})
    offers_api.batch_update_collective_offers(collective_offer_query, {"isActive": is_active})
    if collective_offer_template_query is not None:
        offers_api.batch_update_collective_offers_template(collective_offer_template_query, {"isActive": is_active})


@job(worker.low_queue)
def update_all_collective_offers_active_status_job(filters: dict, is_active: bool) -> None:
    collective_offer_query = offers_repository.get_collective_offers_by_filters(
        user_id=filters["user_id"],
        user_is_admin=filters["is_user_admin"],
        offerer_id=filters["offerer_id"],
        status=filters["status"],
        venue_id=filters["venue_id"],
        category_id=filters["category_id"],
        name_keywords=filters["name_or_isbn"],
        period_beginning_date=filters["period_beginning_date"],
        period_ending_date=filters["period_ending_date"],
    )
    collective_offer_template_query = offers_repository.get_collective_offers_template_by_filters(
        user_id=filters["user_id"],
        user_is_admin=filters["is_user_admin"],
        offerer_id=filters["offerer_id"],
        status=filters["status"],
        venue_id=filters["venue_id"],
        category_id=filters["category_id"],
        name_keywords=filters["name_or_isbn"],
        period_beginning_date=filters["period_beginning_date"],
        period_ending_date=filters["period_ending_date"],
    )
    offers_api.batch_update_collective_offers(collective_offer_query, {"isActive": is_active})
    offers_api.batch_update_collective_offers_template(collective_offer_template_query, {"isActive": is_active})


@job(worker.low_queue)
def update_venue_synchronized_offers_active_status_job(venue_id: int, provider_id: int, is_active: bool) -> None:
    venue_synchronized_offers_query = offers_repository.get_synchronized_offers_with_provider_for_venue(
        venue_id, provider_id
    )

    offers_api.batch_update_offers(venue_synchronized_offers_query, {"isActive": is_active})
