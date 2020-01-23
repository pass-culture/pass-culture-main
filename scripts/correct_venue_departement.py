from models import Venue
from repository import repository


def correct_venue_departement():
    venues = Venue.query.filter_by(isVirtual=False).all()
    for venue in venues:
        venue.store_departement_code()
    repository.save(*venues)
