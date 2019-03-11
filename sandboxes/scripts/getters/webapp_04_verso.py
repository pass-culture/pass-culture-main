from models import Booking, Event, EventOccurrence, Offer, Stock, Thing, User
from repository.user_queries import filter_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper, get_offer_helper

from pprint import pprint

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

def get_booking_for_user(user):
    query = Booking.query.filter_by(userId=user.id)
    bookings = query.all()
    return bookings

def get_event_already_booked_and_user_hnmm_93():
  join_on_event = (Stock.eventOccurrenceId == EventOccurrence.id)
  join_on_event_occurrence = (Offer.id == EventOccurrence.offerId)
  offers = Offer.query.outerjoin(Event) \
      .outerjoin(EventOccurrence, join_on_event_occurrence) \
      .join(Stock, join_on_event) \
      .add_columns(Stock.id) \
      .all()
  user = get_existing_webapp_hnmm_user()
  bookings = get_booking_for_user(user)
  offer = filter_booking_by_offer_id(bookings, offers)
  return {
      "offer": get_offer_helper(offer),
      "user": get_user_helper(user)
  }

def get_digital_offer_already_booked_and_user_hnmm_93():
  offers = Offer.query.outerjoin(Thing) \
      .filter(Thing.url != None) \
      .join(Stock, (Offer.id == Stock.offerId)) \
      .add_columns(Stock.id) \
      .all()
  user = get_existing_webapp_hnmm_user()
  bookings = get_booking_for_user(user)
  offer = filter_booking_by_offer_id(bookings, offers)
  return {
      "offer": get_offer_helper(offer),
      "user": get_user_helper(user)
  }
