from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import beneficiaries
    from . import bookings
    from . import favorites
    from . import mailing_contacts
    from . import music_types
    from . import recommendations
    from . import seen_offers
    from . import show_types
    from . import signup
