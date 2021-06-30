from pcapi import settings
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalYear
from pcapi.core.mails.models import Email
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import VenueLabel
from pcapi.core.offerers.models import VenueType
from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.local_providers.install import install_local_providers
from pcapi.models import AllocinePivot
from pcapi.models import BankInformation
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportStatus
from pcapi.models import Booking
from pcapi.models import Criterion
from pcapi.models import Deposit
from pcapi.models import Favorite
from pcapi.models import IrisFrance
from pcapi.models import IrisVenues
from pcapi.models import LocalProviderEvent
from pcapi.models import Offer
from pcapi.models import OfferCategory
from pcapi.models import OfferCriterion
from pcapi.models import OfferSubcategory
from pcapi.models import Payment
from pcapi.models import PaymentMessage
from pcapi.models import PaymentStatus
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.models import UserOfferer
from pcapi.models import UserSession
from pcapi.models import Venue
from pcapi.models.db import db
from pcapi.models.install import install_features


def clean_all_database(*args, **kwargs):
    """Order of deletions matters because of foreign key constraints"""
    if settings.ENV not in ("development", "testing"):
        raise ValueError(f"You cannot do this on this environment: '{settings.ENV}'")
    LocalProviderEvent.query.delete()
    ActivationCode.query.delete()
    AllocineVenueProviderPriceRule.query.delete()
    AllocineVenueProvider.query.delete()
    VenueProvider.query.delete()
    PaymentStatus.query.delete()
    Payment.query.delete()
    PaymentMessage.query.delete()
    Booking.query.delete()
    Stock.query.delete()
    Favorite.query.delete()
    Mediation.query.delete()
    OfferCriterion.query.delete()
    Criterion.query.delete()
    Offer.query.delete()
    Product.query.delete()
    BankInformation.query.delete()
    IrisVenues.query.delete()
    IrisFrance.query.delete()
    Venue.query.delete()
    UserOfferer.query.delete()
    ApiKey.query.delete()
    Offerer.query.delete()
    Deposit.query.delete()
    BeneficiaryImportStatus.query.delete()
    BeneficiaryImport.query.delete()
    Token.query.delete()
    OfferValidationConfig.query.delete()
    User.query.delete()
    UserSession.query.delete()
    Email.query.delete()
    LocalProviderEvent.query.delete()
    Provider.query.delete()
    AllocinePivot.query.delete()
    VenueType.query.delete()
    VenueLabel.query.delete()
    OfferSubcategory.query.delete()
    OfferCategory.query.delete()
    EducationalBooking.query.delete()
    EducationalDeposit.query.delete()
    EducationalInstitution.query.delete()
    EducationalYear.query.delete()
    db.session.commit()
    install_features()
    install_local_providers()
