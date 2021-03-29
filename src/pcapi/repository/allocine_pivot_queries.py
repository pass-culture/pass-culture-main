from pcapi.models import AllocinePivot
from pcapi.models import Venue


def has_allocine_pivot_for_venue(venue: Venue) -> bool:
    allocine_link = AllocinePivot.query.filter_by(siret=venue.siret).first()
    return allocine_link is not None


def get_allocine_pivot_for_venue(venue: Venue) -> AllocinePivot:
    allocine_pivot = AllocinePivot.query.filter_by(siret=venue.siret).first_or_404(
        f"No Allocine pivot was found for the venue with SIRET: {venue.siret}"
    )
    return allocine_pivot
