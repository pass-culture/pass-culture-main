from models.allocine_pivot import AllocinePivot
from models.api_errors import ApiErrors
from models.api_key import ApiKey
from models.bank_information import BankInformation
from models.beneficiary_import import BeneficiaryImport
from models.beneficiary_import_status import BeneficiaryImportStatus, \
    ImportStatus
from models.booking_sql_entity import BookingSQLEntity
from models.criterion import Criterion
from models.deactivable_mixin import DeactivableMixin
from models.deposit import Deposit
from models.discovery_view import DiscoveryView
from models.discovery_view_v3 import DiscoveryViewV3
from models.email import Email
from models.extra_data_mixin import ExtraDataMixin
from models.favorite import Favorite
from models.feature import Feature
from models.has_address_mixin import HasAddressMixin
from models.has_thumb_mixin import HasThumbMixin
from models.iris_venues import IrisVenues
from models.local_provider_event import LocalProviderEvent
from models.mediation import Mediation
from models.needs_validation_mixin import NeedsValidationMixin
from models.offer import Offer
from models.offer_criterion import OfferCriterion
from models.offer_type import EventType, ThingType
from models.offerer import Offerer
from models.payment import Payment
from models.payment_message import PaymentMessage
from models.payment_status import PaymentStatus
from models.pc_object import PcObject
from models.product import BookFormat, Product
from models.providable_mixin import ProvidableMixin
from models.provider import Provider
from models.recommendation import Recommendation
from models.seen_offers import SeenOffer
from models.stock_sql_entity import StockSQLEntity
from models.user_sql_entity import UserSQLEntity
from models.user_offerer import RightsType, UserOfferer
from models.user_session import UserSession
from models.venue import Venue
from models.venue_label_sql_entity import VenueLabelSQLEntity
from models.venue_provider import VenueProvider
from models.venue_type import VenueType
from models.versioned_mixin import VersionedMixin
from models.allocine_venue_provider import AllocineVenueProvider
from models.allocine_venue_provider_price_rule import \
    AllocineVenueProviderPriceRule
from models.iris_france import IrisFrance

__all__ = (
    'VersionedMixin',
    'ApiErrors',
    'ApiKey',
    'AllocinePivot',
    'AllocineVenueProvider',
    'BankInformation',
    'BeneficiaryImport',
    'BeneficiaryImportStatus',
    'Criterion',
    'PcObject',
    'DeactivableMixin',
    'Deposit',
    'Email',
    'EventType',
    'ExtraDataMixin',
    'Favorite',
    'Feature',
    'HasAddressMixin',
    'HasThumbMixin',
    'IrisFrance',
    'IrisVenues',
    'BookFormat',
    'NeedsValidationMixin',
    'ProvidableMixin',
    'BookingSQLEntity',
    'Mediation',
    'StockSQLEntity',
    'Offerer',
    'VenueProvider',
    'AllocineVenueProviderPriceRule',
    'LocalProviderEvent',
    'OfferCriterion',
    'Offer',
    'Payment',
    'PaymentStatus',
    'PaymentMessage',
    'Provider',
    'Product',
    'Recommendation',
    'DiscoveryView',
    'DiscoveryViewV3',
    'RightsType',
    'ThingType',
    'UserOfferer',
    'UserSQLEntity',
    'UserSession',
    'Venue',
    'VenueType',
    'VenueLabelSQLEntity',
    'SeenOffer'
)

# Order matters
models = (
    UserSQLEntity,
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
    Recommendation,
    Favorite,
    Feature,
    StockSQLEntity,
    BookingSQLEntity,
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
    SeenOffer
)

materialized_views = (
    DiscoveryView,
    DiscoveryViewV3,
)
