from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import

    from . import addresses
    from . import bookings
    from . import events
    from . import products
    from . import providers
    from . import venues
