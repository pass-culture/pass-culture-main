from pcapi.core.bookings.models import Booking
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import BeneficiaryFraudResult
from pcapi.core.mails.models import Email
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueLabel
from pcapi.core.offerers.models import VenueType
from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.payments.models import CustomReimbursementRule
from pcapi.core.payments.models import Deposit
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.subscription.models import SubscriptionMessage
from pcapi.core.users.models import Favorite
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.models.allocine_pivot import AllocinePivot
from pcapi.models.api_errors import ApiErrors
from pcapi.models.bank_information import BankInformation
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.criterion import Criterion
from pcapi.models.db import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.extra_data_mixin import ExtraDataMixin
from pcapi.models.feature import Feature
from pcapi.models.has_address_mixin import HasAddressMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.local_provider_event import LocalProviderEvent
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.models.payment import Payment
from pcapi.models.payment_message import PaymentMessage
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.pc_object import PcObject
from pcapi.models.product import BookFormat
from pcapi.models.product import Product
from pcapi.models.providable_mixin import ProvidableMixin
from pcapi.models.user_offerer import UserOfferer
from pcapi.models.user_session import UserSession


__all__ = (
    "ActivationCode",
    "ApiErrors",
    "ApiKey",
    "AllocinePivot",
    "BankInformation",
    "BeneficiaryFraudCheck",
    "BeneficiaryFraudResult",
    "BeneficiaryImport",
    "BeneficiaryImportStatus",
    "Criterion",
    "CustomReimbursementRule",
    "PcObject",
    "DeactivableMixin",
    "Deposit",
    "Email",
    "ExtraDataMixin",
    "Favorite",
    "Feature",
    "HasAddressMixin",
    "HasThumbMixin",
    "BookFormat",
    "NeedsValidationMixin",
    "ProvidableMixin",
    "Booking",
    "Mediation",
    "Stock",
    "Offerer",
    "LocalProviderEvent",
    "OfferCriterion",
    "Offer",
    "Payment",
    "PaymentStatus",
    "PaymentMessage",
    "Product",
    "SubscriptionMessage",
    "Token",
    "UserOfferer",
    "User",
    "UserSession",
    "Venue",
    "VenueType",
    "VenueLabel",
)

# Order matters
models = (
    User,
    UserSession,
    Provider,
    Offerer,
    UserOfferer,
    VenueLabel,
    VenueType,
    Venue,
    ApiKey,
    AllocinePivot,
    BankInformation,
    BeneficiaryFraudCheck,
    BeneficiaryFraudResult,
    BeneficiaryImport,
    BeneficiaryImportStatus,
    Criterion,
    Deposit,
    Email,
    Product,
    Offer,
    Mediation,
    Favorite,
    Feature,
    Stock,
    Booking,
    VenueProvider,
    AllocineVenueProvider,
    AllocineVenueProviderPriceRule,
    LocalProviderEvent,
    OfferCriterion,
    PaymentMessage,
    CustomReimbursementRule,
    Payment,
    PaymentStatus,
    Token,
    SubscriptionMessage,
)
