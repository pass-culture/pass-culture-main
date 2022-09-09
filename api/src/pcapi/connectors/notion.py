import logging

from notion_client import APIResponseError
from notion_client import Client

from pcapi import settings
from pcapi.core.providers import models as providers_models


logger = logging.getLogger(__name__)


PROVIDER_API_ERRORS_DATABASE_ID = "e7bd2f6ddedf43f7a7bc87849caaa3ed"


def add_to_synchronization_error_database(exception: Exception, venue_provider: providers_models.VenueProvider) -> None:
    if settings.IS_DEV:
        return
    provider_name = venue_provider.provider.name
    venue_id = venue_provider.venueId
    venue_id_at_offer_provider = venue_provider.venueIdAtOfferProvider
    try:
        notion = Client(auth=settings.NOTION_TOKEN)
        notion.pages.create(
            parent={"database_id": PROVIDER_API_ERRORS_DATABASE_ID},
            properties={
                "Détail": {
                    "title": [{"text": {"content": str(exception)[:2000]}}],
                },
                "Type": {"select": {"name": exception.__class__.__name__}},
                "Provider": {"select": {"name": provider_name}},
                "VenueId": {
                    "rich_text": [{"text": {"content": str(venue_id)}}],
                },
                "VenueIdAtOfferProvider": {"rich_text": [{"text": {"content": str(venue_id_at_offer_provider)}}]},
                "Environnement": {"select": {"name": settings.ENV}},
                "Statut": {"select": {"name": "New"}},
            },
        )
    except APIResponseError as error:
        logger.exception(
            "Could not create page to notion database",
            extra={
                "error": str(error),
                "error_code": error.code,
            },
        )
