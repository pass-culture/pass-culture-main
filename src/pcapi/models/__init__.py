from pcapi.core.bookings.models import Booking
from pcapi.core.mails.models import Email
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.models import Favorite
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.models.allocine_pivot import AllocinePivot
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_key import ApiKey
from pcapi.models.bank_information import BankInformation
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.criterion import Criterion
from pcapi.models.db import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.deposit import Deposit
from pcapi.models.extra_data_mixin import ExtraDataMixin
from pcapi.models.feature import Feature
from pcapi.models.has_address_mixin import HasAddressMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.iris_venues import IrisVenues
from pcapi.models.local_provider_event import LocalProviderEvent
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ThingType
from pcapi.models.payment import Payment
from pcapi.models.payment_message import PaymentMessage
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.pc_object import PcObject
from pcapi.models.product import BookFormat
from pcapi.models.product import Product
from pcapi.models.providable_mixin import ProvidableMixin
from pcapi.models.user_offerer import UserOfferer
from pcapi.models.user_session import UserSession
from pcapi.models.venue_label_sql_entity import VenueLabelSQLEntity
from pcapi.models.venue_type import VenueType
from pcapi.models.versioned_mixin import VersionedMixin


# TODO: fix circular import
from pcapi.models.iris_france import IrisFrance  # isort:skip

__all__ = (
    "VersionedMixin",
    "ApiErrors",
    "ApiKey",
    "AllocinePivot",
    "BankInformation",
    "BeneficiaryImport",
    "BeneficiaryImportStatus",
    "Criterion",
    "PcObject",
    "DeactivableMixin",
    "Deposit",
    "Email",
    "EventType",
    "ExtraDataMixin",
    "Favorite",
    "Feature",
    "HasAddressMixin",
    "HasThumbMixin",
    "IrisFrance",
    "IrisVenues",
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
    "ThingType",
    "Token",
    "UserOfferer",
    "User",
    "UserSession",
    "Venue",
    "VenueType",
    "VenueLabelSQLEntity",
)

# Order matters
models = (
    User,
    UserSession,
    Provider,
    Offerer,
    UserOfferer,
    VenueLabelSQLEntity,
    VenueType,
    Venue,
    ApiKey,
    AllocinePivot,
    BankInformation,
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
    Payment,
    PaymentStatus,
    IrisFrance,
    IrisVenues,
    Token,
)
