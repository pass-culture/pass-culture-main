from pcapi.models import Venue


def find_by_id(venue_id: int) -> Venue:
    return Venue.query.filter_by(id=venue_id).one_or_none()


def find_by_siret(siret):
    return Venue.query.filter_by(siret=siret).one_or_none()


def find_by_managing_offerer_id(offerer_id: int) -> Venue:
    return Venue.query.filter_by(managingOffererId=offerer_id).first()


def find_by_offerer_id_and_is_virtual(offrer_id: int):
    return Venue.query.filter_by(managingOffererId=offrer_id, isVirtual=True).first()
