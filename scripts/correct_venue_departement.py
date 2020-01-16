from models import Venue


def correct_venue_departement():
    venues = Venue.query.filter_by(isVirtual=False).all()
    for venue in venues:
        venue.store_departement_code()
    Repository.save(*venues)
