from sqlalchemy import func

from models import Booking, Stock, EventOccurrence, Offer, Venue, Offerer
from models.db import db


def find_all_by_user_id(user_id):
    return Booking.query.filter_by(userId=user_id).all()


def compute_total_booking_value_of_offerer(offerer_id):
    query_event = db.session.query(func.sum(Booking.amount * Booking.quantity))\
        .join(Booking.stock)\
        .join(Stock.eventOccurrence)\
        .join(EventOccurrence.offer)\
        .join(Offer.venue)\
        .join(Venue.managingOfferer)\
        .filter(Offerer.id == offerer_id)\
        .first()

    query_thing = db.session\
        .query(func.sum(Booking.amount * Booking.quantity))\
        .join(Booking.stock)\
        .join(Stock.offer)\
        .join(Offer.venue)\
        .join(Venue.managingOfferer)\
        .filter(Offerer.id == offerer_id)\
        .first()

    return query_event[0] + query_thing[0]
