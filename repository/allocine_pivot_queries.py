from models import AllocinePivot, Venue


def has_allocine_pivot_for_venue(venue: Venue) -> bool:
    allocine_link = AllocinePivot.query \
        .filter_by(siret=venue.siret) \
        .first()
    return allocine_link is not None


def get_allocine_theaterId_for_venue(venue: Venue) -> str:
    allocine_link = AllocinePivot.query \
        .filter_by(siret=venue.siret) \
        .first()
    return allocine_link.theaterId if allocine_link else None
