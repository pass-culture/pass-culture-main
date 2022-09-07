import logging

from pcapi.routes.serialization import BaseModel
from pcapi.settings import GCP_ZENDESK_SELL_QUEUE_NAME
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)


class OffererPayload(BaseModel):
    offerer_id: int


class VenuePayload(BaseModel):
    venue_id: int


@task(GCP_ZENDESK_SELL_QUEUE_NAME, "/zendesk_sell/create_offerer")  # type: ignore [arg-type]
def create_offerer_task(payload: OffererPayload) -> None:
    from pcapi.core.users.external import zendesk_sell

    zendesk_sell.do_create_offerer(payload.offerer_id)


@task(GCP_ZENDESK_SELL_QUEUE_NAME, "/zendesk_sell/update_offerer")  # type: ignore [arg-type]
def update_offerer_task(payload: OffererPayload) -> None:
    from pcapi.core.users.external import zendesk_sell

    logger.info("update_offerer_task: payload=%s, payload.offerer_id=%s", payload, payload.offerer_id)
    zendesk_sell.do_update_offerer(payload.offerer_id)


@task(GCP_ZENDESK_SELL_QUEUE_NAME, "/zendesk_sell/create_venue")  # type: ignore [arg-type]
def create_venue_task(payload: VenuePayload) -> None:
    from pcapi.core.users.external import zendesk_sell

    zendesk_sell.do_create_venue(payload.venue_id)


@task(GCP_ZENDESK_SELL_QUEUE_NAME, "/zendesk_sell/update_venue")  # type: ignore [arg-type]
def update_venue_task(payload: VenuePayload) -> None:
    from pcapi.core.users.external import zendesk_sell

    logger.info("update_venue_task: payload=%s, payload.venue_id=%s", payload, payload.venue_id)
    zendesk_sell.do_update_venue(payload.venue_id)
