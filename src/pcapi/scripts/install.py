
def install_scripts():
    from pcapi.models.versioned_mixin import VersionedMixin
    from pcapi.models.api_errors import ApiErrors
    from pcapi.models.pc_object import PcObject
    from pcapi.models.deactivable_mixin import DeactivableMixin
    from pcapi.models.extra_data_mixin import ExtraDataMixin
    from pcapi.models.has_address_mixin import HasAddressMixin
    from pcapi.models.has_thumb_mixin import HasThumbMixin
    from pcapi.models.needs_validation_mixin import NeedsValidationMixin
    from pcapi.models.providable_mixin import ProvidableMixin
    from pcapi.core.bookings.models import BookingSQLEntity

    from pcapi.models.mediation_sql_entity import MediationSQLEntity
    from pcapi.models.stock_sql_entity import StockSQLEntity
    from pcapi.models.offerer import Offerer
    from pcapi.models.venue_provider import VenueProvider
    from pcapi.models.local_provider_event import LocalProviderEvent
    from pcapi.local_providers.local_provider import LocalProvider
    from pcapi.models.offer_sql_entity import OfferSQLEntity
    from pcapi.models.provider import Provider
    from pcapi.models.recommendation import Recommendation

    from pcapi.models.user_offerer import UserOfferer
    from pcapi.models.user_sql_entity import UserSQLEntity
    from pcapi.models import VenueSQLEntity

    import pcapi.scripts.clean_database
    import pcapi.scripts.sandbox
    import pcapi.scripts.update_providables
    import pcapi.scripts.storage
    import pcapi.scripts.install_data
    import pcapi.scripts.iris.commands
    import pcapi.scripts.payment.banishment_command
    import pcapi.scripts.payment.generate_payments
    import pcapi.scripts.algolia_indexing.commands
