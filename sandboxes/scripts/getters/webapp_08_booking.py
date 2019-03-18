from models.user import User
from datetime import datetime
from models import Offer, EventOccurrence, Stock
from repository.user_queries import filter_webapp_users
from sandboxes.scripts.utils.helpers import get_user_helper, get_offer_helper

def get_non_free_offer_with_multi_dates_not_already_booked():
  query = Offer.query.filter(EventOccurrence.query.filter((Offer.id == EventOccurrence.offerId) & (EventOccurrence.beginningDatetime > datetime.utcnow())).count() > 1)
  query = query.filter(Stock.price >= 0)
  offer = query.first()
  return {
      "offer": get_offer_helper(offer)
  }

def get_existing_webapp_user_has_no_more_money():
  query = filter_webapp_users(User.query)
  query = query.filter(User.email.contains('has-no-more-money'))
  user = query.first()
  return {
      "user": get_user_helper(user)
  }

def get_existing_webapp_user_can_book_thing_offer():
    query = filter_webapp_users(User.query)
    query = query.filter(User.email.contains('93.has-booked-some'))
    user = query.first()
    return {
        "user": get_user_helper(user)
    }

def get_existing_webapp_user_can_book_digital_offer():
    query = filter_webapp_users(User.query)
    query = query.filter(User.email.contains('93.has-booked-some'))
    user = query.first()
    return {
        "user": get_user_helper(user)
    }

def get_existing_webapp_user_can_book_event_offer():
    query = filter_webapp_users(User.query)
    query = query.filter(User.email.contains('93.has-booked-some'))
    user = query.first()
    return {
        "user": get_user_helper(user)
    }

def get_existing_webapp_user_can_book_multidates():
    query = filter_webapp_users(User.query)
    query = query.filter(User.email.contains('97.has-confirmed-activation'))
    user = query.first()
    return {
        "user": get_user_helper(user)
    }

def get_existing_webapp_user_reach_digital_limit():
    query = filter_webapp_users(User.query)
    query = query.filter(User.email.contains('93.has-booked-some'))
    user = query.first()
    return {
        "user": get_user_helper(user)
    }

def get_existing_webapp_user_reach_physical_limit():
  query = filter_webapp_users(User.query)
  query = query.filter(User.email.contains('93.has-booked-some'))
  user = query.first()
  return {
      "user": get_user_helper(user)
  }
