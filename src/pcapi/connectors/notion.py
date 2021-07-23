import logging

from notion_client import APIResponseError
from notion_client import Client

from pcapi import settings


logger = logging.getLogger(__name__)


PROVIDER_API_ERRORS_DATABASE_ID = "e7bd2f6ddedf43f7a7bc87849caaa3ed"


def add_to_synchronization_error_database(
    title: str,
    provider_name: str,
    venue_id: str,
    venue_id_at_offer_provider: str,
):
    if settings.IS_DEV:
        return

    try:
        notion = Client(auth=settings.NOTION_TOKEN)
        notion.pages.create(
            parent={"database_id": PROVIDER_API_ERRORS_DATABASE_ID},
            properties={
                "Titre": {
                    "title": [{"text": {"content": title}}],
                },
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
