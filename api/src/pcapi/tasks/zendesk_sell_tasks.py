import logging

from pcapi.settings import GCP_ZENDESK_SELL_QUEUE_NAME
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)


@task(GCP_ZENDESK_SELL_QUEUE_NAME, "/zendesk_sell/create_offerer")  # type: ignore [arg-type]
def create_offerer_task(offerer_id: int) -> None:
    from pcapi.core.users.external import zendesk_sell

    zendesk_sell.do_create_offerer(offerer_id)


@task(GCP_ZENDESK_SELL_QUEUE_NAME, "/zendesk_sell/update_offerer")  # type: ignore [arg-type]
def update_offerer_task(offerer_id: int) -> None:
    from pcapi.core.users.external import zendesk_sell

    zendesk_sell.do_update_offerer(offerer_id)


@task(GCP_ZENDESK_SELL_QUEUE_NAME, "/zendesk_sell/create_venue")  # type: ignore [arg-type]
def create_venue_task(venue_id: int) -> None:
    from pcapi.core.users.external import zendesk_sell

    zendesk_sell.do_create_venue(venue_id)


@task(GCP_ZENDESK_SELL_QUEUE_NAME, "/zendesk_sell/update_venue")  # type: ignore [arg-type]
def update_venue_task(venue_id: int) -> None:
    from pcapi.core.users.external import zendesk_sell

    zendesk_sell.do_update_venue(venue_id)
