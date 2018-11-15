# from sqlalchemy import func

from models import PcObject, ApiErrors
from models import Venue
from models.db import db
from models.venue import TooManyVirtualVenuesException



def save_venue(venue):
    try:
        PcObject.check_and_save(venue)
    except TooManyVirtualVenuesException:
        errors = ApiErrors()
        errors.addError('isVirtual', 'Un lieu pour les offres numériques existe déjà pour cette structure')
        raise errors


def find_by_id(venue_id):
    return Venue.query.filter_by(id=venue_id).first()
