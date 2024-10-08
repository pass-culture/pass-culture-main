from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import

    # Disable it for now as we change our approach on addresses for the public API
    from . import addresses
    from . import bookings
    from . import events
    from . import products
    from . import providers
