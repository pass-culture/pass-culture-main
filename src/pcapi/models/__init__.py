from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.models.allocine_pivot import AllocinePivot
from pcapi.models.allocine_venue_provider import AllocineVenueProvider
from pcapi.models.allocine_venue_provider_price_rule import AllocineVenueProviderPriceRule
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
from pcapi.models.discovery_view import DiscoveryView
from pcapi.models.discovery_view_v3 import DiscoveryViewV3
from pcapi.models.email import Email
from pcapi.models.extra_data_mixin import ExtraDataMixin
from pcapi.models.favorite_sql_entity import FavoriteSQLEntity
from pcapi.models.feature import Feature
from pcapi.models.has_address_mixin import HasAddressMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.iris_venues import IrisVenues
from pcapi.models.local_provider_event import LocalProviderEvent
from pcapi.models.mediation_sql_entity import MediationSQLEntity
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ThingType
from pcapi.models.offerer import Offerer
from pcapi.models.payment import Payment
from pcapi.models.payment_message import PaymentMessage
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.pc_object import PcObject
from pcapi.models.product import BookFormat
from pcapi.models.product import Product
from pcapi.models.providable_mixin import ProvidableMixin
from pcapi.models.provider import Provider
from pcapi.models.recommendation import Recommendation
from pcapi.models.seen_offers import SeenOffer
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.user_offerer import RightsType
from pcapi.models.user_offerer import UserOfferer
from pcapi.models.user_session import UserSession
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.models.venue_label_sql_entity import VenueLabelSQLEntity
from pcapi.models.venue_provider import VenueProvider
from pcapi.models.venue_sql_entity import VenueSQLEntity
from pcapi.models.venue_type import VenueType
from pcapi.models.versioned_mixin import VersionedMixin


# TODO: fix circular import
from pcapi.models.iris_france import IrisFrance #isort:skip

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
    'FavoriteSQLEntity',
    'Feature',
    'HasAddressMixin',
    'HasThumbMixin',
    'IrisFrance',
    'IrisVenues',
    'BookFormat',
    'NeedsValidationMixin',
    'ProvidableMixin',
    'Booking',
    'MediationSQLEntity',
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
    'VenueSQLEntity',
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
    VenueSQLEntity,
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
    MediationSQLEntity,
    Recommendation,
    FavoriteSQLEntity,
    Feature,
    StockSQLEntity,
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
    SeenOffer
)

materialized_views = (
    DiscoveryView,
    DiscoveryViewV3,
)
