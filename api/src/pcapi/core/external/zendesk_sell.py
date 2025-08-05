import logging
from functools import partial

from pcapi.core.external.zendesk_sell_backends import zendesk_backend
from pcapi.core.external.zendesk_sell_backends.base import ContactFoundMoreThanOneError
from pcapi.core.external.zendesk_sell_backends.base import ContactNotFoundError
from pcapi.core.external.zendesk_sell_backends.base import ZendeskCustomFieldsShort
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.models.feature import FeatureToggle
from pcapi.tasks import zendesk_sell_tasks
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)

SEARCH_PARENT = -1


def is_offerer_only_virtual(offerer: offerers_models.Offerer) -> bool:
    return offerer.managedVenues and all(venue.isVirtual for venue in offerer.managedVenues)


def _get_parent_organization_id(venue: offerers_models.Venue) -> int | None:
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
    return zendesk_backend.create_offerer(offerer, created=True)


def zendesk_update_offerer(zendesk_id: int, offerer: offerers_models.Offerer) -> dict:
    return zendesk_backend.update_offerer(zendesk_id, offerer)


def zendesk_create_venue(venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
    if parent_organization_id == SEARCH_PARENT:
        parent_organization_id = _get_parent_organization_id(venue)

    return zendesk_backend.create_venue(venue, parent_organization_id, created=True)


def zendesk_update_venue(zendesk_id: int, venue: offerers_models.Venue, parent_organization_id: int | None) -> dict:
    if parent_organization_id == SEARCH_PARENT:
        parent_organization_id = _get_parent_organization_id(venue)

    return zendesk_backend.update_venue(zendesk_id, venue, parent_organization_id)


def create_venue(venue: offerers_models.Venue) -> None:
    if not FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
        return

    if venue.isVirtual:
        return

    # API calls to Zendesk Sell are delayed in a GCP task to return quickly
    on_commit(
        partial(
            zendesk_sell_tasks.create_venue_task.delay,
            zendesk_sell_tasks.VenuePayload(venue_id=venue.id),
        )
    )


def do_create_venue(venue_id: int) -> None:
    """Called asynchronously by GCP task"""
    venue = offerers_repository.find_venue_by_id(venue_id)
    if not venue:
        logger.error("Trying to create venue which does not exist", extra={"venue_id": venue_id})
        return

    zendesk_create_venue(venue, SEARCH_PARENT)


def update_venue(venue: offerers_models.Venue) -> None:
    if venue.isVirtual:
        return

    # API calls to Zendesk Sell are delayed in a GCP task to return quickly
    on_commit(
        partial(
            zendesk_sell_tasks.update_venue_task.delay,
            zendesk_sell_tasks.VenuePayload(venue_id=venue.id),
        )
    )


def do_update_venue(venue_id: int) -> None:
    """Called asynchronously by GCP task"""
    venue = offerers_repository.find_venue_by_id(venue_id)
    if not venue:
        logger.error("Trying to update venue which does not exist", extra={"venue_id": venue_id})
        return

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

    if is_offerer_only_virtual(offerer):
        return

    # API calls to Zendesk Sell are delayed in a GCP task to return quickly
    on_commit(
        partial(
            zendesk_sell_tasks.create_offerer_task.delay,
            zendesk_sell_tasks.OffererPayload(offerer_id=offerer.id),
        )
    )


def do_create_offerer(offerer_id: int) -> None:
    """Called asynchronously by GCP task"""
    offerer = offerers_repository.find_offerer_by_id(offerer_id)
    if not offerer:
        logger.error("Trying to create offerer which does not exist", extra={"offerer_id": offerer_id})
        return

    zendesk_create_offerer(offerer)


def update_offerer(offerer: offerers_models.Offerer) -> None:
    if is_offerer_only_virtual(offerer):
        return

    # API calls to Zendesk Sell are delayed in a GCP task to return quickly
    on_commit(
        partial(
            zendesk_sell_tasks.update_offerer_task.delay,
            zendesk_sell_tasks.OffererPayload(offerer_id=offerer.id),
        )
    )


def do_update_offerer(offerer_id: int) -> None:
    """Called asynchronously by GCP task"""
    offerer = offerers_repository.find_offerer_by_id(offerer_id)
    if not offerer:
        logger.error("Trying to update offerer which does not exist", extra={"offerer_id": offerer_id})
        return

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
