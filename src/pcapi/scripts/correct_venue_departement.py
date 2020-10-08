from pcapi.models import VenueSQLEntity
from pcapi.repository import repository


def correct_venue_departement():
    venues = VenueSQLEntity.query.filter_by(isVirtual=False).all()
    for venue in venues:
        venue.store_departement_code()
    repository.save(*venues)
