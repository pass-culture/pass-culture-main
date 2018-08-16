from sqlalchemy import func

from models import Booking, Stock, EventOccurrence, Offer, Venue, Offerer
from models.db import db


def find_all_by_user_id(user_id):
    return Booking.query.filter_by(userId=user_id).all()


def compute_total_booking_value_of_offerer(offerer_id):
    return db.session.query(func.sum(Booking.amount * Booking.quantity)) \
        .join(Stock) \
        .join(EventOccurrence) \
        .join(Offer) \
        .join(Venue) \
        .join(Offerer) \
        .filter_by(id=offerer_id)\
        .first()
