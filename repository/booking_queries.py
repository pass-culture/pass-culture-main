from models import Booking, Stock, EventOccurrence, Offer, Venue, Offerer


def find_all_by_user_id(user_id):
    return Booking.query.filter_by(userId=user_id).all()


def find_all_by_offerer_sorted_by_date_modified_asc(offerer_id):
    query_event = Booking.query \
        .join(Booking.stock) \
        .join(Stock.eventOccurrence) \
        .join(EventOccurrence.offer) \
        .join(Offer.venue) \
        .join(Venue.managingOfferer) \
        .filter(Offerer.id == offerer_id) \
        .all()

    query_thing = Booking.query \
        .join(Booking.stock) \
        .join(Stock.offer) \
        .join(Offer.venue) \
        .join(Venue.managingOfferer) \
        .filter(Offerer.id == offerer_id) \
        .all()

    return sorted(query_event + query_thing, key=lambda b: b.dateModified)
