def install_scripts():
    from pcapi.core.bookings import models
    from pcapi.core.offers import models
    from pcapi.local_providers.local_provider import LocalProvider
    from pcapi.models import VenueSQLEntity
    from pcapi.models.api_errors import ApiErrors
    from pcapi.models.deactivable_mixin import DeactivableMixin
    from pcapi.models.extra_data_mixin import ExtraDataMixin
    from pcapi.models.has_address_mixin import HasAddressMixin
    from pcapi.models.has_thumb_mixin import HasThumbMixin
    from pcapi.models.local_provider_event import LocalProviderEvent
    from pcapi.models.needs_validation_mixin import NeedsValidationMixin
    from pcapi.models.offerer import Offerer
    from pcapi.models.pc_object import PcObject
    from pcapi.models.providable_mixin import ProvidableMixin
    from pcapi.models.provider import Provider
    from pcapi.models.recommendation import Recommendation
    from pcapi.models.user_offerer import UserOfferer
    from pcapi.models.user_sql_entity import UserSQLEntity
    from pcapi.models.venue_provider import VenueProvider
    from pcapi.models.versioned_mixin import VersionedMixin
    import pcapi.scripts.algolia_indexing.commands
    import pcapi.scripts.clean_database
    import pcapi.scripts.install_data
    import pcapi.scripts.iris.commands
    import pcapi.scripts.payment.banishment_command
    import pcapi.scripts.payment.generate_payments
    import pcapi.scripts.sandbox
    import pcapi.scripts.storage
    import pcapi.scripts.update_providables
