from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import adage_data
    from . import bookings
    from . import collective_bookings
    from . import collective_offers
    from . import collective_stocks
    from . import features
    from . import finance
    from . import offerers
    from . import offers
    from . import providers
    from . import reimbursements
    from . import signup
    from . import sirene
    from . import stocks
    from . import users
    from . import validate
    from . import venue_labels
    from . import venue_providers
    from . import venue_types
    from . import venues
