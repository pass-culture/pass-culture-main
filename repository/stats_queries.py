from postgresql_audit.flask import versioning_manager
from sqlalchemy import func, distinct

from models import Venue, Booking, User, Stock, EventOccurrence
from models.db import db


try:
    Activity = versioning_manager.activity_cls
except AttributeError:
    pass

def find_bookings_stats_per_department(time_intervall):
    result = db.session.query(Venue.departementCode, func.date_trunc(time_intervall, Activity.issued_at), func.count(Booking.id), func.count(User.id),
                              func.count(distinct(User.id))) \
        .join(Booking) \
        .join(Stock) \
        .join(EventOccurrence) \
        .join(Activity, Activity.table_name == 'booking') \
        .filter(Activity.verb == 'insert', Activity.data['id'].astext.cast(db.Integer) == Booking.id) \
        .filter(User.canBookFreeOffers == 'true') \
        .group_by(func.date_trunc(time_intervall, Activity.issued_at), Venue.departementCode) \
        .order_by(func.date_trunc(time_intervall, Activity.issued_at), Venue.departementCode) \
        .all()
    return result
