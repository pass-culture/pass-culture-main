from sqlalchemy import func

from models import Offerer, Venue, Offer, EventOccurrence, UserOfferer, User, Event, Booking, Stock
from models import RightsType
from models.activity import load_activity
from models.db import db


def get_by_offer_id(offer_id):
    return Offerer.query.join(Venue).join(Offer).filter_by(id=offer_id).first()


def get_by_event_occurrence_id(event_occurrence_id):
    return Offerer.query.join(Venue).join(Offer).join(EventOccurrence).filter_by(id=event_occurrence_id).first()


def find_all_admin_offerer_emails(offerer_id):
    return [result.email for result in Offerer.query.filter_by(id=offerer_id).join(UserOfferer).filter_by(rights=RightsType.admin).filter_by(validationToken=None).join(
        User).with_entities(User.email)]


def find_offerers_in_date_range_for_given_departement(date_max, date_min, department):
    Activity = load_activity()
    query = db.session.query(func.distinct(Offerer.id), Offerer.name, Activity.issued_at, Venue.departementCode) \
        .join(Venue) \
        .join(Activity, Activity.table_name == 'offerer') \
        .filter(Activity.verb == 'insert', Activity.data['id'].astext.cast(db.Integer) == Offerer.id)
    if department:
        query = query.filter(Venue.departementCode == department)
    if date_min:
        query = query.filter(Activity.issued_at >= date_min)
    if date_max:
        query = query.filter(Activity.issued_at <= date_max)
    result = query.order_by(Activity.issued_at) \
        .all()
    return result


def find_offerers_with_user_venues_and_bookings_by_departement(department):
    Activity = load_activity()
    query = db.session.query(Offerer.name, UserOfferer.id, User.email, User.dateCreated, Venue.departementCode,
                             Offer.dateCreated, Event.name, Activity.issued_at, Booking.dateModified) \
        .join(Venue) \
        .outerjoin(Offer) \
        .outerjoin(EventOccurrence) \
        .join(Stock) \
        .outerjoin(Booking) \
        .join(Event) \
        .outerjoin(UserOfferer) \
        .outerjoin(User) \
        .join(Activity, Activity.table_name == 'event') \
        .filter(Activity.verb == 'insert', Activity.data['id'].astext.cast(db.Integer) == Event.id)
    if department:
        query = query.filter(Venue.departementCode == department)
    result = query.order_by(Offerer.id).all()
    return result