from flask import Flask


def install_routes(app: Flask) -> None:
    from . import adage_data
    from . import bookings
    from . import collective_bookings
    from . import collective_offers
    from . import collective_stocks
    from . import features
    from . import finance
    from . import headline_offer
    from . import offerers
    from . import offers
    from . import providers
    from . import reimbursements
    from . import sirene
    from . import statistics
    from . import stocks
    from . import users
    from . import venue_labels
    from . import venue_providers
    from . import venue_types
    from . import venues
