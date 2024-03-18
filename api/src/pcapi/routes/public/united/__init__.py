from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import

    from .endpoints import collective_bookings
    from .endpoints import collective_offers
    from .endpoints import individual_bookings
    from .endpoints import offerers
    from .endpoints import venues
