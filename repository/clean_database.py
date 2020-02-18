from local_providers.install import install_local_providers
from models import ApiKey, \
    BeneficiaryImport, \
    Booking, \
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
    Provider, \
    VenueProvider, \
    PaymentMessage, \
    BankInformation, \
    LocalProviderEvent, \
    Favorite, \
    BeneficiaryImportStatus, \
    OfferCriterion, \
    Criterion, VenueProviderPriceRule, AllocinePivot, AllocineVenueProvider
from models.activity import load_activity
from models.db import db
from models.email import Email
from models.install import install_features


def clean_all_database(*args, **kwargs):
    """ Order of deletions matters because of foreign key constraints """
    Activity = load_activity()
    LocalProviderEvent.query.delete()
    VenueProviderPriceRule.query.delete()
    AllocineVenueProvider.query.delete()
    VenueProvider.query.delete()
    PaymentStatus.query.delete()
    Payment.query.delete()
    PaymentMessage.query.delete()
    Booking.query.delete()
    Stock.query.delete()
    Favorite.query.delete()
    Recommendation.query.delete()
    Mediation.query.delete()
    OfferCriterion.query.delete()
    Criterion.query.delete()
    Offer.query.delete()
    Product.query.delete()
    BankInformation.query.delete()
    Venue.query.delete()
    UserOfferer.query.delete()
    ApiKey.query.delete()
    Offerer.query.delete()
    Deposit.query.delete()
    BeneficiaryImportStatus.query.delete()
    BeneficiaryImport.query.delete()
    User.query.delete()
    Activity.query.delete()
    UserSession.query.delete()
    Email.query.delete()
    LocalProviderEvent.query.delete()
    Provider.query.delete()
    AllocinePivot.query.delete()
    db.session.commit()
    install_features()
    install_local_providers()
