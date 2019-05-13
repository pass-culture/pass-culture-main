from models.activity import load_activity
from models.db import db
from models import Booking, \
    Deposit, \
    Mediation, \
    Payment, \
    PaymentStatus, \
    Product, \
    Offer, \
    Offerer, \
    Recommendation, \
    Stock, \
    User, \
    UserOfferer, \
    UserSession, \
    Venue, \
    VenueProvider, PaymentMessage, BankInformation, LocalProviderEvent
from models.email import Email


def clean_all_database(*args, **kwargs):
    """ Order of deletions matters because of foreign key constraints """
    Activity = load_activity()
    LocalProviderEvent.query.delete()
    VenueProvider.query.delete()
    PaymentStatus.query.delete()
    Payment.query.delete()
    PaymentMessage.query.delete()
    Booking.query.delete()
    Stock.query.delete()
    Recommendation.query.delete()
    Mediation.query.delete()
    Offer.query.delete()
    Product.query.delete()
    BankInformation.query.delete()
    Venue.query.delete()
    UserOfferer.query.delete()
    Offerer.query.delete()
    Deposit.query.delete()
    User.query.delete()
    Activity.query.delete()
    UserSession.query.delete()
    Email.query.delete()
    db.session.commit()
