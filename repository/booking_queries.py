from models import Booking, Stock, EventOccurrence, Offer, Venue, Offerer


def find_all_by_user_id(user_id):
    return Booking.query.filter_by(userId=user_id).all()


def find_all_by_offerer_sorted_by_date_modified_asc(offerer_id):
    query_event = Booking.query \
        .join(Stock) \
        .join(EventOccurrence) \
        .join(Offer) \
        .join(Venue) \
        .filter(Venue.managingOffererId == offerer_id) \
        .all()

    query_thing = Booking.query \
        .join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .filter(Venue.managingOffererId == offerer_id) \
        .all()

    return sorted(query_event + query_thing, key=lambda b: b.dateModified)


def find_bookings_from_recommendation(reco, user):
    booking_query = Booking.query.join(Stock)
    if reco.offer.eventId:
        booking_query = booking_query.join(EventOccurrence)
    booking_query = booking_query.join(Offer) \
        .filter(Booking.user == user) \
        .filter(Offer.id == reco.offerId)
    return booking_query.all()