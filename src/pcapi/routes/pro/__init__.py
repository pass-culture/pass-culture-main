from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import bookings
    from . import offerers
    from . import offers
    from . import providers
    from . import reimbursements
    from . import signup
    from . import stocks
    from . import user_offerers
    from . import users
    from . import validate
    from . import venue_labels
    from . import venue_providers
    from . import venue_types
    from . import venues
