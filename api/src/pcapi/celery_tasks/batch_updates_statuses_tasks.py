import datetime

from pydantic import BaseModel as BaseModelV2

from pcapi.core.educational import repository as educational_offers_repository
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import repository as offers_repository

from .tasks import celery_async_task


class UpdateAllOffersActiveStatusPayload(BaseModelV2):
    is_active: bool
    user_id: int
    offerer_id: int | None
    venue_id: int | None
    name_or_ean: str | None
    category_id: str | None
    creation_mode: str | None
    status: str | None
    period_beginning_date: datetime.date | None
    period_ending_date: datetime.date | None
    offerer_address_id: int | None


@celery_async_task(
    name="tasks.batch_updates.default.update_all_offers_active_status",
    model=UpdateAllOffersActiveStatusPayload,
)
def update_all_offers_active_status_task(payload: UpdateAllOffersActiveStatusPayload) -> None:
    payload_dict = payload.model_dump()
    # TODO (tcoudray-pass, 13/11/25): this is legacy, should be renamed when we drop the RQ job
    name_or_ean = payload_dict.pop("name_or_ean")
    is_active = payload_dict.pop("is_active")

    query = offers_repository.get_offers_by_filters(name_keywords_or_ean=name_or_ean, **payload_dict)
    query = offers_repository.exclude_offers_from_inactive_venue_provider(query)

    offers_api.batch_update_offers(query, activate=is_active)


class UpdateVenueOffersActiveStatusPayload(BaseModelV2):
    is_active: bool
    venue_id: int
    provider_id: int


@celery_async_task(
    name="tasks.batch_updates.default.update_venue_offers_active_status",
    model=UpdateVenueOffersActiveStatusPayload,
)
def update_venue_offers_active_status_task(payload: UpdateVenueOffersActiveStatusPayload) -> None:
    query = offers_repository.get_synchronized_offers_with_provider_for_venue(payload.venue_id, payload.provider_id)
    offers_api.batch_update_offers(query, activate=payload.is_active)


@celery_async_task(
    name="tasks.batch_updates.default.update_venue_collective_offers_active_status",
    model=UpdateVenueOffersActiveStatusPayload,
)
def update_venue_collective_offers_active_status_task(payload: UpdateVenueOffersActiveStatusPayload) -> None:
    query = educational_offers_repository.get_synchronized_collective_offers_with_provider_for_venue(
        payload.venue_id,
        payload.provider_id,
    )
    educational_api_offer.batch_update_collective_offers(query, {"isActive": payload.is_active})
