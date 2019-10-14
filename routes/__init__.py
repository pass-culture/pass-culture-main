from utils.config import IS_DEV, IS_DATALAKE, IS_TESTING


def install_routes():
    if not IS_DATALAKE:
        import routes.bookings
        import routes.error_handlers
        import routes.export
        import routes.favorites
        import routes.features
        import routes.mediations
        import routes.music_types
        import routes.offers
        import routes.offerers
        import routes.signup
        import routes.show_types
        import routes.stocks
        import routes.passwords
        import routes.providers
        import routes.recommendations
        import routes.reimbursements
        import routes.storage
        import routes.types
        import routes.user_offerers
        import routes.users
        import routes.validate
        import routes.venue_providers
        import routes.venues
        import routes.health_check

    if IS_DATALAKE or IS_DEV or IS_TESTING:
        import routes.dashboard

    if IS_DEV:
        import routes.sandboxes
