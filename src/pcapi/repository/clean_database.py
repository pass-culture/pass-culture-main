from pcapi.local_providers.install import install_local_providers
from pcapi.models import ApiKey, \
    BeneficiaryImport, \
    BookingSQLEntity, \
    Deposit, \
    MediationSQLEntity, \
    Payment, \
    PaymentStatus, \
    Product, \
    OfferSQLEntity, \
    Offerer, \
    Recommendation, \
    StockSQLEntity, \
    UserSQLEntity, \
    UserOfferer, \
    UserSession, \
    VenueSQLEntity, \
    Provider, \
    PaymentMessage, \
    BankInformation, \
    LocalProviderEvent, \
    FavoriteSQLEntity, \
    BeneficiaryImportStatus, \
    OfferCriterion, \
    Criterion, \
    AllocineVenueProviderPriceRule, \
    AllocinePivot, VenueProvider, \
    IrisFrance, IrisVenues, \
    SeenOffer, VenueType

from pcapi.models.activity import load_activity
from pcapi.models.allocine_venue_provider import AllocineVenueProvider
from pcapi.models.db import db
from pcapi.models.email import Email
from pcapi.models.install import install_features, install_materialized_views
from pcapi.models.venue_label_sql_entity import VenueLabelSQLEntity


def clean_all_database(*args, **kwargs):
    """ Order of deletions matters because of foreign key constraints """
    Activity = load_activity()
    LocalProviderEvent.query.delete()
    AllocineVenueProviderPriceRule.query.delete()
    AllocineVenueProvider.query.delete()
    VenueProvider.query.delete()
    PaymentStatus.query.delete()
    Payment.query.delete()
    PaymentMessage.query.delete()
    BookingSQLEntity.query.delete()
    StockSQLEntity.query.delete()
    FavoriteSQLEntity.query.delete()
    Recommendation.query.delete()
    MediationSQLEntity.query.delete()
    OfferCriterion.query.delete()
    Criterion.query.delete()
    SeenOffer.query.delete()
    OfferSQLEntity.query.delete()
    Product.query.delete()
    BankInformation.query.delete()
    IrisVenues.query.delete()
    IrisFrance.query.delete()
    VenueSQLEntity.query.delete()
    UserOfferer.query.delete()
    ApiKey.query.delete()
    Offerer.query.delete()
    Deposit.query.delete()
    BeneficiaryImportStatus.query.delete()
    BeneficiaryImport.query.delete()
    UserSQLEntity.query.delete()
    Activity.query.delete()
    UserSession.query.delete()
    Email.query.delete()
    LocalProviderEvent.query.delete()
    Provider.query.delete()
    AllocinePivot.query.delete()
    VenueType.query.delete()
    VenueLabelSQLEntity.query.delete()
    db.session.commit()
    install_materialized_views()
    install_features()
    install_local_providers()
