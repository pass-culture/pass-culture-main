from sqlalchemy.exc import InternalError
from sqlalchemy.orm import aliased

from models import Booking, Stock, EventOccurrence, Offer, Venue, User, PcObject, ApiErrors


class BookingNotFound(ApiErrors):
    pass


def find_all_by_user_id(user_id):
    return Booking.query.filter_by(userId=user_id).all()


def find_all_by_stock_id(stock):
    return Booking.query.filter_by(stockId=stock.id).all()


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


def find_all_with_soft_deleted_stocks():
    return Booking.query.join(Stock).filter_by(isSoftDeleted=True).all()


def find_by_token(token, email=None, offer_id=None):
    query = Booking.query.filter_by(token=token)
    if email:
        query = query.join(User).filter_by(email=email)
    if offer_id:
        query_offer_1 = Booking.query.join(Stock).join(Offer).filter_by(id=offer_id)
        query_offer_2 = Booking.query.join(Stock).join(EventOccurrence).join(aliased(Offer)).filter_by(id=offer_id)
        query_offer = query_offer_1.union_all(query_offer_2)
        query = query.intersect_all(query_offer)

    booking = query.first()

    if booking is None:
        errors = BookingNotFound()
        errors.addError(
            'global',
            "Ce coupon n'a pas été trouvé"
        )
        raise errors

    return booking


def save_booking(booking):
    try:
        PcObject.check_and_save(booking)
    except InternalError as internal_error:
        api_errors = ApiErrors()

        if 'tooManyBookings' in str(internal_error.orig):
            api_errors.addError('global', 'la quantité disponible pour cette offre est atteinte')
        elif 'insufficientFunds' in str(internal_error.orig):
            api_errors.addError('insufficientFunds', 'l\'utilisateur ne dispose pas de fonds suffisants pour '
                                                     'effectuer une réservation.')
        raise api_errors


def find_by_id(booking_id):
    return Booking.query.filter_by(id=booking_id).first_or_404()
