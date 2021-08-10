from pcapi import settings
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.educational.models import EducationalYear
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import BeneficiaryFraudResult
from pcapi.core.fraud.models import BeneficiaryFraudReview
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
from pcapi.models import LocalProviderEvent
from pcapi.models import Offer
from pcapi.models import OfferCriterion
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
    IndividualBooking.query.delete()
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
    Venue.query.delete()
    UserOfferer.query.delete()
    ApiKey.query.delete()
    Offerer.query.delete()
    Deposit.query.delete()
    BeneficiaryImportStatus.query.delete()
    BeneficiaryImport.query.delete()
    BeneficiaryFraudCheck.query.delete()
    BeneficiaryFraudResult.query.delete()
    BeneficiaryFraudReview.query.delete()
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
    EducationalBooking.query.delete()
    EducationalDeposit.query.delete()
    EducationalInstitution.query.delete()
    EducationalYear.query.delete()
    EducationalRedactor.query.delete()

    # Dans le cadre du projet EAC, notre partenaire Adage requête notre api sur le endpoint get_pre_bookings.
    # Ils récupèrent les pré-réservations EAC liées à un utilisateur EAC et stockent les ids en base.
    # Dans la phase de développement, ils se connectent sur notre environnement testing et récupèrent des données issues donc de nos sandbox.
    # Nous avons besoin que les ids soient fixes. Pour ce faire, il faut que la séquence d'ids sur les EducationalBookings recommence à 1 à chaque
    # nouvelle génération de la sandbox sur testing. C'est la raison de la commande ci-dessous.
    # A noter qu'en local la question ne se pose pas car l'instance de base de données est détruite puis reconstruite. L'id recommence donc nécessairement à 1
    db.session.execute("SELECT setval('educational_booking_id_seq', 1, FALSE)")

    db.session.commit()
    install_features()
    install_local_providers()
