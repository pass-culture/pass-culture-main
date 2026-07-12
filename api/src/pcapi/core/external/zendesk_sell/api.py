import logging
import typing
from functools import partial

from pcapi import settings
from pcapi.core.external.zendesk_sell.backends.base import ContactFoundMoreThanOneError
from pcapi.core.external.zendesk_sell.backends.base import ContactNotFoundError
from pcapi.core.external.zendesk_sell.backends.base import ZendeskCustomFieldsShort
from pcapi.core.external.zendesk_sell.backends.logger import LoggerBackend
from pcapi.core.external.zendesk_sell.backends.testing import TestingBackend
from pcapi.core.external.zendesk_sell.backends.zendesk_sell import ZendeskSellBackend
from pcapi.core.external.zendesk_sell.backends.zendesk_sell import ZendeskSellReadOnlyBackend
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.models.feature import FeatureToggle
from pcapi.utils.transaction_manager import on_commit

from . import serialization
from . import tasks


type Backend = ZendeskSellBackend | ZendeskSellReadOnlyBackend | LoggerBackend | TestingBackend

BACKEND_BY_KEY: typing.Final[dict[str, type[Backend]]] = {
    "ZendeskSellBackend": ZendeskSellBackend,
    "ZendeskSellReadOnlyBackend": ZendeskSellReadOnlyBackend,
    "LoggerBackend": LoggerBackend,
    "TestingBackend": TestingBackend,
    "pcapi.core.external.zendesk_sell.backends.zendesk_sell.ZendeskSellBackend": ZendeskSellBackend,
    "pcapi.core.external.zendesk_sell.backends.zendesk_sell.ZendeskSellReadOnlyBackend": ZendeskSellReadOnlyBackend,
    "pcapi.core.external.zendesk_sell.backends.logger.LoggerBackend": LoggerBackend,
}
logger = logging.getLogger(__name__)

SEARCH_PARENT = -1


def get_backend() -> Backend:
    return BACKEND_BY_KEY[settings.ZENDESK_SELL_BACKEND]()


def _get_parent_organization_id(venue: offerers_models.Venue) -> int | None:
    zendesk_backend = get_backend()
    try:
        zendesk_offerer = zendesk_backend.get_offerer_by_id(venue.managingOfferer)
    except ContactFoundMoreThanOneError as e:
        for item in e.items:
            logger.warning(
                "Multiple results on Zendesk Sell search for offerer id %s",
                venue.managingOffererId,
                extra={
                    "sell_id ": item["id"],
                    "offerer_id": item["custom_fields"][ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value],
                    "siren": item["custom_fields"][ZendeskCustomFieldsShort.SIREN.value],
                },
            )
        return None
    except ContactNotFoundError:
        if not FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
            return None
        new_zendesk_offerer = zendesk_create_offerer(venue.managingOfferer)
        return new_zendesk_offerer["id"]
    return zendesk_offerer["id"]


def zendesk_create_offerer(offerer: offerers_models.Offerer) -> dict:
    zendesk_backend = get_backend()
    return zendesk_backend.create_offerer(offerer, created=True)


def zendesk_update_offerer(zendesk_id: int, offerer: offerers_models.Offerer) -> dict:
    zendesk_backend = get_backend()
    return zendesk_backend.update_offerer(zendesk_id, offerer)


def zendesk_create_venue(venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
    if parent_organization_id == SEARCH_PARENT:
        parent_organization_id = _get_parent_organization_id(venue)

    zendesk_backend = get_backend()
    return zendesk_backend.create_venue(venue, parent_organization_id, created=True)


def zendesk_update_venue(zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
    if parent_organization_id == SEARCH_PARENT:
        parent_organization_id = _get_parent_organization_id(venue)

    zendesk_backend = get_backend()
    return zendesk_backend.update_venue(zendesk_id, venue, parent_organization_id)


def create_venue(venue: offerers_models.Venue) -> None:
    if not FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
        return

    # API calls to Zendesk Sell are delayed to return quickly
    on_commit(
        partial(
            tasks.create_venue_task.delay,
            serialization.VenuePayload(venue_id=venue.id).model_dump(),
        )
    )


def do_create_venue(venue_id: int) -> None:
    """Called asynchronously by GCP or Celery task"""
    venue = offerers_repository.find_venue_by_id_with_address(venue_id)
    if not venue:
        logger.error("Trying to create venue which does not exist", extra={"venue_id": venue_id})
        return

    zendesk_create_venue(venue, SEARCH_PARENT)


def update_venue(venue: offerers_models.Venue) -> None:
    # API calls to Zendesk Sell are delayed to return quickly
    on_commit(
        partial(
            tasks.update_venue_task.delay,
            serialization.VenuePayload(venue_id=venue.id).model_dump(),
        )
    )


def do_update_venue(venue_id: int) -> None:
    """Called asynchronously by GCP or Celery task"""
    venue = offerers_repository.find_venue_by_id_with_address(venue_id)
    if not venue:
        logger.error("Trying to update venue which does not exist", extra={"venue_id": venue_id})
        return

    zendesk_backend = get_backend()
    try:
        zendesk_venue_data = zendesk_backend.get_venue_by_id(venue)
    except ContactFoundMoreThanOneError as err:
        logger.warning("Error while updating venue in Zendesk Sell: %s", err, extra={"venue_id": venue.id})
    except ContactNotFoundError:
        if FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
            zendesk_create_venue(venue, SEARCH_PARENT)
    else:
        zendesk_venue_id = zendesk_venue_data["id"]
        zendesk_update_venue(zendesk_venue_id, venue, SEARCH_PARENT)


def create_offerer(offerer: offerers_models.Offerer) -> None:
    if not FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
        return

    # API calls to Zendesk Sell are delayed to return quickly
    on_commit(
        partial(
            tasks.create_offerer_task.delay,
            serialization.OffererPayload(offerer_id=offerer.id).model_dump(),
        )
    )


def do_create_offerer(offerer_id: int) -> None:
    """Called asynchronously by GCP or Celery task"""
    offerer = offerers_repository.find_offerer_by_id(offerer_id)
    if not offerer:
        logger.error("Trying to create offerer which does not exist", extra={"offerer_id": offerer_id})
        return

    zendesk_create_offerer(offerer)


def update_offerer(offerer: offerers_models.Offerer) -> None:
    # API calls to Zendesk Sell are delayed to return quickly
    on_commit(
        partial(
            tasks.update_offerer_task.delay,
            serialization.OffererPayload(offerer_id=offerer.id).model_dump(),
        )
    )


def do_update_offerer(offerer_id: int) -> None:
    """Called asynchronously by GCP or Celery task"""
    offerer = offerers_repository.find_offerer_by_id_with_venues_addresses(offerer_id)
    if not offerer:
        logger.error("Trying to update offerer which does not exist", extra={"offerer_id": offerer_id})
        return

    zendesk_backend = get_backend()
    try:
        zendesk_offerer_data = zendesk_backend.get_offerer_by_id(offerer)
    except ContactFoundMoreThanOneError as err:
        logger.warning("Error while updating offerer in Zendesk Sell: %s", err, extra={"offerer_id": offerer.id})
    except ContactNotFoundError:
        if FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
            zendesk_create_offerer(offerer)
    else:
        zendesk_offerer_id = zendesk_offerer_data["id"]
        zendesk_update_offerer(zendesk_offerer_id, offerer)
