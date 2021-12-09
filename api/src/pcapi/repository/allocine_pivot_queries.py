from pcapi.core.offerers.models import Venue
from pcapi.core.providers.models import AllocinePivot


def get_allocine_pivot_for_venue(venue: Venue) -> AllocinePivot:
    return AllocinePivot.query.filter_by(siret=venue.siret).one_or_none()
