from models import Booking, Event, Mediation, Offer, Stock, Thing, User
from repository.user_queries import filter_webapp_users
from sandboxes.scripts.utils.helpers import get_mediation_helper, get_offer_helper, get_user_helper


def get_existing_webapp_hnmm_user(return_as_dict=False):
    query = filter_webapp_users(User.query)
    query = query.filter(User.email.contains('93.has-no-more-money'))
    user = query.first()
    if return_as_dict == False:
        return user
    return {
        "user": get_user_helper(user)
    }


def get_existing_webapp_hbs_user():
    query = filter_webapp_users(User.query)
    query = query.filter(User.email.contains('has-booked-some'))
    user = query.first()
    return {
        "user": get_user_helper(user)
    }


def filter_booking_by_offer_id(bookings, offers):
    selected = None
    for offer in offers:
        for booking in bookings:
            if booking.stockId == offer.id:
                selected = offer.Offer
                break
    return selected

def get_cancellable_bookings_for_user(user):
    query = Booking.query.filter_by(
        userId=user.id
    )
    bookings = [b for b in query.all() if b.isUserCancellable]
    return bookings

def get_not_cancellable_bookings_for_user(user):
    query = Booking.query.filter_by(
        userId=user.id
    )
    bookings = [b for b in query.all() if not b.isUserCancellable]
    return bookings


def get_event_offer_with_active_mediation_already_booked_but_cancellable_and_user_hnmm_93():
    offers = Offer.query \
        .filter(Offer.mediations.any(Mediation.isActive == True)) \
        .join(Stock) \
        .filter(Stock.beginningDatetime != None) \
        .add_columns(Stock.id) \
        .all()
    user = get_existing_webapp_hnmm_user()
    bookings = get_cancellable_bookings_for_user(user)
    offer = filter_booking_by_offer_id(bookings, offers)

    for mediation in offer.mediations:
        if mediation.isActive:
            return {
                "mediation": get_mediation_helper(mediation),
                "offer": get_offer_helper(offer),
                "user": get_user_helper(user)
            }


def get_digital_offer_with_active_mediation_already_booked_and_user_hnmm_93():
    offers = Offer.query.outerjoin(Thing) \
        .filter(Offer.mediations.any(Mediation.isActive == True)) \
        .filter(Thing.url != None) \
        .join(Stock, (Offer.id == Stock.offerId)) \
        .add_columns(Stock.id) \
        .all()
    user = get_existing_webapp_hnmm_user()
    bookings = get_not_cancellable_bookings_for_user(user)
    offer = filter_booking_by_offer_id(bookings, offers)

    for mediation in offer.mediations:
        if mediation.isActive:
            return {
                "mediation": get_mediation_helper(mediation),
                "offer": get_offer_helper(offer),
                "user": get_user_helper(user)
            }
