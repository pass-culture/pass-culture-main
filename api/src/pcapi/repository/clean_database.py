from pcapi import settings
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.educational.models import EducationalYear
from pcapi.core.finance.models import BusinessUnit
from pcapi.core.finance.models import Cashflow
from pcapi.core.finance.models import CashflowBatch
from pcapi.core.finance.models import CashflowLog
from pcapi.core.finance.models import CashflowPricing
from pcapi.core.finance.models import Invoice
from pcapi.core.finance.models import InvoiceCashflow
from pcapi.core.finance.models import InvoiceLine
from pcapi.core.finance.models import Pricing
from pcapi.core.finance.models import PricingLine
from pcapi.core.finance.models import PricingLog
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import BeneficiaryFraudResult
from pcapi.core.fraud.models import BeneficiaryFraudReview
from pcapi.core.mails.models.models import Email
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueLabel
from pcapi.core.offerers.models import VenueType
from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.core.offers.models import Stock
from pcapi.core.payments.models import CustomReimbursementRule
from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import Recredit
from pcapi.core.providers.models import AllocinePivot
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.models import Favorite
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.core.users.models import UserSuspension
from pcapi.local_providers.install import install_local_providers
from pcapi.models import db
from pcapi.models.bank_information import BankInformation
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.criterion import Criterion
from pcapi.models.feature import Feature
from pcapi.models.feature import install_feature_flags
from pcapi.models.local_provider_event import LocalProviderEvent
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.models.payment import Payment
from pcapi.models.payment_message import PaymentMessage
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.product import Product
from pcapi.models.user_offerer import UserOfferer
from pcapi.models.user_session import UserSession


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
    CashflowPricing.query.delete()
    CashflowLog.query.delete()
    InvoiceCashflow.query.delete()
    Cashflow.query.delete()
    CashflowBatch.query.delete()
    PricingLine.query.delete()
    PricingLog.query.delete()
    Pricing.query.delete()
    InvoiceLine.query.delete()
    Invoice.query.delete()
    CustomReimbursementRule.query.delete()
    Booking.query.delete()
    IndividualBooking.query.delete()
    Stock.query.delete()
    Favorite.query.delete()
    Mediation.query.delete()
    OfferCriterion.query.delete()
    Criterion.query.delete()
    Offer.query.delete()
    Product.query.delete()
    # Handle relationship loop: Venue->BusinessUnit->BankInformation->Venue.
    Venue.query.update({"businessUnitId": None}, synchronize_session=False)
    BusinessUnit.query.delete()
    BankInformation.query.delete()
    Venue.query.delete()
    UserOfferer.query.delete()
    ApiKey.query.delete()
    Offerer.query.delete()
    Recredit.query.delete()
    Deposit.query.delete()
    BeneficiaryImportStatus.query.delete()
    BeneficiaryImport.query.delete()
    BeneficiaryFraudCheck.query.delete()
    BeneficiaryFraudResult.query.delete()
    BeneficiaryFraudReview.query.delete()
    Token.query.delete()
    OfferValidationConfig.query.delete()
    UserSuspension.query.delete()
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
    Feature.query.delete()

    # Dans le cadre du projet EAC, notre partenaire Adage requête notre api sur le endpoint get_pre_bookings.
    # Ils récupèrent les pré-réservations EAC liées à un utilisateur EAC et stockent les ids en base.
    # Dans la phase de développement, ils se connectent sur notre environnement testing et récupèrent des données issues donc de nos sandbox.
    # Nous avons besoin que les ids soient fixes. Pour ce faire, il faut que la séquence d'ids sur les EducationalBookings recommence à 1 à chaque
    # nouvelle génération de la sandbox sur testing. C'est la raison de la commande ci-dessous.
    # A noter qu'en local la question ne se pose pas car l'instance de base de données est détruite puis reconstruite. L'id recommence donc nécessairement à 1
    db.session.execute("SELECT setval('educational_booking_id_seq', 1, FALSE)")

    db.session.commit()
    install_feature_flags()
    install_local_providers()
