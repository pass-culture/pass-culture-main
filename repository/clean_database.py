from models.activity import load_activity
from models.db import db
from models import Booking, \
    Deposit, \
    Event, \
    EventOccurrence, \
    Mediation, \
    Payment, \
    PaymentStatus, \
    Offer, \
    Offerer, \
    Recommendation, \
    Stock, \
    Thing, \
    User, \
    UserOfferer, \
    UserSession, \
    Venue, \
    VenueProvider, PaymentTransaction, BankInformation


def clean_all_database(*args, **kwargs):
    """ Order of deletions matters because of foreign key constraints """
    Activity = load_activity()
    VenueProvider.query.delete()
    PaymentStatus.query.delete()
    Payment.query.delete()
    PaymentTransaction.query.delete()
    Booking.query.delete()
    Stock.query.delete()
    EventOccurrence.query.delete()
    Recommendation.query.delete()
    Mediation.query.delete()
    Offer.query.delete()
    Thing.query.delete()
    Event.query.delete()
    BankInformation.query.delete()
    Venue.query.delete()
    UserOfferer.query.delete()
    Offerer.query.delete()
    Deposit.query.delete()
    User.query.delete()
    Activity.query.delete()
    UserSession.query.delete()
    db.session.commit()
