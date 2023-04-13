import logging

from pcapi.core.external.backends import zendesk_backend
from pcapi.core.external.backends.base import ContactFoundMoreThanOneError
from pcapi.core.external.backends.base import ContactNotFoundError
from pcapi.core.external.backends.base import SEARCH_PARENT
from pcapi.core.external.backends.base import ZendeskCustomFieldsShort
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.models.feature import FeatureToggle
from pcapi.tasks import zendesk_sell_tasks


logger = logging.getLogger(__name__)


def is_offerer_only_virtual(offerer: offerers_models.Offerer) -> bool:
    return offerer.managedVenues and all(venue.isVirtual for venue in offerer.managedVenues)


def get_offerer_by_id(offerer: offerers_models.Offerer) -> dict:
    # (offerer id OR siren) AND NO venue id AND NO siret
    offerer_filter: dict = {
        "filter": {
            "attribute": {"name": "custom_fields." + ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value},
            "parameter": {"eq": offerer.id},
        }
    }

    if offerer.siren:
        offerer_filter = {
            "or": [
                offerer_filter,
                {
                    "filter": {
                        "attribute": {"name": "custom_fields." + ZendeskCustomFieldsShort.SIREN.value},
                        "parameter": {"eq": offerer.siren},
                    }
                },
            ]
        }

    params = {
        "items": [
            {
                "data": {
                    "query": {
                        "filter": {
                            "and": [
                                {
                                    "filter": {
                                        "attribute": {"name": "is_organisation"},
                                        "parameter": {"eq": True},
                                    }
                                },
                                offerer_filter,
                                {
                                    "or": [
                                        {
                                            "filter": {
                                                "attribute": {
                                                    "name": "custom_fields."
                                                    + ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value
                                                },
                                                "parameter": {"is_null": True},
                                            }
                                        },
                                        {
                                            "filter": {
                                                "attribute": {
                                                    "name": "custom_fields."
                                                    + ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value
                                                },
                                                "parameter": {"eq": "0"},
                                            }
                                        },
                                    ]
                                },
                                {
                                    "filter": {
                                        "attribute": {"name": "custom_fields." + ZendeskCustomFieldsShort.SIRET.value},
                                        "parameter": {"is_null": True},
                                    }
                                },
                            ]
                        },
                        "projection": [
                            {"name": "id"},
                            {"name": f"custom_fields.{ZendeskCustomFieldsShort.SIREN.value}"},
                            {"name": f"custom_fields.{ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value}"},
                        ],
                    }
                }
            },
        ]
    }

    try:
        return zendesk_backend.search_contact(params)
    except ContactFoundMoreThanOneError as e:
        contacts = e.items

        # looking for the item that has a product offerer id amongst the found items
        contacts_with_offerer_id = [
            contact
            for contact in contacts
            if contact["custom_fields"][ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value] == str(offerer.id)
        ]

        # we found just one result, we assume it's the offerer, the others seems to be the venues
        if len(contacts_with_offerer_id) == 1:
            return contacts_with_offerer_id[0]
        raise


def get_venue_by_id(venue: offerers_models.Venue) -> dict:
    venue_filter: dict = {
        "filter": {
            "attribute": {"name": f"custom_fields.{ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value}"},
            "parameter": {"eq": venue.id},
        }
    }

    if venue.siret:
        venue_filter = {
            "or": [
                venue_filter,
                {
                    "filter": {
                        "attribute": {"name": "custom_fields." + ZendeskCustomFieldsShort.SIRET.value},
                        "parameter": {"eq": venue.siret},
                    }
                },
            ]
        }

    params = {
        "items": [
            {
                "data": {
                    "query": {
                        "filter": {
                            "and": [
                                {
                                    "filter": {
                                        "attribute": {"name": "is_organisation"},
                                        "parameter": {"eq": True},
                                    }
                                },
                                venue_filter,
                            ]
                        },
                        "projection": [
                            {"name": "id"},
                            {"name": f"custom_fields.{ZendeskCustomFieldsShort.SIRET.value}"},
                            {"name": f"custom_fields.{ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value}"},
                        ],
                    }
                }
            }
        ]
    }

    try:
        return zendesk_backend.search_contact(params)
    except ContactFoundMoreThanOneError as e:
        contacts = e.items

        # looking for the item that has a product venue id amongst the found items
        contacts_with_venue_id = [
            contact
            for contact in contacts
            if contact["custom_fields"][ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value] == str(venue.id)
        ]

        # we found just one result, we assume it's the venue
        if len(contacts_with_venue_id) == 1:
            return contacts_with_venue_id[0]
        raise


def _get_parent_organization_id(venue: offerers_models.Venue) -> int | None:
    try:
        zendesk_offerer = get_offerer_by_id(venue.managingOfferer)
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
    zendesk_sell_tasks.create_venue_task.delay(zendesk_sell_tasks.VenuePayload(venue_id=venue.id))


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
    zendesk_sell_tasks.update_venue_task.delay(zendesk_sell_tasks.VenuePayload(venue_id=venue.id))


def do_update_venue(venue_id: int) -> None:
    """Called asynchronously by GCP task"""
    venue = offerers_repository.find_venue_by_id(venue_id)
    if not venue:
        logger.error("Trying to update venue which does not exist", extra={"venue_id": venue_id})
        return

    try:
        zendesk_venue_data = get_venue_by_id(venue)
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
    zendesk_sell_tasks.create_offerer_task.delay(zendesk_sell_tasks.OffererPayload(offerer_id=offerer.id))


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
    zendesk_sell_tasks.update_offerer_task.delay(zendesk_sell_tasks.OffererPayload(offerer_id=offerer.id))


def do_update_offerer(offerer_id: int) -> None:
    """Called asynchronously by GCP task"""
    offerer = offerers_repository.find_offerer_by_id(offerer_id)
    if not offerer:
        logger.error("Trying to update offerer which does not exist", extra={"offerer_id": offerer_id})
        return

    try:
        zendesk_offerer_data = get_offerer_by_id(offerer)
    except ContactFoundMoreThanOneError as err:
        logger.warning("Error while updating offerer in Zendesk Sell: %s", err, extra={"offerer_id": offerer.id})
    except ContactNotFoundError:
        if FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
            zendesk_create_offerer(offerer)
    else:
        zendesk_offerer_id = zendesk_offerer_data["id"]
        zendesk_update_offerer(zendesk_offerer_id, offerer)
