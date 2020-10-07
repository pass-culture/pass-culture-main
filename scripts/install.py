
def install_scripts():
    from models.versioned_mixin import VersionedMixin
    from models.api_errors import ApiErrors
    from models.pc_object import PcObject
    from models.deactivable_mixin import DeactivableMixin
    from models.extra_data_mixin import ExtraDataMixin
    from models.has_address_mixin import HasAddressMixin
    from models.has_thumb_mixin import HasThumbMixin
    from models.needs_validation_mixin import NeedsValidationMixin
    from models.providable_mixin import ProvidableMixin
    from models.booking_sql_entity import BookingSQLEntity

    from models.mediation_sql_entity import MediationSQLEntity
    from models.stock_sql_entity import StockSQLEntity
    from models.offerer import Offerer
    from models.venue_provider import VenueProvider
    from models.local_provider_event import LocalProviderEvent
    from local_providers.local_provider import LocalProvider
    from models.offer_sql_entity import OfferSQLEntity
    from models.provider import Provider
    from models.recommendation import Recommendation

    from models.user_offerer import UserOfferer
    from models.user_sql_entity import UserSQLEntity
    from models import VenueSQLEntity

    import scripts.clean_database
    import scripts.sandbox
    import scripts.update_providables
    import scripts.storage
    import scripts.install_data
    import scripts.iris.commands
    import scripts.payment.banishment_command
    import scripts.payment.generate_payments
    import scripts.algolia_indexing.commands
