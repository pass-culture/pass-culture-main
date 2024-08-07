from sqlalchemy.orm import joinedload

from pcapi.core.external.subcategory_suggestion_backends import subcategory_suggestion_backend
from pcapi.core.offerers.models import Venue


def get_most_probable_subcategory_ids(
    offer_name: str, offer_description: str | None = None, venue_id: int | None = None
) -> list[str]:
    venue = Venue.query.filter_by(id=venue_id).options(joinedload(Venue.managingOfferer)).one_or_none()
    subcategory_suggestions = subcategory_suggestion_backend.get_most_probable_subcategories(
        offer_name, offer_description, venue
    )

    return [s.subcategory for s in subcategory_suggestions.most_probable_subcategories]
