from utils.config import IS_DEV


def install_routes():
    import routes.bank_informations
    import routes.beneficiaries
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
    import routes.seen_offers
    import routes.storage
    import routes.types
    import routes.user_offerers
    import routes.users
    import routes.validate
    import routes.venue_providers
    import routes.venues
    import routes.venue_types
    import routes.venue_labels
    import routes.health_check
    import routes.mailing_contacts

    if IS_DEV:
        import routes.sandboxes
