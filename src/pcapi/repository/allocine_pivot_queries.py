from pcapi.models import AllocinePivot
from pcapi.models import VenueSQLEntity


def has_allocine_pivot_for_venue(venue: VenueSQLEntity) -> bool:
    allocine_link = AllocinePivot.query.filter_by(siret=venue.siret).first()
    return allocine_link is not None


def get_allocine_theaterId_for_venue(venue: VenueSQLEntity) -> str:
    allocine_link = AllocinePivot.query.filter_by(siret=venue.siret).first()
    return allocine_link.theaterId if allocine_link else None
