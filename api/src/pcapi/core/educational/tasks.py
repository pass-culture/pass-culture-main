from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.educational import repository
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.offers import tasks as offers_tasks


@celery_async_task(
    name="tasks.batch_updates.default.update_venue_collective_offers_active_status",
    model=offers_tasks.UpdateVenueOffersActiveStatusPayload,
)
def update_venue_collective_offers_active_status_task(
    payload: offers_tasks.UpdateVenueOffersActiveStatusPayload,
) -> None:
    query = repository.get_synchronized_collective_offers_with_provider_for_venue(
        payload.venue_id,
        payload.provider_id,
    )
    educational_api_offer.batch_update_collective_offers(query, {"isActive": payload.is_active})
