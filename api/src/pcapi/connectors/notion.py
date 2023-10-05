import logging

from notion_client import Client

from pcapi import settings
from pcapi.core.providers import models as providers_models


logger = logging.getLogger(__name__)


PROVIDER_API_ERRORS_DATABASE_ID = "e7bd2f6ddedf43f7a7bc87849caaa3ed"


def add_venue_provider_error_to_notion_database(
    exception: Exception, venue_provider: providers_models.VenueProvider
) -> None:
    add_to_provider_error_database(
        exception,
        provider_name=venue_provider.provider.name,
        venue_id=str(venue_provider.venueId),
        venue_id_at_offer_provider=venue_provider.venueIdAtOfferProvider,
    )


def add_to_provider_error_database(
    exception: Exception, provider_name: str = "", venue_id: str = "", venue_id_at_offer_provider: str = ""
) -> None:
    if not settings.SEND_SYNCHRONIZATION_ERRORS_TO_NOTION:
        return
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
    except Exception as error:  # pylint: disable=broad-except
        logger.exception(
            "Could not create page to Notion database",
            extra={
                "error": str(error),
            },
        )
