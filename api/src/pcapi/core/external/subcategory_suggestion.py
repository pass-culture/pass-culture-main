import logging

from sqlalchemy.orm import joinedload

from pcapi.core.external.subcategory_suggestion_backends import subcategory_suggestion_backend
from pcapi.core.offerers.models import Venue


logger = logging.getLogger(__name__)


def get_most_probable_subcategory_ids(
    offer_name: str, offer_description: str | None = None, venue_id: int | None = None
) -> tuple[str, list[str]]:
    venue = Venue.query.filter_by(id=venue_id).options(joinedload(Venue.managingOfferer)).one_or_none()
    subcategory_suggestions = subcategory_suggestion_backend.get_most_probable_subcategories(
        offer_name, offer_description, venue
    )
    call_id = subcategory_suggestions.call_id
    subcategories_list = [s.subcategory for s in subcategory_suggestions.most_probable_subcategories]
    logger.info(
        "Offer Categorisation Data API",
        extra={
            "analyticsSource": "app-pro",
            "offer_data_api_call_id": call_id,
            "offer_subcategories": subcategories_list,
        },
        technical_message_id="offer_categorisation",
    )
    return (call_id, subcategories_list)
