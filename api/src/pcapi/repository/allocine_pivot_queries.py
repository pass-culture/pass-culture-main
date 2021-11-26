from pcapi.core.offerers.models import Venue
from pcapi.models.allocine_pivot import AllocinePivot


def has_allocine_pivot_for_venue(venue: Venue) -> bool:
    allocine_link = AllocinePivot.query.filter_by(siret=venue.siret).one_or_none()
    return allocine_link is not None


def get_allocine_pivot_for_venue(venue: Venue) -> AllocinePivot:
    return AllocinePivot.query.filter_by(siret=venue.siret).one_or_none()
