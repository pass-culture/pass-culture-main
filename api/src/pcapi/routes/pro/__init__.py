from flask import Flask


def install_routes(app: Flask) -> None:
    from . import artists
    from . import bookings
    from . import collective_bookings
    from . import collective_offers
    from . import collective_stocks
    from . import educational_institutions
    from . import features
    from . import finance
    from . import headline_offer
    from . import highlights
    from . import offerers
    from . import offers
    from . import reimbursements
    from . import statistics
    from . import stocks
    from . import structure_data
    from . import users
    from . import venue_labels
    from . import venue_providers
    from . import venues
