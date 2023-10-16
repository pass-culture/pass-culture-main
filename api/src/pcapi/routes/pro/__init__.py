from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import adage_academies
    from . import adage_authentication
    from . import adage_bookings
    from . import adage_data
    from . import adage_educational_institution
    from . import adage_favorites
    from . import adage_features
    from . import adage_logs
    from . import adage_offers
    from . import adage_redactor
    from . import adage_venues
    from . import bookings
    from . import collective_bookings
    from . import collective_offers
    from . import collective_stocks
    from . import features
    from . import finance
    from . import national_programs
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
