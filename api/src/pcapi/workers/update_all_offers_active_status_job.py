from typing import Optional

from flask import _request_ctx_stack

import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
import pcapi.core.users.models as users_models
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def update_all_offers_active_status_job(
    filters: dict, is_active: bool, requesting_user_id: Optional[int] = None
) -> None:
    # Push the user on behalf of which the action is been performed - similar to flask-login
    # Since rq forks the worker to process a job, there is no post job cleanup. Might be a gotcha if
    # another asynchrone job system is used
    # Pushing the use to the context allows logs to be linked to the user
    if requesting_user_id:
        requesting_user = users_models.User.query.get(requesting_user_id)
        ctx = _request_ctx_stack.top
        ctx.user = requesting_user

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
        name_keywords_or_isbn=filters["name_or_isbn"],
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
        name_keywords_or_isbn=filters["name_or_isbn"],
        period_beginning_date=filters["period_beginning_date"],
        period_ending_date=filters["period_ending_date"],
    )
    offers_api.batch_update_offers(query, {"isActive": is_active})
    offers_api.batch_update_collective_offers(collective_offer_query, {"isActive": is_active})
    if collective_offer_template_query is not None:
        offers_api.batch_update_collective_offers_template(collective_offer_template_query, {"isActive": is_active})
