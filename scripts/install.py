""" install """


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
    from models.booking import Booking

    from models.mediation import Mediation
    from models.stock import Stock
    from models.offerer import Offerer
    from models.venue_provider import VenueProvider
    from models.local_provider_event import LocalProviderEvent
    from models.local_provider import LocalProvider
    from models.offer import Offer
    from models.provider import Provider
    from models.recommendation import Recommendation

    from models.user_offerer import UserOfferer
    from models.user import User
    from models.venue import Venue

    import scripts.clean_database
    import scripts.request
    import scripts.sandbox
    import scripts.send_final_booking_recaps
    import scripts.testcafe
    import scripts.update_providables
    import scripts.storage
    import scripts.init_titelive.clean_images_in_object_storage
    import scripts.init_titelive.import_thumbs
    import scripts.init_titelive.init_titelive
    import scripts.install_data
    import scripts.migrate_images_for_event_and_thing_merge
